#!/bin/bash
# Использование: ./run_simulation.sh

set -e 

echo "=========================================="
echo "  Запуск системы сортировки мусора"
echo "  Симуляция Gazebo + ROS2 Humble"
echo "=========================================="

source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

# 2. Запуск Gazebo с моделью конвейера и манипуляторов
echo "[1/5] Запуск Gazebo Ignition..."
gnome-terminal --tab --title="Gazebo" -- bash -c "ign gazebo -r ~/ros2_ws/src/garbage_sorting_ros2/worlds/sorting_world.sdf; exec bash"
sleep 5

echo "[2/5] Запуск камеры RealSense..."
gnome-terminal --tab --title="Camera" -- bash -c "ros2 launch realsense2_camera rs_launch.py; exec bash"
sleep 3

echo "[3/5] Запуск детектора мусора..."
gnome-terminal --tab --title="Detector" -- bash -c "ros2 run waste_detector detector_node.py; exec bash"
sleep 2

echo "[4/5] Запуск диспетчера..."
gnome-terminal --tab --title="Dispatcher" -- bash -c "ros2 run dispatcher dispatcher_node.py; exec bash"
sleep 2

echo "[5/5] Запуск контроллеров манипуляторов..."
gnome-terminal --tab --title="Arm Left" -- bash -c "ros2 run arm_controller arm_controller_node.py 1; exec bash"
gnome-terminal --tab --title="Arm Right" -- bash -c "ros2 run arm_controller arm_controller_node.py 2; exec bash"

echo "=========================================="
echo "  Система запущена!"
echo "  Для остановки закройте все терминалы"
echo "=========================================="
