#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from std_msgs.msg import String
import time

class ArmController(Node):
    def __init__(self, arm_id):
        super().__init__(f'arm{arm_id}_controller')
        self.arm_id = arm_id
        
        # Подписка на задания для данного манипулятора
        self.sub_task = self.create_subscription(
            Pose,
            f'/arm{arm_id}/task',
            self.task_callback,
            10
        )
        
        # Публикация статуса
        self.pub_status = self.create_publisher(
            String,
            f'/arm{arm_id}/status',
            10
        )
        
        # Параметры экстраполяции
        self.conveyor_speed = 0.1  # м/с (должно браться из параметров системы)
        self.plan_time = 0.9  # секунды (время от обнаружения до начала движения)
        
        self.get_logger().info(f'Arm{arm_id} Controller Node Started')
        self.publish_status('FREE')
    
    def publish_status(self, status):
        msg = String()
        msg.data = status
        self.pub_status.publish(msg)
    
    def move_arm(self, target_pose):
        self.get_logger().info(f'Перемещение манипулятора {self.arm_id} к точке: x={target_pose.position.x}, y={target_pose.position.y}, z={target_pose.position.z}')
        self.publish_status('BUSY')
        
        # Здесь должна быть реальная логика управления манипулятором через MoveIt2
        # Или прямое управление сервоприводами через последовательный порт
        
        # Имитация движения (задержка)
        time.sleep(1.8)  # имитация времени цикла
        
        self.publish_status('FREE')
    
    def task_callback(self, pose):
        self.get_logger().info(f'Получено задание для манипулятора {self.arm_id}')
        
        # Экстраполяция координат для учёта движения ленты
        # Координата Y (вдоль ленты) корректируется
        corrected_pose = Pose()
        corrected_pose.position.x = pose.position.x
        corrected_pose.position.y = pose.position.y + self.conveyor_speed * self.plan_time
        corrected_pose.position.z = pose.position.z
        corrected_pose.orientation = pose.orientation
        
        self.get_logger().info(f'Скорректированная Y-координата: {corrected_pose.position.y}')
        
        # Захват объекта
        self.move_arm(corrected_pose)
        
        # Имитация захвата и сброса
        self.get_logger().info(f'Захват объекта манипулятором {self.arm_id}')
        time.sleep(0.5)
        self.get_logger().info(f'Сброс объекта в бункер манипулятором {self.arm_id}')
        time.sleep(0.3)

def main(args=None):
    rclpy.init(args=args)
    
    # Можно запустить два экземпляра для левого и правого манипуляторов
    # Но обычно каждый запускается отдельным процессом
    import sys
    if len(sys.argv) > 1:
        arm_id = int(sys.argv[1])
    else:
        arm_id = 1
    
    node = ArmController(arm_id)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
