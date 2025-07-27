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
        self.animation_frames = []
        self.current_frame_index = 0
        self.animation_job = None  # 用于存储 `after` 方法的ID，以便取消
        self.pil_images = []  # 存储原始的Pillow图像对象，用于保存
        self.canvas_size = None      # 存储画布尺寸
        self.frames_data = None      # 存储原始帧数据
        self.palette = None          # 存储调色板

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

        # --- 右侧面板 (预览和控制) ---
        right_frame = ttk.Frame(self.paned_window, width=400, height=580)
        self.paned_window.add(right_frame, weight=2)

        right_content_frame = tk.Frame(right_frame)
        right_content_frame.pack(pady=10, padx=10)

        preview_label = tk.Label(right_content_frame, text="预览:")
        preview_label.pack(anchor='w')

        # 用于显示图像的容器
        image_container = tk.Frame(right_content_frame, width=258, height=258, relief=tk.SUNKEN, bg='#f0f0f0')
        image_container.pack(pady=5)
        image_container.pack_propagate(False)  # 防止容器因内容而缩放

        self.image_label = tk.Label(image_container, text="渲染些什么吧!", bg='#f0f0f0')
        self.image_label.pack(expand=True)

        # 控制按钮和选项的框架
        controls_frame = tk.Frame(right_content_frame)
        controls_frame.pack(fill=tk.X, pady=5)

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
            self.frames_data = data.get('frames', [])
            self.palette = data.get('palette', {})
            
            # 调用渲染器核心函数，获取Pillow图像列表
            self.pil_images = render_from_data(data, transparent_bg=use_transparency)
            if not self.pil_images:
                messagebox.showwarning("警告", "无法从JSON渲染任何帧。")
                return

            self.animation_frames = []
            preview_size = 256  # 预览区域的大小
            
            # 将Pillow图像转换为Tkinter可以显示的格式
            for pil_image in self.pil_images:
                width, height = pil_image.size
                # 计算缩放比例以适应预览区域
                scale = min(preview_size / width, preview_size / height) if width > 0 and height > 0 else 1
                new_size = (int(width * scale), int(height * scale))
                preview_image = pil_image.resize(new_size, Image.NEAREST) # 使用最近邻插值以保持像素风格
                self.animation_frames.append(ImageTk.PhotoImage(preview_image))

            self.current_frame_index = 0
            self.save_button.config(state=tk.NORMAL) # 激活保存按钮
            self.play_animation()

        except json.JSONDecodeError:
            messagebox.showerror("错误", "无效的JSON格式。")
            self.save_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("错误", f"渲染失败: {e}")
            self.save_button.config(state=tk.DISABLED)

    # 播放动画的函数
    def play_animation(self):
        if not self.animation_frames:
            return

        # 显示当前帧
        frame = self.animation_frames[self.current_frame_index]
        self.image_label.config(image=frame, text="")

        # 移动到下一帧，如果到了末尾则循环
        self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
        
        try:
            duration = int(self.duration_var.get())
        except ValueError:
            duration = 100 # 如果输入无效，则使用默认值

        # 如果有多于一帧，则安排下一帧的播放
        if len(self.animation_frames) > 1:
            self.animation_job = self.root.after(duration, self.play_animation)

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