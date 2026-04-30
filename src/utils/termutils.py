import sys
import base64
import io
import math
from PIL import Image
from term_image.image import KittyImage

# ITerm2Image._supported = True
KittyImage._supported = True

def print_with_icon(b64_icon: str | None, lines: list[str], img_width: int = 15, padding: int = 2):
    if not b64_icon:
        print("      [No icon]")
        for line in lines:
            print(line)
        return

    try:
        if b64_icon.startswith("data:image/png;base64,"):
            b64_icon = b64_icon.split(",", 1)[1]
        
        image_bytes = base64.b64decode(b64_icon)
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        term_img = KittyImage(pil_img, width=img_width)
    
        img_height_rows = getattr(term_img, 'rendered_height', math.ceil(img_width / 2.0))
        
        print(term_img)
        
        # Move cursor up
        sys.stdout.write(f"\033[{img_height_rows}A")
        
        offset = img_width + padding
        
        # Print lines DOWN TO THE BOTTOM OF THE IMAGE
        # so that the cursor is at the right place
        max_lines = max(img_height_rows, len(lines))
        # TODO: See if should keep the left offset even after img is done
        for i in range(max_lines):
            text = lines[i] if i < len(lines) else ""
            
            if i < img_height_rows:
                sys.stdout.write(f"\033[{offset}C{text}\n")
            else:
                sys.stdout.write(f"{' ' * offset}{text}\n")
                
    except Exception as e:
        print(f"[Failed to load image: {e}]")
        for line in lines:
            print(line)