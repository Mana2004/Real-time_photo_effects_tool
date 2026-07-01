import cv2
import numpy as np
import os

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

def overlay_transparent(background, overlay, x, y, overlay_width, overlay_height):
    overlay_resized = cv2.resize(overlay, (overlay_width, overlay_height), interpolation=cv2.INTER_AREA)

    h,w = background.shape[:2]
    if x>= w or y >= h or x + overlay_width <= 0 or y + overlay_height <= 0:
        return background

