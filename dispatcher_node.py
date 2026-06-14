#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
from geometry_msgs.msg import Pose, Point
from std_msgs.msg import String

class Dispatcher(Node):
    def __init__(self):
        super().__init__('dispatcher')
        
        # Подписка на детекции
        self.sub_objects = self.create_subscription(
            Detection2DArray,
            '/detected_objects',
            self.object_callback,
            10
        )
        
        # Подписка на статусы манипуляторов
        self.sub_arm1 = self.create_subscription(
            String,
            '/arm1/status',
            self.status_callback,
            10
        )
        self.sub_arm2 = self.create_subscription(
            String,
            '/arm2/status',
            self.status_callback,
            10
        )
        
        # Публикация заданий манипуляторам
        self.pub_arm1 = self.create_publisher(
            Pose,
            '/arm1/task',
            10
        )
        self.pub_arm2 = self.create_publisher(
            Pose,
            '/arm2/task',
            10
        )
        
        # Состояния манипуляторов
        self.arm1_free = True
        self.arm2_free = True
        self.last_overlap_assign = 'right'  # для round-robin
        
        self.get_logger().info('Dispatcher Node Started')
    
    def status_callback(self, msg):
        # Обновление статусов манипуляторов
        if msg.data == 'FREE':
            if 'arm1' in msg.topic:
                self.arm1_free = True
            else:
                self.arm2_free = True
        elif msg.data == 'BUSY':
            if 'arm1' in msg.topic:
                self.arm1_free = False
            else:
                self.arm2_free = False
    
    def assign_to_arm(self, arm_id, obj):
        # Формирование задания для манипулятора
        pose = Pose()
        # Здесь нужно преобразовать координаты из obj в целевые координаты манипулятора
        # obj.bbox.center.position.x, y и т.д.
        pose.position.x = 0.0  # координата X (поперёк ленты)
        pose.position.y = 0.5  # координата Y (вдоль ленты)
        pose.position.z = 0.2  # координата Z (вертикаль)
        pose.orientation.w = 1.0
        
        if arm_id == 1:
            self.pub_arm1.publish(pose)
            self.get_logger().info(f'Назначен левому манипулятору')
        else:
            self.pub_arm2.publish(pose)
            self.get_logger().info(f'Назначен правому манипулятору')
    
    def object_callback(self, msg):
        for detection in msg.detections:
            # Получение координаты X объекта (в системе конвейера)
            # Здесь должна быть реальная координата X
            x_coord = detection.bbox.center.position.x - 320  # пример пересчёта
            
            # Левая зона (X < -50 мм)
            if x_coord < -50:
                if self.arm1_free:
                    self.assign_to_arm(1, detection)
                    self.arm1_free = False
                elif self.arm2_free:
                    self.assign_to_arm(2, detection)
                    self.arm2_free = False
            # Правая зона (X > +50 мм)
            elif x_coord > 50:
                if self.arm2_free:
                    self.assign_to_arm(2, detection)
                    self.arm2_free = False
                elif self.arm1_free:
                    self.assign_to_arm(1, detection)
                    self.arm1_free = False
            # Зона перекрытия (|X| ≤ 50 мм)
            else:
                if self.arm1_free and self.arm2_free:
                    # Алгоритм чередования (round-robin)
                    if self.last_overlap_assign == 'right':
                        self.assign_to_arm(1, detection)
                        self.arm1_free = False
                        self.last_overlap_assign = 'left'
                    else:
                        self.assign_to_arm(2, detection)
                        self.arm2_free = False
                        self.last_overlap_assign = 'right'
                elif self.arm1_free:
                    self.assign_to_arm(1, detection)
                    self.arm1_free = False
                elif self.arm2_free:
                    self.assign_to_arm(2, detection)
                    self.arm2_free = False
                else:
                    self.get_logger().warning('Оба манипулятора заняты, объект пропущен')

def main(args=None):
    rclpy.init(args=args)
    node = Dispatcher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
