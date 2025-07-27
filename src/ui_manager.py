import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox

class UIManager:
    """
    管理所有UI元素的创建和布局。
    """
    def __init__(self, app):
        """
        初始化UIManager。

        :param app: PixelArtApp的实例，用于访问状态和事件处理器。
        """
        self.app = app
        self.root = app.root

    def setup_ui(self):
        """
        创建并布局所有UI组件。
        """
        # 创建一个可调整窗格的窗口，用于左右布局
        self.app.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.app.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- 左侧面板 (JSON 输入) ---
        left_frame = ttk.Frame(self.app.paned_window, width=400, height=580)
        self.app.paned_window.add(left_frame, weight=1)

        json_label = tk.Label(left_frame, text="在此处粘贴JSON数据:")
        json_label.pack(anchor='w', padx=5, pady=(0,5))

        self.app.json_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=50, height=30)
        self.app.json_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

        # --- 右侧主面板 ---
        right_main_frame = ttk.Frame(self.app.paned_window, width=500, height=580)
        self.app.paned_window.add(right_main_frame, weight=2)

        # --- 右侧面板 (预览和控制) ---
        right_content_frame = ttk.Frame(right_main_frame)
        right_content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=10)

        preview_label = tk.Label(right_content_frame, text="预览:")
        preview_label.pack(anchor='w')

        # 用于显示图像的容器
        image_container = tk.Frame(right_content_frame, width=258, height=258, relief=tk.SUNKEN, bg='#f0f0f0')
        image_container.pack(pady=5)
        image_container.pack_propagate(False)  # 防止容器因内容而缩放

        self.app.image_label = tk.Label(image_container, text="渲染些什么吧!", bg='#f0f0f0')
        self.app.image_label.pack(expand=True)

        # --- 事件绑定 ---
        # 注意：事件处理函数在主应用类中定义
        self.app.image_label.bind("<Button-1>", self.app.event_handlers.handle_draw)
        self.app.image_label.bind("<B1-Motion>", self.app.event_handlers.handle_draw)
        self.app.image_label.bind("<Button-3>", self.app.event_handlers.handle_erase)
        self.app.image_label.bind("<B3-Motion>", self.app.event_handlers.handle_erase)

        # 控制按钮和选项的框架
        controls_frame = tk.Frame(right_content_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # --- 调色板UI ---
        palette_frame = ttk.Frame(right_main_frame, width=100)
        palette_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        palette_label = tk.Label(palette_frame, text="调色板:")
        palette_label.pack(anchor='n', pady=(0, 5))
        
        self.app.palette_container = tk.Frame(palette_frame)
        self.app.palette_container.pack(fill=tk.BOTH, expand=True)


        self.app.transparent_check = tk.Checkbutton(controls_frame, text="透明背景", var=self.app.transparent_var)
        self.app.transparent_check.pack(anchor='w', pady=(0, 5))

        duration_frame = tk.Frame(controls_frame)
        duration_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(duration_frame, text="持续时间 (ms):").pack(side=tk.LEFT)
        self.app.duration_entry = tk.Entry(duration_frame, textvariable=self.app.duration_var, width=6)
        self.app.duration_entry.pack(side=tk.LEFT, padx=5)

        self.app.load_button = tk.Button(controls_frame, text="加载JSON文件...", command=self.app.file_io.load_json_file)
        self.app.load_button.pack(fill=tk.X, pady=(5, 5))

        self.app.render_button = tk.Button(controls_frame, text="渲染 / 播放动画", command=self.app.render_image)
        self.app.render_button.pack(fill=tk.X, pady=(0, 5))

        self.app.save_button = tk.Button(controls_frame, text="另存为...", command=self.app.file_io.save_image, state=tk.DISABLED)
        self.app.save_button.pack(fill=tk.X)