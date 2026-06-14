#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, BoundingBox2D, ObjectHypothesisWithPose
from cv_bridge import CvBridge
from ultralytics import YOLO
import numpy as np

class WasteDetector(Node):
    def __init__(self):
        super().__init__('waste_detector')
        self.bridge = CvBridge()
        
        # Загрузка модели YOLO (путь к файлу весов)
        self.model = YOLO('/home/dofbot/ros2_ws/src/garbage_sorting_ros2/src/waste_detector/best.pt')
        self.get_logger().info('Модель YOLO загружена')
        
        # Подписка на топик камеры
        self.subscription = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.image_callback,
            10
        )
        
        # Публикация результатов детекции
        self.publisher = self.create_publisher(
            Detection2DArray,
            '/detected_objects',
            10
        )
        
        # Параметры калибровки камеры (будут загружены из yaml)
        self.fx = 612.3  # фокусное расстояние по X
        self.fy = 611.9  # фокусное расстояние по Y
        self.cx = 325.1  # оптический центр по X
        self.cy = 243.7  # оптический центр по Y
        
        self.get_logger().info('Waste Detector Node Started')
    
    def image_callback(self, msg):
        # Конвертация ROS Image в OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        
        # Инференс YOLO
        results = self.model(cv_image, verbose=False)
        
        # Формирование сообщения с детекциями
        detections_msg = Detection2DArray()
        detections_msg.header = msg.header
        
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    # Получение координат рамки
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Центр рамки в пикселях
                    u = (x1 + x2) / 2
                    v = (y1 + y2) / 2
                    
                    # Получение глубины (для реальной камеры нужно брать из depth топика)
                    # В данном примере используем приблизительное значение
                    Z = 800  # мм, расстояние до объекта (должно браться из карты глубины)
                    
                    # Преобразование в 3D-координаты
                    Xc = (u - self.cx) * Z / self.fx
                    Yc = (v - self.cy) * Z / self.fy
                    
                    # Создание сообщения для одного объекта
                    detection = Detection2D()
                    detection.bbox.center.position.x = float(u)
                    detection.bbox.center.position.y = float(v)
                    detection.bbox.size_x = float(x2 - x1)
                    detection.bbox.size_y = float(y2 - y1)
                    
                    hypothesis = ObjectHypothesisWithPose()
                    hypothesis.hypothesis.class_id = str(cls)
                    hypothesis.hypothesis.score = conf
                    detection.results.append(hypothesis)
                    
                    detections_msg.detections.append(detection)
                    
                    self.get_logger().debug(f'Обнаружено: класс {cls}, уверенность {conf:.2f}, координаты: X={Xc:.1f}, Y={Yc:.1f}, Z={Z:.1f}')
        
        # Публикация результата
        self.publisher.publish(detections_msg)

def main(args=None):
    rclpy.init(args=args)
    node = WasteDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
