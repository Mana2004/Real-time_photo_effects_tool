import cv2
import numpy as np


def apply_pencil_sketch(frame, ksize=31, dynamic_range=1.8, shadow_bias=1.4):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_smoothed = cv2.bilateralFilter(gray, d=5, sigmaColor=40, sigmaSpace=40)

    laplacian_kernel = np.array([[0, -1, 0],
                                 [-1, 5, -1],
                                 [0, -1, 0]], dtype=np.float32)
    gray_sharp = cv2.filter2D(gray_smoothed.astype(np.float32), -1, laplacian_kernel)
    gray_sharp = np.clip(gray_sharp, 0, 255).astype(np.uint8)

    inverted = 255 - gray_sharp
    blurred = cv2.GaussianBlur(inverted, (ksize, ksize), 0)
    lines = cv2.divide(gray_sharp, 255 - blurred, scale=256.0)
    lines_norm = lines.astype(np.float32) / 255.0

    stroke_kernel_size = 15
    kernel = np.zeros((stroke_kernel_size, stroke_kernel_size), dtype=np.float32)
    np.fill_diagonal(kernel, 1.0)
    kernel /= stroke_kernel_size

    h, w = gray.shape
    raw_noise = np.random.normal(128, 64, (h, w)).astype(np.uint8)
    hatch_texture = cv2.filter2D(raw_noise, -1, kernel).astype(np.float32) / 255.0

    shadow_map = (255.0 - gray_sharp.astype(np.float32)) / 255.0
    shadow_map = np.power(shadow_map, shadow_bias)

    shading_layer = 1.0 - (shadow_map * (1.0 - hatch_texture) * 0.75)

    combined_sketch = lines_norm * shading_layer
    final_gray = np.clip(np.power(combined_sketch, dynamic_range) * 255.0, 0, 255).astype(np.uint8)

    return cv2.merge([final_gray, final_gray, final_gray])


def apply_watercolor(frame, passes=2, color_boost=1.2):

    blurred = frame
    for _ in range(passes):
        blurred = cv2.bilateralFilter(blurred, d=9, sigmaColor=75, sigmaSpace=75)

    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV).astype(np.float32)

    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * color_boost, 0, 255)

    vibrant = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)

    edges = 255 - gradient
    edges = cv2.GaussianBlur(edges, (5, 5), 0)

    edges_norm = edges.astype(np.float32) / 255.0

    edges_3d = cv2.merge([edges_norm, edges_norm, edges_norm])
    final_art = (vibrant.astype(np.float32) * edges_3d).astype(np.uint8)

    return final_art