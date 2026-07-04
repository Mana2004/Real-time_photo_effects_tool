import tkinter as tk
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog
import os
import datetime
import  json
import tkinter as tk

from MediaBridge import MediaBridge
import image_filters.A_color as color_mod
import image_filters.B_sampling as sampling_mod
import image_filters.C_color_quantization as quant_mod
import image_filters.D_stylization as style_mod
import image_filters.E_texture as texture_mod
import image_filters.F_ar_filters as ar_mod


class FilterDrawer(tk.Frame):
    def __init__(self, parent, title_text, bg_color="#343A40", fg_color="#F8F9FA"):
        super().__init__(parent, bg=bg_color)
        self.is_expanded = False
        
        self.header_text = f"▶  {title_text}"
        self.header_btn = tk.Button(
            self, text=self.header_text, font=("Helvetica", 10, "bold"), 
            bg=bg_color, fg=fg_color, anchor="w", relief=tk.FLAT,
            activebackground="#2c3e50", activeforeground=fg_color,
            bd=0, cursor="hand2"
        )
        self.header_btn.pack(fill=tk.X, pady=(5, 2))
        
        self.header_btn.config(command=self.toggle)
        
        self.content_frame = tk.Frame(self, bg=bg_color)
        
        self.raw_title = title_text

    def toggle(self):
        if self.is_expanded:
            self.content_frame.pack_forget()
            self.header_btn.config(text=f"▶  {self.raw_title}")
            self.is_expanded = False
        else:
            self.content_frame.pack(fill=tk.X, padx=10, pady=2)
            self.header_btn.config(text=f"▼  {self.raw_title}")
            self.is_expanded = True


class FXCanvas:
    def __init__(self, window, window_title, assets = None):
        self.window = window
        self.window.title(window_title)
        self.assets = assets if assets else {}
        self.window.geometry("900x600")
        self.window.configure(bg="#2c3e50")

        self.current_filter_name = None
        self.current_filter_func = None

        self.bridge = MediaBridge(source_type="webcam", path=0)
        #self.vid = cv2.VideoCapture(0)
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

        right_container = tk.Frame(self.window, bg="#212529")
        right_container.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.display_panel = tk.Label(right_container, bg="#212529")
        self.display_panel.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        #control_bar = tk.Frame(right_container, bg="#212529", height=80)
        #control_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=15)

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

        settings_btn = tk.Button(self.sidebar, text="⚙️ Set Save Folder", command=self.change_save_folder,bg="#4e6187", fg="white", 
                                font=("Helvetica", 10, "bold"), 
                                width=25, height=1, relief=tk.FLAT, cursor="hand2")
        settings_btn.pack(side=tk.BOTTOM, pady=(5, 10))

        self.capture_btn = tk.Button(self.sidebar, text="Capture", command=self.capture_photo,bg="#4e6187", fg="white", 
                                    font=("Helvetica", 10, "bold"),
                                    width=25, height=2, relief=tk.FLAT, cursor="hand2")
        self.capture_btn.pack(side=tk.BOTTOM, pady=(5, 0))

        clear_btn = tk.Button(self.sidebar, text="Reset Image", command=self.clear_filter, bg="#769edb", fg="white",
                              font=("Helvetica", 10, "bold"), 
                              width=25, height=2, relief=tk.FLAT, cursor="hand2")
        clear_btn.pack(side=tk.BOTTOM, pady=(5, 0))

        import_btn = tk.Button(self.sidebar, text="Import Photo", command=self.import_photo,bg="#769edb", fg="white", 
                               font=("Helvetica", 10, "bold"), 
                               width=25, height=2, relief=tk.FLAT, cursor="hand2")
        import_btn.pack(side=tk.BOTTOM, pady=(10, 0))


    def create_category_section(self, label_text, filter_list):
        drawer = FilterDrawer(self.sidebar, label_text, bg_color="#343A40")
        drawer.pack(fill=tk.X, pady=2)

        for name, func in filter_list:
            btn = tk.Button(
                drawer.content_frame, text=name, 
                command=lambda f=func, n=name: self.set_filter(n, f),
                bg="#343A40", fg="#ecf0f1", relief=tk.FLAT, 
                activebackground="#9f9f9f", anchor="w"
            )
            btn.pack(fill=tk.X, padx=5, pady=1)


    def set_filter(self, name, filter_func):
        self.current_filter_name = name
        self.current_filter_func = filter_func


    def clear_filter(self):
        self.current_filter_name = None
        self.current_filter_func = None


    def update_frame(self):
        frame = self.bridge.get_frame() 
        
        if frame is not None:
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


    def import_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select a Photo to Edit",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            if hasattr(self, 'bridge') and self.bridge:
                self.bridge.release()
            
            self.bridge = MediaBridge(source_type="photo", path=file_path)
            print(f"Successfully loaded static image: {file_path}")
            
            self.clear_filter()
    

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

        self.capture_btn.configure(bg="#e7e7e7", text="Saved!")
        self.window.after(1000, lambda: self.capture_btn.configure(bg="#4e6187", text="Capture"))


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
        if hasattr(self, 'bridge') and self.bridge:
            self.bridge.release()