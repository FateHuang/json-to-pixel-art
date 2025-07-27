# API 文档：AI 像素艺术动画生成器

**版本：** 1.3
**日期：** 2023年10月30日

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
| `renderer.py` | [`render_from_data`](#renderer-render_from_data) | 从JSON数据渲染图像和雪碧图 | `data` (dict), `transparent_bg` (bool) | `(list[Image], Image\|None)` |
| `renderer.py` | [`create_sprite_sheet`](#renderer-create_sprite_sheet) | 从图像列表创建雪碧图 | `images` (list) | `Image` |
| `renderer.py` | [`create_image_from_pixels`](#renderer-create_image_from_pixels) | 从像素数据创建单个图像 | `pixel_data`, `palette`, `canvas_width`, `canvas_height`, `transparent_bg` | `Image` |
| `renderer.py` | [`hex_to_rgb`](#renderer-hex_to_rgb) | 将十六进制颜色转为RGB元组 | `hex_color` (str) | `tuple` |
| `file_io.py` | [`load_json_file`](#file_io-load_json_file) | 加载JSON文件到UI | - | - |
| `file_io.py` | [`save_image`](#file_io-save_image) | 保存PNG和JSON文件 | - | - |
| `app.py` | [`render_image`](#app-render_image) | 触发渲染流程并更新状态 | - | - |
| `app.py` | [`play_animation`](#app-play_animation) | 启动或恢复动画播放 | - | - |
| `app.py` | [`pause_animation`](#app-pause_animation) | 暂停动画播放 | - | - |
| `app.py` | [`change_frame`](#app-change_frame) | 手动切换当前帧 | `delta` (int) | - |
| `app.py` | [`update_animation_controls`](#app-update_animation_controls) | 更新动画控制UI的状态 | - | - |
| `app.py` | [`update_canvas_image`](#app-update_canvas_image) | 实时更新预览图像 | - | - |
| `app.py` | [`update_palette_ui`](#app-update_palette_ui) | 更新调色板UI | - | - |
| `event_handlers.py` | [`handle_play_pause`](#event_handlers-handle_play_pause) | 处理播放/暂停按钮点击 | - | - |
| `event_handlers.py` | [`handle_prev_frame`](#event_handlers-handle_prev_frame) | 处理上一帧按钮点击 | - | - |
| `event_handlers.py` | [`handle_next_frame`](#event_handlers-handle_next_frame) | 处理下一帧按钮点击 | - | - |
| `event_handlers.py` | [`handle_draw` / `handle_erase`](#event_handlers-handle_draw_handle_erase) | 处理鼠标绘制/擦除事件 | `event` | - |
| `event_handlers.py` | [`select_color`](#event_handlers-select_color) | 处理调色板颜色选择 | `color_key` (str) | - |

---

## 2. `renderer.py` - 渲染引擎API

`renderer.py` 是一个独立的模块，提供从结构化JSON数据生成像素艺术图像和动画的所有核心功能。

### <a id="renderer-render_from_data"></a>2.1. `render_from_data(data, transparent_bg=False)`

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

### <a id="renderer-create_sprite_sheet"></a>2.2. `create_sprite_sheet(images)`

此函数接收一个Pillow图像对象列表，并将它们水平拼接成一个单一的PNG雪碧图。

*   **参数：**
    *   `images` (list[Image.Image]): 一个包含动画所有帧的Pillow图像对象列表。

*   **返回值：**
    *   `Image.Image`: 一个表示最终雪碧图的Pillow `Image` 对象。

### <a id="renderer-create_image_from_pixels"></a>2.3. `create_image_from_pixels(...)`

从二维像素数据数组创建单个Pillow图像对象。

*   **参数：**
    *   `pixel_data` (list[list[int]]): 代表单个图像的二维像素数据数组。
    *   `palette` (dict): 调色板字典。
    *   `canvas_width` (int): 图像的宽度。
    *   `canvas_height` (int): 图像的高度。
    *   `transparent_bg` (bool, optional): 控制值为 `0` 的像素是否应被渲染为透明。

*   **返回值：**
    *   `Image.Image`: 一个表示所提供数据的Pillow `Image` 对象。

### <a id="renderer-hex_to_rgb"></a>2.4. `hex_to_rgb(hex_color)`

一个辅助函数，用于将十六进制颜色字符串（例如 `#RRGGBB`）转换为一个 `(R, G, B)` 整数元组。

*   **参数：**
    *   `hex_color` (str): 十六进制颜色字符串。
*   **返回值：**
    *   `tuple`: 一个包含三个整数的元组 `(R, G, B)`。

### 2.5. 命令行接口

`renderer.py` 也可以作为独立的命令行工具使用。

*   **用法：**
    ```bash
    python renderer.py <json_file> <output_file> [--transparent]
    ```

---

## 3. `app.py` - 应用主控API

`app.py` 是应用的入口，`PixelArtApp` 类是整个应用的核心，负责初始化和协调其他所有模块。

### 3.1. `PixelArtApp` 类

#### <a id="app-__init__"></a>构造函数 `__init__(self, root)`

初始化应用，包括创建窗口、设置路径、并实例化所有核心模块（`AppState`, `UIManager`, `FileIOManager`, `EventHandlers`）。它还初始化了两个 `tkinter` 变量：
*   `transparent_var` (tk.BooleanVar): 用于绑定“透明背景”复选框的状态。
*   `duration_var` (tk.StringVar): 用于绑定“持续时间”输入框的值。

#### 主要方法

*   **<a id="app-render_image"></a>`render_image(self)`**: 当用户点击“渲染/播放动画”按钮时触发。此方法负责：
    1.  如果动画正在播放，则先暂停。
    2.  从UI文本框获取JSON字符串。
    3.  解析JSON，并处理潜在的 `JSONDecodeError`。
    4.  从JSON数据中提取 `canvas_size`, `palette`, `frames_data` 或 `pixels_data` 并存入 `AppState`。
    5.  调用 `renderer.render_from_data` 生成图像。
    6.  将返回的图像和雪碧图存储在 `AppState` 中。
    7.  激活“另存为”按钮并自动开始播放动画。

*   **<a id="app-play_animation"></a>`play_animation(self)`**: 启动或恢复动画播放。它将 `AppState` 中的 `is_playing` 标志设为 `True`，更新UI按钮文本为“暂停”，然后调用 `_animation_loop` 来开始播放循环。

*   **<a id="app-pause_animation"></a>`pause_animation(self)`**: 暂停动画播放。它会取消由 `root.after()` 安排的下一个动画循环作业，并将 `is_playing` 标志设为 `False`，同时更新UI按钮文本为“播放”。

*   **<a id="app-_animation_loop"></a>`_animation_loop(self)`**: (私有方法) 动画播放的核心循环。它负责：
    1.  检查 `is_playing` 状态，如果为 `False` 则停止。
    2.  显示当前帧。
    3.  更新帧指示器标签。
    4.  递增帧索引。
    5.  使用 `root.after()` 根据 `duration_var` 的值安排下一帧的显示。

*   **<a id="app-change_frame"></a>`change_frame(self, delta)`**: 手动更改当前显示的帧。
    *   **参数**: `delta` (int) - 帧变化的量（`1` 表示下一帧，`-1` 表示上一帧）。
    *   **逻辑**: 如果动画正在播放，会先暂停。然后根据 `delta` 计算新的帧索引，并更新图像显示和UI控件。

*   **<a id="app-update_animation_controls"></a>`update_animation_controls(self)`**: 根据当前的应用状态（例如，是否存在动画帧）来更新动画控制按钮（上一帧、播放/暂停、下一帧）的启用/禁用状态，并更新帧指示器标签（例如，“1/10”）。

*   **<a id="app-update_canvas_image"></a>`update_canvas_image(self)`**: 在用户进行实时编辑（如绘制或擦除）后，重新渲染当前帧并更新预览。此方法会调用私有的 `_update_display_image` 方法来完成实际的图像显示更新。

*   **<a id="app-_update_display_image"></a>`_update_display_image(self, pil_image)`**: (私有方法) 这是一个未在API中直接暴露的辅助方法，负责将给定的Pillow图像进行缩放（使用最近邻插值以保持像素风格），并将其更新到UI的预览区域。

*   **<a id="app-update_palette_ui"></a>`update_palette_ui(self)`**: 根据 `AppState` 中当前加载的调色板数据，动态地在UI中创建或更新颜色选择按钮。

*   **<a id="app-_update_json_text"></a>`_update_json_text(self)`**: 根据 `AppState` 中的数据，重新生成格式化的JSON字符串并更新UI中的文本框。

---

## 4. `app_state.py` - 应用状态管理

此模块定义了 `AppState` 类，作为一个中央数据容器。

### 4.1. `AppState` 类

一个简单的数据类，其实例被传递给所有需要访问或修改应用状态的模块。

*   **主要属性：**
    *   `animation_job` (str | None): 存储 `tkinter` 的 `after` 方法返回的作业ID，用于取消动画。
    *   `is_playing` (bool): 一个布尔标志，用于追踪动画当前是否正在播放。
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

#### <a id="file_io-__init__"></a>构造函数 `__init__(self, app)`
初始化文件管理器。它需要一个 `PixelArtApp` 的实例，以便访问主应用的状态和UI组件。

#### <a id="file_io-load_json_file"></a>`load_json_file(self)`

打开一个文件对话框，允许用户选择一个 `.json` 文件，并将其内容加载到UI的文本框中。

#### <a id="file_io-save_image"></a>`save_image(self)`

处理保存逻辑。当用户点击“另存为...”时触发。

*   **逻辑：**
    1.  打开一个文件保存对话框，让用户选择PNG图像的保存位置和文件名（默认指向 `output/` 目录）。
    2.  根据 `AppState` 中是否存在 `sprite_sheet`，来决定是保存雪碧图还是单帧图像。
    3.  **自动地**，它会获取UI文本框中的JSON内容，并将其保存到 `assets/` 目录下。这个JSON文件的名称与用户指定的PNG文件名（不含扩展名）相同。

---

## 6. `ui_manager.py` - UI管理器API

此模块定义了 `UIManager` 类，负责所有 `tkinter` 界面元素的创建和布局。

### 6.1. `UIManager` 类

#### <a id="ui_manager-__init__"></a>构造函数 `__init__(self, app)`
初始化UI管理器。它需要一个 `PixelArtApp` 的实例，以便访问根窗口和应用状态。

#### <a id="ui_manager-setup_ui"></a>`setup_ui(self)`

这是唯一的主要方法。它构建整个应用程序的GUI，包括：
*   **主布局**: 使用 `ttk.PanedWindow` 创建一个可左右拖动的窗格。
*   **左侧面板**: 包含一个 `scrolledtext.ScrolledText` 小部件，用于显示和编辑JSON数据。
*   **右侧面板**:
    *   **预览区**: 一个带有固定大小的 `tk.Frame`，内部包含一个 `tk.Label` 用于显示渲染后的图像。
    *   **控制区**: 包含加载、渲染、保存按钮，以及“透明背景”复选框和“持续时间”输入框。
    *   **动画控制区**: 一个新的框架，包含“上一帧”、“播放/暂停”、“下一帧”按钮和一个显示当前帧号的标签。
    *   **调色板**: 一个垂直排列的框架，用于动态生成颜色选择按钮。
*   **事件绑定**: 将预览区的鼠标事件（点击和拖动）绑定到 `event_handlers` 模块中的相应处理函数。

---

## 7. `event_handlers.py` - 事件处理器API

此模块定义了 `EventHandlers` 类，用于处理所有来自用户的直接交互。

### 7.1. `EventHandlers` 类

#### <a id="event_handlers-__init__"></a>构造函数 `__init__(self, app)`
初始化事件处理器。它需要一个 `PixelArtApp` 的实例，以便访问应用的状态、UI和核心逻辑。

#### <a id="event_handlers-animation"></a>动画控制事件处理器

*   **`handle_play_pause(self)`**: 绑定到“播放/暂停”按钮。它会检查 `app.state.is_playing` 的当前值，并相应地调用 `app.play_animation()` 或 `app.pause_animation()`。
*   **`handle_prev_frame(self)`**: 绑定到“上一帧”按钮。它调用 `app.change_frame(-1)` 来切换到前一帧。
*   **`handle_next_frame(self)`**: 绑定到“下一帧”按钮。它调用 `app.change_frame(1)` 来切换到后一帧。

#### <a id="event_handlers-handle_draw_handle_erase"></a>`handle_draw(self, event)` 和 `handle_erase(self, event)`

绑定到预览图像的鼠标点击和拖动事件。它们调用 `screen_to_grid_coords` 将屏幕坐标转换为像素网格坐标，然后直接修改 `AppState` 中存储的 `pixels_data` 或 `frames_data`。最后，它们会触发 `app.update_canvas_image()` 来刷新预览，并调用 `app._update_json_text()` 来实时更新UI中的JSON显示。

#### <a id="event_handlers-select_color"></a>`select_color(self, color_key)`

当用户点击调色板中的颜色时触发。它更新 `AppState` 中的 `selected_color`，并调整UI以高亮显示选中的颜色。

#### <a id="event_handlers-screen_to_grid_coords"></a>`screen_to_grid_coords(self, event_x, event_y)`

一个辅助方法，用于精确地将鼠标在预览区域的点击位置转换为对应像素在画布网格上的 `(行, 列)` 坐标。