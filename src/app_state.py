class AppState:
    def __init__(self):
        self.animation_job = None
        self.is_playing = False
        self.pil_images = []
        self.sprite_sheet = None # 用于存储渲染好的雪碧图
        self.current_frame_index = 0
        self.canvas_size = None
        self.frames_data = None
        self.pixels_data = None
        self.palette = None
        self.selected_color = None
        self.palette_buttons = {}