import json
import os
from PIL import Image, ImageDraw

# Load JSON data from file
with open('annotations/instances_default.json') as f:
    data = json.load(f)

# Map category IDs to RGB colors
category_colors = {
    1: (255, 0, 0),   # Red
    2: (0, 255, 0),   # Green
    3: (0, 0, 255),   # Blue
    4: (255, 255, 0)  # Yellow
}

# Create mask image
for image in data['images']:
    image_id = image['id']
    image_path = os.path.join('images', image['file_name'])
    img = Image.new('RGB', (384, 320), color=(0, 0, 0))

    # Draw polygons for all categories in the image
    for annotation in data['annotations']:
        if annotation['image_id'] == image_id:
            category_id = annotation['category_id']
            color = category_colors.get(category_id, (255, 255, 255))
            segmentation = annotation['segmentation'][0]
            polygon = [(segmentation[i], segmentation[i+1]) for i in range(0, len(segmentation), 2)]
            draw = ImageDraw.Draw(img)
            draw.polygon(polygon, outline=color, fill=color)

    # Save mask image with original filename in a different directory
    image_name = os.path.basename(image_path)
    save_path = os.path.join('labels', image_name)
    img.save(save_path)
    print(f"Created {save_path}")