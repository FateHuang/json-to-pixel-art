import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import json
import os
from PIL import Image, ImageTk
# 从渲染器模块导入核心函数
from renderer import render_from_data, create_sprite_sheet

# 主应用程序类
class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI 像素艺术动画生成器")
        self.root.geometry("900x600")

        # --- 路径设置 ---
        # 获取项目根目录 (src文件夹的上级目录)
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.project_root, "assets")
        self.output_dir = os.path.join(self.project_root, "output")

        # 确保assets和output文件夹存在
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # 初始化用于存储动画帧和状态的变量
        self.animation_job = None  # 用于存储 `after` 方法的ID，以便取消
        self.pil_images = []  # 存储原始的Pillow图像对象，用于保存
        self.current_frame_index = 0
        self.canvas_size = None      # 存储画布尺寸
        self.frames_data = None      # 存储原始帧数据
        self.pixels_data = None      # 存储原始单帧数据
        self.palette = None          # 存储调色板
        self.selected_color = None   # 存储当前选中的颜色
        self.palette_buttons = {}    # 存储调色板按钮以更新UI

        # 创建Tkinter变量，用于绑定UI控件
        self.transparent_var = tk.BooleanVar()
        self.duration_var = tk.StringVar(value='100')

        # 创建一个可调整窗格的窗口，用于左右布局
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- 左侧面板 (JSON 输入) ---
        left_frame = ttk.Frame(self.paned_window, width=400, height=580)
        self.paned_window.add(left_frame, weight=1)

        json_label = tk.Label(left_frame, text="在此处粘贴JSON数据:")
        json_label.pack(anchor='w', padx=5, pady=(0,5))

        self.json_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=50, height=30)
        self.json_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

        # --- 右侧主面板 ---
        right_main_frame = ttk.Frame(self.paned_window, width=500, height=580)
        self.paned_window.add(right_main_frame, weight=2)

        # --- 右侧面板 (预览和控制) ---
        right_content_frame = ttk.Frame(right_main_frame)
        right_content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=10)

        preview_label = tk.Label(right_content_frame, text="预览:")
        preview_label.pack(anchor='w')

        # 用于显示图像的容器
        image_container = tk.Frame(right_content_frame, width=258, height=258, relief=tk.SUNKEN, bg='#f0f0f0')
        image_container.pack(pady=5)
        image_container.pack_propagate(False)  # 防止容器因内容而缩放

        self.image_label = tk.Label(image_container, text="渲染些什么吧!", bg='#f0f0f0')
        self.image_label.pack(expand=True)

        # --- 事件绑定 ---
        self.image_label.bind("<Button-1>", self.handle_draw)
        self.image_label.bind("<B1-Motion>", self.handle_draw)
        self.image_label.bind("<Button-3>", self.handle_erase)
        self.image_label.bind("<B3-Motion>", self.handle_erase)

        # 控制按钮和选项的框架
        controls_frame = tk.Frame(right_content_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # --- 调色板UI ---
        palette_frame = ttk.Frame(right_main_frame, width=100)
        palette_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        palette_label = tk.Label(palette_frame, text="调色板:")
        palette_label.pack(anchor='n', pady=(0, 5))
        
        self.palette_container = tk.Frame(palette_frame)
        self.palette_container.pack(fill=tk.BOTH, expand=True)


        self.transparent_check = tk.Checkbutton(controls_frame, text="透明背景", var=self.transparent_var)
        self.transparent_check.pack(anchor='w', pady=(0, 5))

        duration_frame = tk.Frame(controls_frame)
        duration_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(duration_frame, text="持续时间 (ms):").pack(side=tk.LEFT)
        self.duration_entry = tk.Entry(duration_frame, textvariable=self.duration_var, width=6)
        self.duration_entry.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(controls_frame, text="加载JSON文件...", command=self.load_json_file)
        self.load_button.pack(fill=tk.X, pady=(5, 5))

        self.render_button = tk.Button(controls_frame, text="渲染 / 播放动画", command=self.render_image)
        self.render_button.pack(fill=tk.X, pady=(0, 5))

        self.save_button = tk.Button(controls_frame, text="另存为...", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(fill=tk.X)

    # 从文件加载JSON数据
    def load_json_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.assets_dir,
            title="选择一个JSON文件",
            filetypes=(("JSON 文件", "*.json"), ("所有文件", "*.*"))
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_content = f.read()
            self.json_text.delete('1.0', tk.END)
            self.json_text.insert(tk.END, json_content)
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {e}")

    # 渲染图像或动画的函数
    def render_image(self):
        # 如果有正在播放的动画，先取消
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

        json_string = self.json_text.get("1.0", tk.END)
        if not json_string.strip():
            messagebox.showwarning("警告", "JSON输入为空。")
            return

        try:
            data = json.loads(json_string)
            use_transparency = self.transparent_var.get()

            # 从JSON数据中提取并存储关键信息
            self.canvas_size = tuple(data.get('canvas_size', (16, 16))) # 提供默认值以防万一
            self.palette = data.get('palette', {})
            
            # 根据JSON中是否存在'frames'或'pixels'来确定模式
            if 'frames' in data:
                self.frames_data = data.get('frames', [])
                self.pixels_data = None # 确保像素数据被清空
            elif 'pixels' in data:
                self.pixels_data = data.get('pixels', [])
                self.frames_data = None # 确保帧数据被清空
            else:
                self.frames_data = None
                self.pixels_data = None
            
            # 调用渲染器核心函数，获取Pillow图像列表
            self.pil_images = render_from_data(data, transparent_bg=use_transparency)
            if not self.pil_images:
                messagebox.showwarning("警告", "无法从JSON渲染任何帧。")
                return

            self.current_frame_index = 0
            self.save_button.config(state=tk.NORMAL) # 激活保存按钮
            self.play_animation()
            self.update_palette_ui() # 更新调色板UI

        except json.JSONDecodeError:
            messagebox.showerror("错误", "无效的JSON格式。")
            self.save_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("错误", f"渲染失败: {e}")
            self.save_button.config(state=tk.DISABLED)

    def _update_display_image(self, pil_image):
        """
        更新预览区域的图像，处理缩放和显示。
        :param pil_image: 要显示的Pillow图像对象。
        """
        preview_size = 256  # 预览区域的大小
        width, height = pil_image.size
        
        # 计算缩放比例以适应预览区域
        scale = min(preview_size / width, preview_size / height) if width > 0 and height > 0 else 1
        new_size = (int(width * scale), int(height * scale))
        
        # 使用最近邻插值以保持像素风格
        preview_image = pil_image.resize(new_size, Image.NEAREST)
        
        # 将Pillow图像转换为Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(preview_image)
        
        # 更新Label以显示新图像
        self.image_label.config(image=tk_image, text="")
        # 必须保留对PhotoImage的引用，否则它会被垃圾回收
        self.image_label.image = tk_image

    # 播放动画的函数
    def play_animation(self):
        if not self.pil_images:
            return

        # 获取当前帧的Pillow图像并显示
        current_pil_image = self.pil_images[self.current_frame_index]
        self._update_display_image(current_pil_image)

        # 移动到下一帧，如果到了末尾则循环
        self.current_frame_index = (self.current_frame_index + 1) % len(self.pil_images)
        
        try:
            duration = int(self.duration_var.get())
        except ValueError:
            duration = 100 # 如果输入无效，则使用默认值

        # 如果有多于一帧，则安排下一帧的播放
        if len(self.pil_images) > 1:
            self.animation_job = self.root.after(duration, self.play_animation)

    def update_palette_ui(self):
        """
        根据当前加载的调色板数据更新UI。
        为每个颜色创建一个可点击的色块，并绑定选择事件。
        """
        # 清空旧的调色板按钮
        for widget in self.palette_container.winfo_children():
            widget.destroy()
        self.palette_buttons.clear()

        if not self.palette:
            return

        # 遍历调色板数据，创建色块按钮
        for color_key, hex_color in self.palette.items():
            # 尝试将十六进制颜色转换为Tkinter支持的格式
            try:
                # Tkinter可以直接使用#RRGGBB格式的颜色字符串
                tk_color = hex_color
            except Exception:
                # 如果颜色格式无效，则使用默认颜色
                tk_color = "#CCCCCC" # 灰色

            btn = tk.Button(self.palette_container,
                            bg=tk_color,
                            width=2, height=1, # 小尺寸按钮
                            relief=tk.RAISED, # 凸起效果
                            borderwidth=1,
                            command=lambda ck=color_key: self.select_color(ck))
            btn.pack(pady=2, padx=2, fill=tk.X)
            self.palette_buttons[color_key] = btn
        
        # 默认选中第一个颜色（如果存在）
        if self.palette and not self.selected_color:
            first_key = list(self.palette.keys())[0]
            self.select_color(first_key)

    def select_color(self, color_key):
        """
        处理颜色选择事件，更新当前选中的颜色，并更新UI。
        :param color_key: 选中的颜色在调色板中的键（例如 '0', '1'）。
        """
        # 移除之前选中颜色的边框
        if self.selected_color and self.selected_color in self.palette_buttons:
            self.palette_buttons[self.selected_color].config(relief=tk.RAISED, borderwidth=1)

        # 设置当前选中的颜色
        self.selected_color = color_key

        # 给新选中的颜色添加边框
        if color_key in self.palette_buttons:
            self.palette_buttons[color_key].config(relief=tk.SUNKEN, borderwidth=2) # 凹陷效果，边框加粗

    def screen_to_grid_coords(self, event_x, event_y):
        """
        将屏幕上的点击坐标转换为像素网格坐标。
        :param event_x: 鼠标事件的x坐标。
        :param event_y: 鼠标事件的y坐标。
        :return: (行, 列) 的元组，如果无法转换则返回None。
        """
        # 检查是否有画布尺寸和显示的图像
        if not self.canvas_size or not hasattr(self.image_label, 'image'):
            return None

        # 获取预览图像的实际显示尺寸 (PhotoImage对象)
        displayed_image = self.image_label.image
        img_width, img_height = displayed_image.width(), displayed_image.height()
        
        # 获取Label控件的尺寸
        label_width, label_height = self.image_label.winfo_width(), self.image_label.winfo_height()

        # 计算图像在Label中的偏移量（居中显示）
        offset_x = (label_width - img_width) // 2
        offset_y = (label_height - img_height) // 2

        # 减去偏移量，得到在图像内的精确坐标
        x_in_img = event_x - offset_x
        y_in_img = event_y - offset_y

        # 检查点击是否在图像范围内
        if not (0 <= x_in_img < img_width and 0 <= y_in_img < img_height):
            return None

        # 获取原始画布尺寸
        canvas_w, canvas_h = self.canvas_size
        
        # 计算每个像素块在显示图像中的大小
        pixel_width = img_width / canvas_w
        pixel_height = img_height / canvas_h

        # 计算网格坐标
        col = int(x_in_img / pixel_width)
        row = int(y_in_img / pixel_height)

        return row, col

    def update_canvas_image(self):
        """
        根据当前帧数据或单帧像素数据，重新渲染并更新画布上的图像。
        """
        if not self.canvas_size or (self.frames_data is None and self.pixels_data is None):
            return

        # 准备用于渲染的数据
        render_data = {
            'canvas_size': self.canvas_size,
            'palette': self.palette,
        }

        # 根据是动画还是单帧，准备不同的数据结构
        if self.frames_data is not None:
            # 如果是动画，我们只渲染和更新当前显示的帧
            current_frame_data = self.frames_data[self.current_frame_index]
            render_data['frames'] = [current_frame_data]
        elif self.pixels_data is not None:
            # 如果是单张图片
            render_data['pixels'] = self.pixels_data

        # 使用渲染器生成新的Pillow图像
        pil_images = render_from_data(render_data, transparent_bg=self.transparent_var.get())

        if pil_images:
            new_pil_image = pil_images[0]
            
            # 更新我们存储的Pillow图像列表
            if self.frames_data is not None:
                # 对于动画，替换当前帧的图像
                self.pil_images[self.current_frame_index] = new_pil_image
            else:
                # 对于单帧图像，整个列表就是这个新图像
                self.pil_images = [new_pil_image]

            # 使用新方法更新显示
            self._update_display_image(new_pil_image)

    def handle_draw(self, event):
        """处理鼠标左键点击和拖动事件，用于绘制。"""
        if self.selected_color is None:
            print("Debug: No color selected.")
            return

        coords = self.screen_to_grid_coords(event.x, event.y)
        if not coords:
            print("Debug: Invalid coordinates for draw.")
            return
        
        row, col = coords
        color_key = self.selected_color

        # 根据是单帧还是动画，更新对应的数据
        if self.pixels_data is not None:
            if 0 <= row < len(self.pixels_data) and 0 <= col < len(self.pixels_data[0]):
                self.pixels_data[row][col] = color_key
        elif self.frames_data is not None:
            current_frame_data = self.frames_data[self.current_frame_index]
            if 0 <= row < len(current_frame_data) and 0 <= col < len(current_frame_data[0]):
                current_frame_data[row][col] = color_key
        
        self.update_canvas_image()


    def handle_erase(self, event):
        """处理鼠标右键点击和拖动事件，用于擦除。"""
        coords = self.screen_to_grid_coords(event.x, event.y)
        if not coords:
            print("Debug: Invalid coordinates for erase.")
            return
        
        row, col = coords
        
        # 使用背景色键（通常是'0'）进行擦除
        erase_key = '0'

        if self.pixels_data is not None:
            if 0 <= row < len(self.pixels_data) and 0 <= col < len(self.pixels_data[0]):
                self.pixels_data[row][col] = erase_key
        elif self.frames_data is not None:
            current_frame_data = self.frames_data[self.current_frame_index]
            if 0 <= row < len(current_frame_data) and 0 <= col < len(current_frame_data[0]):
                current_frame_data[row][col] = erase_key

        self.update_canvas_image()

    # 保存图像或动画的函数
    def save_image(self):
        if not self.pil_images:
            messagebox.showwarning("警告", "没有可保存的内容。")
            return

        is_animation = len(self.pil_images) > 1

        # 统一保存为PNG格式
        # 如果是动画，则为雪碧图；如果是单帧，则为普通PNG
        file_types = [("PNG 图像", "*.png")]
        default_ext = ".png"

        # 打开文件保存对话框
        file_path = filedialog.asksaveasfilename(
            initialdir=self.output_dir,  # 设置默认保存目录
            defaultextension=default_ext,
            filetypes=file_types,
            title="另存为"
        )

        if not file_path:
            return

        # 获取不带扩展名的文件名
        base_filename = os.path.basename(file_path)
        filename_without_ext = os.path.splitext(base_filename)[0]

        try:
            if is_animation:
                # 检查是否有可用于创建雪碧图的图像
                if not self.pil_images:
                    raise ValueError("没有已渲染的图像可用于创建雪碧图。")
                
                # 直接使用渲染好的图像列表创建雪碧图
                sprite_sheet = create_sprite_sheet(self.pil_images)
                
                if sprite_sheet:
                    sprite_sheet.save(file_path)
                else:
                    raise ValueError("无法创建雪碧图。")
            else:
                # 保存单张PNG图像
                self.pil_images[0].save(file_path)

            # 自动保存源JSON数据到assets目录
            json_path = os.path.join(self.assets_dir, filename_without_ext + ".json")
            with open(json_path, 'w') as f:
                f.write(self.json_text.get("1.0", tk.END))

            messagebox.showinfo("成功", f"文件保存成功!\n图像: {file_path}\nJSON: {json_path}")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

# 当该脚本作为主程序运行时
if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()