import cv2
import numpy as np


def apply_warm(frame):

    matrix = np.array([
        [0.80, 0.00, 0.00],  # Blue channel scaled down by 20%
        [0.00, 1.05, 0.00],  # Green channel scaled up by 5%
        [0.00, 0.00, 1.25]  # Red channel scaled up by 25%
    ], dtype=np.float32)

    # cv2.transform performs: P_out = Matrix * P_in
    res = cv2.transform(frame, matrix)
    return np.clip(res, 0, 255).astype(np.uint8)


def apply_cold(frame):

    matrix = np.array([
        [1.30, 0.00, 0.00],  # Blue channel scaled up by 30%
        [0.00, 1.00, 0.00],  # Green remains stable
        [0.00, 0.00, 0.75]  # Red channel scaled down by 25%
    ], dtype=np.float32)

    res = cv2.transform(frame, matrix)
    return np.clip(res, 0, 255).astype(np.uint8)


def apply_cinematic_teal_orange(frame):

    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    y, cr, cb = cv2.split(ycrcb)

    bright_mask = y > 120
    cr[bright_mask] += (y[bright_mask] - 120) * 0.25
    cb[bright_mask] -= (y[bright_mask] - 120) * 0.20

    dark_mask = y <= 120
    cr[dark_mask] -= (120 - y[dark_mask]) * 0.15
    cb[dark_mask] += (120 - y[dark_mask]) * 0.25

    cr = np.clip(cr, 0, 255)
    cb = np.clip(cb, 0, 255)

    merged = cv2.merge([y, cr, cb]).astype(np.uint8)
    return cv2.cvtColor(merged, cv2.COLOR_YCrCb2BGR)


def apply_black_and_white(frame):

    matrix = np.array([
        [0.114, 0.587, 0.299]
    ], dtype=np.float32)

    gray = cv2.transform(frame, matrix)
    gray_clipped = np.clip(gray, 0, 255).astype(np.uint8)

    return cv2.cvtColor(gray_clipped, cv2.COLOR_GRAY2BGR)