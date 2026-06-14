#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
import random

class GarbageSpawner(Node):
    def __init__(self):
        super().__init__('garbage_spawner')
        self.publisher = self.create_publisher(Marker, '/garbage/spawn', 10)
        self.timer = self.create_timer(2.0, self.spawn_callback)
        
        # Классы отходов (названия для маркеров)
        self.waste_types = ['glass', 'plastic', 'metal', 'paper']
        
        self.get_logger().info('Garbage Spawner Started')
    
    def spawn_callback(self):
        # Случайный выбор типа отхода
        waste_type = random.choice(self.waste_types)
        
        # Создание маркера для визуализации в Gazebo/RViz
        marker = Marker()
        marker.header.frame_id = 'conveyor_frame'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'garbage'
        marker.id = random.randint(0, 10000)
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        
        # Случайная позиция на ленте
        marker.pose.position.x = random.uniform(-0.2, 0.2)  # поперёк ленты
        marker.pose.position.y = 1.0  # появляется в начале зоны видимости
        marker.pose.position.z = 0.05  # высота объекта
        
        # Размеры объекта
        marker.scale.x = 0.05
        marker.scale.y = 0.05
        marker.scale.z = 0.05
        
        # Цвет в зависимости от типа
        if waste_type == 'glass':
            marker.color = (0.0, 1.0, 0.0, 1.0)  # зелёный для стекла
        elif waste_type == 'plastic':
            marker.color = (0.0, 0.0, 1.0, 1.0)  # синий для пластика
        elif waste_type == 'metal':
            marker.color = (0.5, 0.5, 0.5, 1.0)  # серый для металла
        else:
            marker.color = (1.0, 1.0, 0.0, 1.0)  # жёлтый для бумаги
        
        self.publisher.publish(marker)
        self.get_logger().info(f'Сгенерирован объект: {waste_type}')

def main(args=None):
    rclpy.init(args=args)
    node = GarbageSpawner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
