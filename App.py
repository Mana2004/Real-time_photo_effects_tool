import tkinter as tk
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog
import os
import datetime
import  json

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
        self.window.geometry("1000x900")
        self.window.configure(bg="#2c3e50")

        self.current_filter_name = None
        self.current_filter_func = None

        self.vid = cv2.VideoCapture(0)
        self.assets_dir = "./assets"

        self.save_directory = None
        self.current_processed_frame = None

        self.config_file = "config.json"
        self.save_directory = self.load_config()

        self.setup_ui()
        self.update_frame()

    def setup_ui(self):
        self.sidebar = tk.Frame(self.window, width=280, bg="#343A40", padx=10, pady=10)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.display_panel = tk.Label(self.window, bg="#212529")
        self.display_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        title = tk.Label(self.sidebar, text="CanvasFX", font=("Helvetica", 16, "bold"), bg="#343A40", fg="#ecf0f1")
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

        settings_btn = tk.Button(self.sidebar, text="⚙️ Set Save Folder", command=self.change_save_folder,
                                 bg="#34495e", fg="white", font=("Helvetica", 10, "bold"), width=25, height=1)
        settings_btn.pack(side=tk.BOTTOM, pady=(0, 10))

        clear_btn = tk.Button(self.sidebar, text="Reset Image", command=self.clear_filter, bg="#769edb", fg="white",
                              font=("Helvetica", 10, "bold"), width=25, height=2)
        clear_btn.pack(side=tk.BOTTOM, pady=(10, 5))

        self.capture_btn = tk.Button(self.display_panel, text="Capture", command=self.capture_photo,
                                     bg="#e74c3c", fg="white", font=("Helvetica", 14, "bold"),
                                     padx=20, pady=10, relief=tk.RAISED, borderwidth=3)
        self.capture_btn.place(relx=0.5, rely=0.95, anchor=tk.S)

    def create_category_section(self, label_text, filter_list):
        lbl = tk.Label(self.sidebar, text=label_text, font=("Helvetica", 10, "bold"), bg="#343A40", fg="#F8F9FA",
                       anchor="w")
        lbl.pack(fill=tk.X, pady=(10, 2))

        for name, func in filter_list:
            btn = tk.Button(self.sidebar, text=name, command=lambda f=func, n=name: self.set_filter(n, f),
                            bg="#343A40", fg="#ecf0f1", relief=tk.FLAT, activebackground="#16a085")
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

            self.current_processed_frame = frame.copy()

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)

            self.display_panel.img_tk = img_tk
            self.display_panel.configure(image=img_tk)

        self.window.after(15, self.update_frame)

    def change_save_folder(self):
        selected_dir = filedialog.askdirectory(title="Select Folder to Save Photos")
        if selected_dir:
            self.save_directory = selected_dir
            print(f"Save directory updated to: {self.save_directory}")
            self.save_config()

    def capture_photo(self):
        if self.current_processed_frame is None:
            return

        if self.save_directory is None:
            self.change_save_folder()
            if self.save_directory is None:
                return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filter_str = self.current_filter_name.replace(" ", "_") if self.current_filter_name else "Normal"
        filename = f"CanvasFX_{filter_str}_{timestamp}.jpg"
        filepath = os.path.join(self.save_directory, filename)

        cv2.imwrite(filepath, self.current_processed_frame)
        print(f"SNAP! Saved to: {filepath}")

        self.capture_btn.configure(bg="#2ecc71", text="Saved!")
        self.window.after(1000, lambda: self.capture_btn.configure(bg="#e74c3c", text="Capture"))

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    saved_dir = config.get("save_directory")
                    if os.path.exists(saved_dir):
                        print(f"Loaded save directory from config: {saved_dir}")
                        return saved_dir
            except Exception as e:
                print(f"Error loading config file: {e}")
        return None

    def save_config(self):
        try:
            config_data = {"save_directory": self.save_directory}
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
            print("Configuration updated locally.")
        except Exception as e:
            print(f"Error saving config file: {e}")

    def __del__(self):
        if hasattr(self, 'vid') and self.vid.isOpened():
            self.vid.release()