# API 文档：AI 像素艺术动画生成器

**版本：** 1.1
**日期：** 2023年10月28日

## 1. 概述

本API文档旨在为“AI 像素艺术动画生成器”的开发者提供详细的技术参考。文档涵盖了项目的主要模块、核心函数、数据结构以及它们之间的交互方式。

项目采用模块化架构，职责清晰，主要分为以下几个部分：

*   **`app.py`**: 主应用类，作为中心协调器，负责整合所有模块并驱动整个应用。
*   **`app_state.py`**: 提供一个中央状态容器 (`AppState`)，用于管理整个应用的共享数据。
*   **`ui_manager.py`**: 负责所有图形用户界面（GUI）组件的创建和布局。
*   **`event_handlers.py`**: 处理所有用户交互事件，如鼠标绘制、擦除和颜色选择。
*   **`file_io.py`**: 管理所有文件的输入/输出操作，包括加载和保存。
*   **`renderer.py`**: 作为核心渲染引擎，负责从结构化JSON数据生成像素艺术图像。

---

## 1.5 API 速查表

| 模块名 | 函数名/方法名 | 功能概述 | 主要参数 | 返回值 |
| :--- | :--- | :--- | :--- | :--- |
| `renderer.py` | `render_from_data` | 从JSON数据渲染图像和雪碧图 | `data` (dict), `transparent_bg` (bool) | `(list[Image], Image\|None)` |
| `renderer.py` | `create_sprite_sheet` | 从图像列表创建雪碧图 | `images` (list) | `Image` |
| `renderer.py` | `create_image_from_pixels` | 从像素数据创建单个图像 | `pixel_data`, `palette`, `canvas_width`, `canvas_height` | `Image` |
| `file_io.py` | `load_json_file` | 加载JSON文件到UI | - | - |
| `file_io.py` | `save_image` | 保存PNG和JSON文件 | - | - |
| `app.py` | `render_image` | 触发渲染流程并更新状态 | - | - |
| `app.py` | `play_animation` | 播放动画 | - | - |
| `app.py` | `update_canvas_image` | 实时更新预览图像 | - | - |
| `app.py` | `update_palette_ui` | 更新调色板UI | - | - |
| `event_handlers.py` | `handle_draw` / `handle_erase` | 处理鼠标绘制/擦除事件 | `event` | - |
| `event_handlers.py` | `select_color` | 处理调色板颜色选择 | `color_key` (str) | - |

---

## 2. `renderer.py` - 渲染引擎API

`renderer.py` 是一个独立的模块，提供从结构化JSON数据生成像素艺术图像和动画的所有核心功能。

### 2.1. `render_from_data(data, transparent_bg=False)`

这是渲染器的主要入口函数。它解析一个包含像素数据的字典，并能处理单个图像或动画帧。

*   **参数：**
    *   `data` (dict): 包含所有渲染所需信息的字典，必须遵循项目定义的 [JSON 模式](PRD_zh-CN.md#51-json数据模式)。
    *   `transparent_bg` (bool, optional): 一个布尔标志，用于决定值为 `0` 的像素是否应被渲染为透明。默认为 `False`。

*   **返回值：**
    *   `(list[Image.Image], Image.Image | None)`: 一个元组，包含两个元素：
        1.  一个Pillow `Image` 对象的列表，代表所有渲染出的帧。
        2.  一个Pillow `Image` 对象，代表拼接好的雪碧图。如果输入数据是单帧图像，则此值为 `None`。

*   **异常：**
    *   `ValueError`: 如果 `data` 字典中缺少 `canvas_size`、`pixels` 或 `frames` 等关键键，则会引发此异常。

### 2.2. `create_sprite_sheet(images)`

此函数接收一个Pillow图像对象列表，并将它们水平拼接成一个单一的PNG雪碧图。

*   **参数：**
    *   `images` (list[Image.Image]): 一个包含动画所有帧的Pillow图像对象列表。

*   **返回值：**
    *   `Image.Image`: 一个表示最终雪碧图的Pillow `Image` 对象。

### 2.3. `create_image_from_pixels(...)`

从二维像素数据数组创建单个Pillow图像对象。

*   **参数：**
    *   `pixel_data` (list[list[int]]): 代表单个图像的二维像素数据数组。
    *   `palette` (dict): 调色板字典。
    *   `canvas_width` (int): 图像的宽度。
    *   `canvas_height` (int): 图像的高度。
    *   `transparent_bg` (bool, optional): 控制值为 `0` 的像素是否应被渲染为透明。

*   **返回值：**
    *   `Image.Image`: 一个表示所提供数据的Pillow `Image` 对象。

### 2.4. 命令行接口

`renderer.py` 也可以作为独立的命令行工具使用。

*   **用法：**
    ```bash
    python renderer.py <json_file> <output_file> [--transparent]
    ```

---

## 3. `app.py` - 应用主控API

`app.py` 是应用的入口，`PixelArtApp` 类是整个应用的核心，负责初始化和协调其他所有模块。

### 3.1. `PixelArtApp` 类

#### 构造函数 `__init__(self, root)`

初始化应用，包括创建窗口、设置路径、并实例化所有核心模块（`AppState`, `UIManager`, `FileIOManager`, `EventHandlers`）。

#### 主要方法

*   **`render_image(self)`**: 当用户点击“渲染/播放动画”按钮时触发。它从UI获取JSON数据，调用 `renderer.render_from_data`，将返回的图像和雪碧图存储在 `AppState` 中，然后启动动画播放。
*   **`play_animation(self)`**: 一个递归函数，用于在预览面板中循环显示动画帧。它从 `AppState` 中读取图像和帧索引。
*   **`update_canvas_image(self)`**: 在用户进行实时编辑（如绘制或擦除）后，重新渲染当前帧并更新预览。
*   **`update_palette_ui(self)`**: 根据 `AppState` 中当前加载的调色板数据，动态地在UI中创建或更新颜色选择按钮。
*   **`_update_json_text(self)`**: 根据 `AppState` 中的数据，重新生成格式化的JSON字符串并更新UI中的文本框。

---

## 4. `app_state.py` - 应用状态管理

此模块定义了 `AppState` 类，作为一个中央数据容器。

### 4.1. `AppState` 类

一个简单的数据类，其实例被传递给所有需要访问或修改应用状态的模块。

*   **主要属性：**
    *   `animation_job` (str | None): 存储 `tkinter` 的 `after` 方法返回的作业ID，用于取消动画。
    *   `pil_images` (list): 存储由渲染器生成的原始Pillow图像帧。
    *   `sprite_sheet` (Image.Image | None): 存储生成的雪碧图，如果不是动画则为None。
    *   `current_frame_index` (int): 追踪当前正在显示的动画帧的索引。
    *   `canvas_size` (tuple | None): 存储画布的尺寸 `(宽度, 高度)`。
    *   `frames_data` (list | None): 存储从JSON加载的原始动画帧数据。
    *   `pixels_data` (list | None): 存储从JSON加载的原始单帧像素数据。
    *   `palette` (dict | None): 存储当前调色板。
    *   `selected_color` (str | None): 存储当前在调色板中选中的颜色键。
    *   `palette_buttons` (dict): 存储对调色板中每个颜色按钮的引用，用于更新UI状态。

---

## 5. `file_io.py` - 文件输入/输出API

此模块定义了 `FileIOManager` 类，封装了所有文件操作。

### 5.1. `FileIOManager` 类

#### `load_json_file(self)`

打开一个文件对话框，允许用户选择一个 `.json` 文件，并将其内容加载到UI的文本框中。

#### `save_image(self)`

处理保存逻辑。当用户点击“另存为...”时触发。

*   **逻辑：**
    1.  打开一个文件保存对话框，让用户选择PNG图像的保存位置和文件名（默认指向 `output/` 目录）。
    2.  根据 `AppState` 中是否存在 `sprite_sheet`，来决定是保存雪碧图还是单帧图像。
    3.  **自动地**，它会获取UI文本框中的JSON内容，并将其保存到 `assets/` 目录下。这个JSON文件的名称与用户指定的PNG文件名（不含扩展名）相同。

---

## 6. `ui_manager.py` - UI管理器API

此模块定义了 `UIManager` 类，负责所有 `tkinter` 界面元素的创建和布局。

### 6.1. `UIManager` 类

#### `setup_ui(self)`

这是唯一的主要方法。它构建整个应用程序的GUI，包括左右窗格、JSON文本输入区、图像预览区、控制按钮（加载、渲染、保存）、选项（透明背景、持续时间）以及动态生成的调色板。它还将UI事件（如按钮点击）绑定到 `app` 或 `event_handlers` 模块中的相应处理函数。

---

## 7. `event_handlers.py` - 事件处理器API

此模块定义了 `EventHandlers` 类，用于处理所有来自用户的直接交互。

### 7.1. `EventHandlers` 类

#### `handle_draw(self, event)` 和 `handle_erase(self, event)`

绑定到预览图像的鼠标点击和拖动事件。它们调用 `screen_to_grid_coords` 将屏幕坐标转换为像素网格坐标，然后直接修改 `AppState` 中存储的 `pixels_data` 或 `frames_data`，最后触发 `app.update_canvas_image()` 来刷新预览。

#### `select_color(self, color_key)`

当用户点击调色板中的颜色时触发。它更新 `AppState` 中的 `selected_color`，并调整UI以高亮显示选中的颜色。

#### `screen_to_grid_coords(self, event_x, event_y)`

一个辅助方法，用于精确地将鼠标在预览区域的点击位置转换为对应像素在画布网格上的 `(行, 列)` 坐标。