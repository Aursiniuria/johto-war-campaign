import os
from PIL import Image

def convert_and_compress_pngs(base_path, jpeg_quality=75):
    ignore_dirs = {"card_backs", "card_fronts", "moves", "color cards", "bronze", "silver", "gold", "tactics", "__pycache__"}

    for root, dirs, files in os.walk(base_path):
        # Remove ignored directories from the walk
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in files:
            if filename.lower().endswith('.png'):
                png_path = os.path.join(root, filename)
                jpeg_filename = os.path.splitext(filename)[0] + '.jpg'
                jpeg_path = os.path.join(root, jpeg_filename)

                try:
                    with Image.open(png_path) as img:
                        # Convert to RGB (JPEG does not support alpha channel)
                        rgb_img = img.convert('RGB')
                        rgb_img.save(jpeg_path, 'JPEG', quality=jpeg_quality)
                    
                    # Delete the original PNG after successful conversion
                    os.remove(png_path)
                    print(f"Converted and deleted: {png_path} → {jpeg_path}")
                except Exception as e:
                    print(f"Failed to convert {png_path}: {e}")

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    convert_and_compress_pngs(current_directory, jpeg_quality=75)
