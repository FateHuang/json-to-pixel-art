import tkinter as tk
from tkinter import filedialog, messagebox
import os

class FileIOManager:
    """
    管理所有文件输入/输出操作，例如加载和保存文件。
    """
    def __init__(self, app):
        """
        初始化FileIOManager。

        :param app: PixelArtApp 的实例，用于访问主应用的状态和UI组件。
        """
        self.app = app
        self.assets_dir = app.assets_dir
        self.output_dir = app.output_dir

    def load_json_file(self):
        """
        打开一个文件对话框来加载JSON文件，并将其内容放入JSON文本框中。
        """
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
            self.app.json_text.delete('1.0', tk.END)
            self.app.json_text.insert(tk.END, json_content)
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {e}")

    def save_image(self):
        """
        打开一个文件对话框，将当前渲染的图像（单帧或雪碧图）保存为PNG，
        并自动将文本框中的JSON内容保存为同名的.json文件。
        """
        if not self.app.state.pil_images:
            messagebox.showwarning("警告", "没有可保存的内容。")
            return

        # 统一保存为PNG格式
        file_types = [("PNG 图像", "*.png")]
        default_ext = ".png"

        file_path = filedialog.asksaveasfilename(
            initialdir=self.output_dir,
            defaultextension=default_ext,
            filetypes=file_types,
            title="另存为"
        )

        if not file_path:
            return

        # 从选择的路径中仅提取文件名部分
        filename_with_ext = os.path.basename(file_path)
        filename_without_ext = os.path.splitext(filename_with_ext)[0]
        
        # 定义PNG和JSON的最终保存路径
        png_path = file_path # PNG路径由用户指定
        json_path = os.path.join(self.assets_dir, f"{filename_without_ext}.json") # JSON路径固定到assets

        try:
            # --- 保存PNG图像 ---
            # 根据是否存在雪碧图来决定保存内容
            if self.app.state.sprite_sheet:
                self.app.state.sprite_sheet.save(png_path, 'PNG')
            elif self.app.state.pil_images:
                # 如果没有雪碧图，但有单帧图像
                self.app.state.pil_images[0].save(png_path, 'PNG')
            else:
                # 此情况理论上不应发生，因为保存按钮在无图时是禁用的
                messagebox.showwarning("警告", "没有图像可保存。")
                return
            
            # --- 保存JSON文件 ---
            json_content = self.app.json_text.get("1.0", tk.END)
            if json_content.strip(): # 确保有内容才保存
                with open(json_path, 'w', encoding='utf-8') as f:
                    f.write(json_content)
            
            messagebox.showinfo("成功", f"文件已成功保存:\n- 图像: {png_path}\n- 数据: {json_path}")

        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {e}")