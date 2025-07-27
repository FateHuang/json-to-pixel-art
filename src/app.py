import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import json
import os
from PIL import Image, ImageTk
# 从渲染器模块导入核心函数
from renderer import render_from_data, create_sprite_sheet
from app_state import AppState
from file_io import FileIOManager
from ui_manager import UIManager
from event_handlers import EventHandlers

# 主应用程序类
class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI 像素艺术动画生成器")
        self.root.geometry("900x600")

        # --- 路径设置 ---
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.project_root, "assets")
        self.output_dir = os.path.join(self.project_root, "output")

        # 确保assets和output文件夹存在
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # --- 模块初始化 ---
        self.state = AppState()
        self.file_io = FileIOManager(self)
        self.ui = UIManager(self)
        self.event_handlers = EventHandlers(self)

        # 初始化Tkinter变量
        self.transparent_var = tk.BooleanVar()
        self.duration_var = tk.StringVar(value='100')

        # --- 设置UI ---
        self.ui.setup_ui()

    # 渲染图像或动画的函数
    def render_image(self):
        # 如果有正在播放的动画，先取消
        if self.state.animation_job:
            self.root.after_cancel(self.state.animation_job)
            self.state.animation_job = None

        json_string = self.json_text.get("1.0", tk.END)
        if not json_string.strip():
            messagebox.showwarning("警告", "JSON输入为空。")
            return

        try:
            data = json.loads(json_string)
            use_transparency = self.transparent_var.get()

            # 从JSON数据中提取并存储关键信息
            self.state.canvas_size = tuple(data.get('canvas_size', (16, 16))) # 提供默认值以防万一
            self.state.palette = data.get('palette', {})
            
            # 根据JSON中是否存在'frames'或'pixels'来确定模式
            if 'frames' in data:
                self.state.frames_data = data.get('frames', [])
                self.state.pixels_data = None # 确保像素数据被清空
            elif 'pixels' in data:
                self.state.pixels_data = data.get('pixels', [])
                self.state.frames_data = None # 确保帧数据被清空
            else:
                self.state.frames_data = None
                self.state.pixels_data = None
            
            # 调用渲染器核心函数，获取Pillow图像列表和可能的雪碧图
            self.state.pil_images, self.state.sprite_sheet = render_from_data(data, transparent_bg=use_transparency)
            
            if not self.state.pil_images:
                messagebox.showwarning("警告", "无法从JSON渲染任何帧。")
                return

            self.state.current_frame_index = 0
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
        if not self.state.pil_images:
            return

        # 获取当前帧的Pillow图像并显示
        current_pil_image = self.state.pil_images[self.state.current_frame_index]
        self._update_display_image(current_pil_image)

        # 移动到下一帧，如果到了末尾则循环
        self.state.current_frame_index = (self.state.current_frame_index + 1) % len(self.state.pil_images)
        
        try:
            duration = int(self.duration_var.get())
        except ValueError:
            duration = 100 # 如果输入无效，则使用默认值

        # 如果有多于一帧，则安排下一帧的播放
        if len(self.state.pil_images) > 1:
            self.state.animation_job = self.root.after(duration, self.play_animation)

    def update_palette_ui(self):
        """
        根据当前加载的调色板数据更新UI。
        为每个颜色创建一个可点击的色块，并绑定选择事件。
        """
        # 清空旧的调色板按钮
        for widget in self.palette_container.winfo_children():
            widget.destroy()
        self.state.palette_buttons.clear()

        if not self.state.palette:
            return

        # 遍历调色板数据，创建色块按钮
        for color_key, hex_color in self.state.palette.items():
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
                            command=lambda ck=color_key: self.event_handlers.select_color(ck))
            btn.pack(pady=2, padx=2, fill=tk.X)
            self.state.palette_buttons[color_key] = btn
        
        # 默认选中第一个颜色（如果存在）
        if self.state.palette and not self.state.selected_color:
            first_key = list(self.state.palette.keys())[0]
            self.event_handlers.select_color(first_key)

    def update_canvas_image(self):
        """
        根据当前帧数据或单帧像素数据，重新渲染并更新画布上的图像。
        """
        if not self.state.canvas_size or (self.state.frames_data is None and self.state.pixels_data is None):
            return

        # 准备用于渲染的数据
        render_data = {
            'canvas_size': self.state.canvas_size,
            'palette': self.state.palette,
        }

        # 根据是动画还是单帧，准备不同的数据结构
        if self.state.frames_data is not None:
            # 如果是动画，我们只渲染和更新当前显示的帧
            current_frame_data = self.state.frames_data[self.state.current_frame_index]
            render_data['frames'] = [current_frame_data]
        elif self.state.pixels_data is not None:
            # 如果是单张图片
            render_data['pixels'] = self.state.pixels_data

        # 使用渲染器生成新的Pillow图像，并正确解包返回值
        pil_images, _ = render_from_data(render_data, transparent_bg=self.transparent_var.get())

        if pil_images:
            new_pil_image = pil_images[0]
            
            # 更新我们存储的Pillow图像列表
            if self.state.frames_data is not None:
                # 对于动画，替换当前帧的图像
                self.state.pil_images[self.state.current_frame_index] = new_pil_image
            else:
                # 对于单帧图像，整个列表就是这个新图像
                self.state.pil_images = [new_pil_image]

            # 使用新方法更新显示
            self._update_display_image(new_pil_image)

    def _update_json_text(self):
        """
        根据当前的应用状态，重建JSON数据并更新文本框，同时优化可读性。
        """
        if not self.state.canvas_size:
            return

        # 手动构建JSON字符串以获得更好的格式
        lines = [
            "{",
            f'    "canvas_size": {json.dumps(self.state.canvas_size)},',
            f'    "palette": {json.dumps(self.state.palette, indent=4)},'
        ]

        # 格式化 'pixels' 或 'frames' 数据
        if self.state.frames_data is not None:
            lines.append('    "frames": [')
            num_frames = len(self.state.frames_data)
            for frame_index, frame in enumerate(self.state.frames_data):
                lines.append('        [')
                num_rows = len(frame)
                for row_index, row in enumerate(frame):
                    row_str = f'            {json.dumps(row)}'
                    if row_index < num_rows - 1:
                        row_str += ','
                    lines.append(row_str)
                
                frame_end = '        ]'
                if frame_index < num_frames - 1:
                    frame_end += ','
                lines.append(frame_end)
            lines.append('    ]')

        elif self.state.pixels_data is not None:
            lines.append('    "pixels": [')
            num_rows = len(self.state.pixels_data)
            for row_index, row in enumerate(self.state.pixels_data):
                row_str = f'        {json.dumps(row)}'
                if row_index < num_rows - 1:
                    row_str += ','
                lines.append(row_str)
            lines.append('    ]')
        
        lines.append("}")
        json_string = "\n".join(lines)

        # 更新文本框内容
        self.json_text.delete('1.0', tk.END)
        self.json_text.insert(tk.END, json_string)

# 主执行块
if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()