# API 文档：AI 像素艺术动画生成器

**版本：** 1.0
**日期：** 2023年10月27日

## 1. 概述

本API文档旨在为“AI 像素艺术动画生成器”的开发者提供详细的技术参考。文档涵盖了项目的主要模块、核心函数、数据结构以及它们之间的交互方式。项目主要分为两个核心部分：

*   `app.py`：负责图形用户界面（GUI）、用户交互和事件处理。
*   `renderer.py`：负责解析数据、创建图像以及处理文件导出。

---

## 2. `renderer.py` - 渲染引擎API

`renderer.py` 是一个独立的模块，提供从结构化JSON数据生成像素艺术图像和动画的所有核心功能。

### 2.1. `render_from_data(data, transparent_bg=False)`

这是渲染器的主要入口函数。它解析一个包含像素数据的字典，并能处理单个图像或动画帧。它在内存中返回图像对象以供预览或进一步处理。

*   **参数：**
    *   `data` (dict): 包含所有渲染所需信息的字典，必须遵循项目定义的 [JSON 模式](PRD_zh-CN.md#51-json数据模式)。
    *   `transparent_bg` (bool, optional): 一个布尔标志，用于决定值为 `0` 的像素是否应被渲染为透明。如果为 `True`，则这些像素将是透明的；否则，它们将根据调色板中的颜色进行渲染。默认为 `False`。

*   **返回值：**
    *   `list[Image.Image]`: 一个包含一个或多个Pillow `Image` 对象的列表。对于单张图片，列表包含一个元素；对于动画，列表包含所有帧。

*   **异常：**
    *   `ValueError`: 如果 `data` 字典中缺少 `canvas_size`、`pixels` 或 `frames` 等关键键，或者格式不正确，则会引发此异常。

### 2.2. `create_sprite_sheet(images)`

此函数接收一个Pillow图像对象列表，并将它们水平拼接成一个单一的PNG雪碧图。

*   **参数：**
    *   `images` (list[Image.Image]): 一个包含动画所有帧的Pillow图像对象列表。

*   **返回值：**
    *   `Image.Image`: 一个表示最终雪碧图的Pillow `Image` 对象。该图像始终具有透明背景。

### 2.3. `create_image_from_pixels(pixel_data, palette, canvas_width, canvas_height, transparent_bg=False)`

从二维像素数据数组创建单个Pillow图像对象。该函数具有画布兼容性，如果 `pixel_data` 的尺寸与指定的画布尺寸不匹配，它会自动进行裁剪或填充。

*   **参数：**
    *   `pixel_data` (list[list[int]]): 代表单个图像的二维像素数据数组。
    *   `palette` (dict): 调色板字典。
    *   `canvas_width` (int): 图像的宽度。
    *   `canvas_height` (int): 图像的高度。
    *   `transparent_bg` (bool, optional): 控制值为 `0` 的像素是否应被渲染为透明。默认为 `False`。

*   **返回值：**
    *   `Image.Image`: 一个表示所提供数据的Pillow `Image` 对象。

### 2.4. `hex_to_rgb(hex_color)`

一个辅助函数，用于将十六进制颜色字符串（例如 `#RRGGBB`）转换为一个 `(R, G, B)` 元组。

*   **参数：**
    *   `hex_color` (str): 十六进制颜色字符串。

*   **返回值：**
    *   `tuple`: 一个包含 `(R, G, B)` 值的元组。

### 2.5. 命令行接口

`renderer.py` 也可以作为独立的命令行工具使用，用于从JSON文件直接生成PNG图像。

*   **用法：**
    ```bash
    python renderer.py <json_file> <output_file> [--transparent]
    ```
*   **参数：**
    *   `json_file` (str): 输入的JSON文件的路径。
    *   `output_file` (str): 输出的PNG文件的路径。如果JSON包含多帧，将自动生成雪碧图。
    *   `--transparent` (flag, optional): 使用此标志以启用透明背景。

---

## 3. `app.py` - GUI 应用API

`app.py` 使用 `tkinter` 构建图形界面，并利用 `renderer.py` 来执行核心的渲染任务。它管理用户输入、预览和文件保存流程。

### 3.1. `PixelArtApp` 类

这是主应用程序类，它封装了GUI的所有组件和逻辑。

#### 构造函数 `__init__(self, root)`

初始化应用程序窗口、布局和所有UI控件（如文本框、按钮、复选框等）。

*   **参数：**
    *   `root` (tk.Tk): `tkinter` 的根窗口实例。

#### 主要方法

*   **`render_image(self)`**
    *   **描述：** 当用户点击“渲染/播放动画”按钮时触发。它从JSON文本框中获取数据，调用 `renderer.render_from_data` 来生成图像，并在预览面板中显示结果。如果生成的是动画，它将启动一个循环播放。
    *   **交互：** 调用 `renderer.render_from_data`，并使用 `play_animation` 来处理动画的显示。

*   **`play_animation(self)`**
    *   **描述：** 一个递归函数，用于在预览面板中循环显示动画的每一帧。它使用 `root.after()` 来调度下一帧的显示，从而创建动画效果。
    *   **状态管理：** 管理 `self.current_frame_index` 以跟踪当前帧，并从 `self.animation_frames` 列表中获取要显示的图像。

*   **`save_image(self)`**
    *   **描述：** 当用户点击“另存为...”按钮时触发。它会打开一个文件保存对话框，让用户选择保存PNG文件的位置。
    *   **逻辑：**
        1.  检查 `self.pil_images` 中是否有可保存的图像。
        2.  如果图像是单帧，则直接保存为PNG文件。
        3.  如果图像是多帧动画，则调用 `renderer.create_sprite_sheet` 生成雪碧图，然后将其保存为PNG文件。
        4.  保存图像后，它会自动将源JSON数据保存到 `assets` 目录下，文件名与输出的图像文件相同，但扩展名为 `.json`。图像文件本身则保存在 `output` 目录下。

#### 内部状态变量

*   `self.pil_images` (list[Image.Image]): 存储由 `render_from_data` 返回的原始Pillow图像对象，用于保存。
*   `self.animation_frames` (list[ImageTk.PhotoImage]): 存储用于在 `tkinter` 中显示的 `ImageTk` 对象。
*   `self.canvas_size` (tuple): 存储从JSON加载的画布尺寸，例如 `(16, 16)`。
*   `self.frames_data` (list): 存储从JSON加载的原始帧数据。
*   `self.palette` (dict): 存储从JSON加载的调色板。