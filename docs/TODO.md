# 项目任务清单 (Project Task List)

## V1.0 已完成功能 (V1.0 Completed Features)

### 核心功能：交互式像素编辑器 (Core Feature: Interactive Pixel Editor)
- **UI实现：调色板 (UI Implementation: Palette)**
    - [x] 在预览面板旁边创建了新的UI区域用于显示调色板。
    - [x] 实现了动态加载JSON中的`palette`数据并以可选色块的形式展示。
    - [x] 实现了颜色选择逻辑，记录当前用户选中的颜色。

- **预览画布：事件绑定 (Preview Canvas: Event Binding)**
    - [x] 为预览画布绑定了鼠标左键（绘制）和右键（擦除）的点击与拖动事件。
    - [x] 实现了坐标转换函数，将屏幕像素坐标精确映射到像素画网格坐标。

- **核心编辑逻辑 (Core Editing Logic)**
    - [x] 实现了左键点击绘制功能，能够根据当前选中的颜色更新内部数据。
    - [x] 实现了右键点击擦除功能，将对应数据设置为透明（`0`）。

- **数据同步 (Data Synchronization)**
    - [x] 实现了画布编辑与JSON文本框之间的实时双向数据同步。
    - [x] 优化了JSON的格式化输出，提高了可读性。

- **代码重构与稳定 (Code Refactoring & Stabilization)**
    - [x] 将应用重构为模块化架构 (`app`, `app_state`, `ui_manager`, `event_handlers`, `file_io`, `renderer`)。
    - [x] 修复了渲染逻辑、状态管理和文件保存中的多个Bug。
    - [x] 确保了应用的整体稳定性和代码质量。

- **文档 (Documentation)**
    - [x] 创建并完善了详细的 `API_Documentation_zh-CN.md`。
    - [x] 确保了代码与文档的完全同步。

---

## 未来功能规划 (Future Feature Roadmap)

### 核心功能：动画编辑控制器 (Core Feature: Animation Edit Controller)
- **UI实现：动画控制条 (UI Implementation: Animation Control Bar)**
    - [x] 在预览面板下方添加一个新的UI容器作为控制条。
    - [x] 在控制条中添加“播放/暂停”、“上一帧”、“下一帧”按钮和一个帧指示器。

- [x] **动画播放逻辑**
    - [x] 重构现有的动画播放循环，使其可以被“播放/暂停”按钮控制。
    - [x] 实现“上一帧”/“下一帧”按钮的逻辑，使其能正确更新当前显示的帧。
    - [x] 将UI状态（如当前帧号）与播放逻辑同步。

- [x] **帧编辑逻辑 (Frame Editing Logic)**
    - [x] 将画布的编辑功能与动画状态关联，确保修改只作用于当前显示的帧。
    - [x] 更新数据同步逻辑，使其能准确地修改JSON中`frames`数组里对应帧的数据。