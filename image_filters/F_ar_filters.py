import cv2
import numpy as np


cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)


def overlay_transparent(bg, overlay, x, y, overlay_w, overlay_h):
    overlay_resized = cv2.resize(overlay, (overlay_w, overlay_h), interpolation=cv2.INTER_AREA)
    h, w = bg.shape[:2]

    if x >= w or y >= h or x + overlay_w <= 0 or y + overlay_h <= 0:
        return bg

    x1, x2 = max(0, x), min(w, x + overlay_w)
    y1, y2 = max(0, y), min(h, y + overlay_h)
    ox1, ox2 = max(0, -x), overlay_w - max(0, (x + overlay_w) - w)
    oy1, oy2 = max(0, -y), overlay_h - max(0, (y + overlay_h) - h)

    sub_bg = bg[y1:y2, x1:x2].astype(np.float32)
    sub_overlay = overlay_resized[oy1:oy2, ox1:ox2].astype(np.float32)

    alpha_2d = sub_overlay[:, :, 3] / 255.0

    alpha_3d = np.expand_dims(alpha_2d, axis=2)

    # Formula: C_out = (C_overlay * Alpha) + (C_background * (1 - Alpha))
    blended = (sub_overlay[:, :, :3] * alpha_3d) + (sub_bg * (1.0 - alpha_3d))

    bg[y1:y2, x1:x2] = blended.astype(np.uint8)
    return bg


def apply_ar_prop(frame, overlay, prop_type="glasses"):
    if overlay is None:
        print("ERROR: Overlay image is None. Check your file path!")
        return frame

    if len(overlay.shape) < 3 or overlay.shape[2] < 3:
        print("ERROR: Overlay image must have color channels (BGR/BGRA).")
        return frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

    for (x, y, w, h) in faces:
        if prop_type == "glasses":
            ow, oh, ox, oy = int(w * 1.0), int(h * 0.35), x, y + int(h * 0.25)
        elif prop_type == "mustache":
            ow, oh, ox, oy = int(w * 0.55), int(h * 0.20), x + int(w * 0.22), y + int(h * 0.62)
        elif prop_type == "hat":
            ow, oh, ox, oy = int(w * 1.2), int(h * 0.6), x - int(w * 0.1), y - int(h * 0.45)
        else:
            continue

        frame = overlay_transparent(frame, overlay, ox, oy, ow, oh)

    return frame