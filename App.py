import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os

import image_filters.A_color as color_mod
import image_filters.B_sampling as sampling_mod
import image_filters.C_color_quantization as quant_mod
import image_filters.D_stylization as style_mod
import image_filters.E_texture as texture_mod
import image_filters.F_ar_filters as ar_mod


class FXCanvas:
    def __init__(self, window, window_title, assets = None):
        self.window = window
        self.window.title(window_title)
        self.assets = assets if assets else {}
        self.window.geometry("1100x700")
        self.window.configure(bg="#2c3e50")

        self.current_filter_name = None
        self.current_filter_func = None

        self.vid = cv2.VideoCapture(0)
        self.assets_dir = "./assets"

        self.setup_ui()
        self.update_frame()

    def setup_ui(self):
        self.sidebar = tk.Frame(self.window, width=280, bg="#34495e", padx=10, pady=10)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.display_panel = tk.Label(self.window, bg="#2c3e50")
        self.display_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        title = tk.Label(self.sidebar, text="IMAGE FILTERS", font=("Helvetica", 16, "bold"), bg="#34495e", fg="#ecf0f1")
        title.pack(pady=10)

        self.create_category_section("Color Transformations", [
            ("Warm", lambda f: color_mod.apply_warm(f)),
            ("Cold", lambda f: color_mod.apply_cold(f)),
            ("Teal & Orange", lambda f: color_mod.apply_cinematic_teal_orange(f)),
            ("Black & White", lambda f: color_mod.apply_black_and_white(f))
        ])

        self.create_category_section("Sampling & Quantization", [
            ("Pixel Art", lambda f: sampling_mod.apply_pixel_art(f)),
            ("Halftone Dots", lambda f: sampling_mod.apply_halftone(f)),
            ("Pop Art", lambda f: quant_mod.apply_pop_art(f)),
            ("Posterize", lambda f: quant_mod.apply_posterize(f))
        ])

        self.create_category_section("Image Stylization", [
            ("Watercolor", lambda f: style_mod.apply_watercolor(f)),
            ("Pencil Sketch", lambda f: style_mod.apply_pencil_sketch(f))
        ])

        self.create_category_section("Texture Synthesis", [
            ("Film Grain", lambda f: texture_mod.apply_grain(f)),
            ("Retro VHS", lambda f: texture_mod.apply_vhs_retro(f))
        ])

        self.create_category_section("Face-aware AR", [
            ("AR Hat", lambda f: ar_mod.apply_ar_prop(f, self.assets.get("hat"), "hat")),
            ("AR Mustache", lambda f: ar_mod.apply_ar_prop(f, self.assets.get("mustache"), "mustache")),
            ("AR Glasses", lambda f: ar_mod.apply_ar_prop(f, self.assets.get("glasses"), "glasses")),
            ("AR Butterfly", lambda f: ar_mod.apply_ar_prop(f, self.assets.get("butterfly"), "butterfly"))
        ])

        clear_btn = tk.Button(self.sidebar, text="Reset Image", command=self.clear_filter, bg="#e74c3c", fg="white",
                              font=("Helvetica", 10, "bold"), width=25, height=2)
        clear_btn.pack(side=tk.BOTTOM, pady=10)

    def create_category_section(self, label_text, filter_list):
        lbl = tk.Label(self.sidebar, text=label_text, font=("Helvetica", 10, "bold"), bg="#34495e", fg="#1abc9c",
                       anchor="w")
        lbl.pack(fill=tk.X, pady=(10, 2))

        for name, func in filter_list:
            btn = tk.Button(self.sidebar, text=name, command=lambda f=func, n=name: self.set_filter(n, f),
                            bg="#2c3e50", fg="#ecf0f1", relief=tk.FLAT, activebackground="#16a085")
            btn.pack(fill=tk.X, padx=10, pady=1)

    def set_filter(self, name, filter_func):
        self.current_filter_name = name
        self.current_filter_func = filter_func

    def clear_filter(self):
        self.current_filter_name = None
        self.current_filter_func = None

    def update_frame(self):
        ret, frame = self.vid.read()
        if ret:
            if self.current_filter_name and self.current_filter_func:
                try:
                    frame = self.current_filter_func(frame)
                except Exception as e:
                    print(f"Error in {self.current_filter_name}: {e}")

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)

            self.display_panel.img_tk = img_tk
            self.display_panel.configure(image=img_tk)

        self.window.after(15, self.update_frame)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()