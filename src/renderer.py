# 导入Pillow库，用于图像处理
from PIL import Image

def hex_to_rgb(hex_color):
    """将十六进制颜色字符串转换为 (R, G, B) 元组。"""
    # 移除颜色字符串开头的 '#'
    hex_color = hex_color.lstrip('#')
    # 将十六进制字符串按每两位分割，并转换为整数，最终返回RGB元组
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_image_from_pixels(pixel_data, palette, canvas_width, canvas_height, transparent_bg=False):
    """
    从二维像素数据列表创建单个 PIL Image 对象。
    根据 transparent_bg 标志，决定如何处理值为0的像素。
    """
    # 创建一个新的 RGBA 图像，背景完全透明
    img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
    pixels = img.load()

    # 遍历画布的每个像素
    for y in range(canvas_height):
        for x in range(canvas_width):
            # 检查像素数据是否存在于当前坐标
            if y < len(pixel_data) and x < len(pixel_data[y]):
                pixel_value = pixel_data[y][x]
                
                # 如果勾选了透明背景，则跳过值为0的像素
                if transparent_bg and pixel_value == 0:
                    continue

                # 从调色板中获取颜色并绘制像素
                color_key = str(pixel_value)
                if color_key in palette:
                    color = hex_to_rgb(palette[color_key])
                    pixels[x, y] = color + (255,)
            # 如果坐标超出像素数据范围，则该像素将保持透明（或背景色）
            
    return img

def create_sprite_sheet(images):
    """
    从一个Pillow图像对象列表创建雪碧图。
    背景始终是透明的，它只负责拼接。
    """
    if not images:
        return None

    canvas_width, canvas_height = images[0].size
    total_width = canvas_width * len(images)
    
    # 创建一个完全透明的底板
    sprite_sheet = Image.new('RGBA', (total_width, canvas_height), (0, 0, 0, 0))

    # 将每一帧粘贴到底板上
    for i, img in enumerate(images):
        sprite_sheet.paste(img, (i * canvas_width, 0), img)
        
    return sprite_sheet

def render_from_data(data, transparent_bg=False):
    """
    从数据字典渲染像素艺术，处理单个图像和动画。
    """
    try:
        canvas_width, canvas_height = data['canvas_size']
    except (KeyError, ValueError):
        raise ValueError("JSON 必须包含一个 'canvas_size' 键，其值为 [宽度, 高度] 列表。")

    palette = data.get('palette', {})

    if 'frames' in data and data['frames']:
        frames_data = data['frames']
        images = [create_image_from_pixels(frame, palette, canvas_width, canvas_height, transparent_bg) for frame in frames_data]
        return images
    elif 'pixels' in data:
        pixel_data = data['pixels']
        img = create_image_from_pixels(pixel_data, palette, canvas_width, canvas_height, transparent_bg)
        return [img]
    else:
        raise ValueError("JSON 数据必须包含 'pixels' 或 'frames' 键。")


# 当该脚本作为主程序运行时
if __name__ == '__main__':
    import json
    import argparse

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='从 JSON 文件渲染像素艺术。')
    # 添加 'json_file' 参数
    parser.add_argument('json_file', type=str, help='JSON 文件的路径。')
    # 添加 'output_file' 参数
    parser.add_argument('output_file', type=str, help='输出图像文件的路径 (仅支持PNG)。')
    # 添加 '--transparent' 可选参数
    parser.add_argument('--transparent', action='store_true', help='使用透明背景。')
    
    # 解析命令行参数
    args = parser.parse_args()

    # 检查输出文件是否为PNG
    if not args.output_file.lower().endswith('.png'):
        print("错误：输出文件必须是 .png 格式。")
        exit()

    # 打开并读取JSON文件
    with open(args.json_file, 'r') as f:
        data = json.load(f)
    
    try:
        # 从数据渲染图像列表
        images = render_from_data(data, args.transparent)
        
        if not images:
            print("错误：未能从JSON数据生成任何图像。")
        elif len(images) == 1:
            # 如果只有一张图片，直接保存
            images[0].save(args.output_file, 'PNG')
            print(f"成功将单张图片渲染到 {args.output_file}")
        else:
            # 如果有多张图片（动画帧），创建并保存雪碧图
            sprite_sheet = create_sprite_sheet(images)
            if sprite_sheet:
                sprite_sheet.save(args.output_file, 'PNG')
                print(f"成功将动画雪碧图渲染到 {args.output_file}")
            else:
                print("错误：创建雪碧图失败。")

    except (ValueError, KeyError) as e:
        print(f"错误: {e}")