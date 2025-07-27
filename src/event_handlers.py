import json

class EventHandlers:
    """
    处理所有用户交互事件，例如鼠标点击、拖动和UI控件的命令。
    """
    def __init__(self, app):
        """
        初始化EventHandlers。

        :param app: PixelArtApp的实例，用于访问状态、UI和核心逻辑。
        """
        self.app = app

    def handle_draw(self, event):
        """处理鼠标左键点击和拖动事件，用于绘制。"""
        if self.app.state.selected_color is None:
            return

        coords = self.screen_to_grid_coords(event.x, event.y)
        if not coords:
            return
        
        row, col = coords
        try:
            color_key = int(self.app.state.selected_color)
        except (ValueError, TypeError):
            return

        if self.app.state.pixels_data is not None:
            if 0 <= row < len(self.app.state.pixels_data) and 0 <= col < len(self.app.state.pixels_data[0]):
                self.app.state.pixels_data[row][col] = color_key
        elif self.app.state.frames_data is not None:
            current_frame_data = self.app.state.frames_data[self.app.state.current_frame_index]
            if 0 <= row < len(current_frame_data) and 0 <= col < len(current_frame_data[0]):
                current_frame_data[row][col] = color_key
        
        self.app.update_canvas_image()
        self.app._update_json_text()

    def handle_erase(self, event):
        """处理鼠标右键点击和拖动事件，用于擦除。"""
        coords = self.screen_to_grid_coords(event.x, event.y)
        if not coords:
            return
        
        row, col = coords
        erase_key = 0

        if self.app.state.pixels_data is not None:
            if 0 <= row < len(self.app.state.pixels_data) and 0 <= col < len(self.app.state.pixels_data[0]):
                self.app.state.pixels_data[row][col] = erase_key
        elif self.app.state.frames_data is not None:
            current_frame_data = self.app.state.frames_data[self.app.state.current_frame_index]
            if 0 <= row < len(current_frame_data) and 0 <= col < len(current_frame_data[0]):
                current_frame_data[row][col] = erase_key

        self.app.update_canvas_image()
        self.app._update_json_text()

    def select_color(self, color_key):
        """
        处理颜色选择事件，更新当前选中的颜色，并更新UI。
        :param color_key: 选中的颜色在调色板中的键（例如 '0', '1'）。
        """
        if self.app.state.selected_color and self.app.state.selected_color in self.app.state.palette_buttons:
            self.app.state.palette_buttons[self.app.state.selected_color].config(relief="raised", borderwidth=1)

        self.app.state.selected_color = color_key

        if color_key in self.app.state.palette_buttons:
            self.app.state.palette_buttons[color_key].config(relief="sunken", borderwidth=2)

    def handle_play_pause(self):
        """处理播放/暂停按钮的点击事件。"""
        if self.app.state.is_playing:
            self.app.pause_animation()
        else:
            self.app.play_animation()

    def handle_prev_frame(self):
        """处理“上一帧”按钮的点击事件。"""
        self.app.change_frame(-1)

    def handle_next_frame(self):
        """处理“下一帧”按钮的点击事件。"""
        self.app.change_frame(1)

    def screen_to_grid_coords(self, event_x, event_y):
        """
        将屏幕上的点击坐标转换为像素网格坐标。
        :param event_x: 鼠标事件的x坐标。
        :param event_y: 鼠标事件的y坐标。
        :return: (行, 列) 的元组，如果无法转换则返回None。
        """
        if not self.app.state.canvas_size or not hasattr(self.app.image_label, 'image'):
            return None

        displayed_image = self.app.image_label.image
        img_width, img_height = displayed_image.width(), displayed_image.height()
        
        label_width, label_height = self.app.image_label.winfo_width(), self.app.image_label.winfo_height()

        offset_x = (label_width - img_width) // 2
        offset_y = (label_height - img_height) // 2

        x_in_img = event_x - offset_x
        y_in_img = event_y - offset_y

        if not (0 <= x_in_img < img_width and 0 <= y_in_img < img_height):
            return None

        canvas_w, canvas_h = self.app.state.canvas_size
        
        pixel_width = img_width / canvas_w
        pixel_height = img_height / canvas_h

        col = int(x_in_img / pixel_width)
        row = int(y_in_img / pixel_height)

        return row, col