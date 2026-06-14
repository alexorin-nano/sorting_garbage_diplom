#!/usr/bin/env python3
import cv2
import numpy as np
import yaml

def calibrate_camera():
    # Размер шахматной доски (количество внутренних углов)
    chessboard_size = (8, 6)
    square_size = 0.03  # размер клетки в метрах (30 мм)
    
    # Критерии завершения итераций калибровки
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # Подготовка точек объекта (координаты углов в реальном мире)
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    objp = objp * square_size
    
    # Массивы для хранения точек объекта и изображения
    objpoints = []  # 3D точки в реальном мире
    imgpoints = []  # 2D точки на изображении
    
    # Захват видео с камеры
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Ошибка: не удалось открыть камеру")
        return
    
    print("Нажмите 'пробел' для захвата изображения, 'q' для завершения")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Поиск углов шахматной доски
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
        
        if ret:
            cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)
            cv2.putText(frame, "Press SPACE to capture", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Calibration', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            if ret:
                # Уточнение координат углов
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                objpoints.append(objp)
                imgpoints.append(corners2)
                print(f'Захвачено {len(objpoints)} изображений')
        
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if len(objpoints) < 10:
        print(f"Недостаточно изображений для калибровки (нужно минимум 10, получено {len(objpoints)})")
        return
    
    # Калибровка камеры
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    if ret:
        print("\n=== РЕЗУЛЬТАТЫ КАЛИБРОВКИ ===")
        print(f"Матрица камеры:\n{mtx}")
        print(f"Коэффициенты дисторсии:\n{dist}")
        print(f"Ошибка перепроецирования: {ret}")
        
        # Сохранение параметров в YAML файл
        calib_data = {
            'camera_matrix': mtx.tolist(),
            'distortion_coefficients': dist.tolist(),
            'image_width': gray.shape[1],
            'image_height': gray.shape[0],
            'fx': mtx[0, 0],
            'fy': mtx[1, 1],
            'cx': mtx[0, 2],
            'cy': mtx[1, 2]
        }
        
        with open('config/camera_calibration.yaml', 'w') as f:
            yaml.dump(calib_data, f)
        print("\nПараметры сохранены в config/camera_calibration.yaml")
    else:
        print("Калибровка не удалась")

if __name__ == '__main__':
    calibrate_camera()
