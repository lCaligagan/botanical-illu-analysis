import os
import json
import cv2
import numpy as np
from sklearn.cluster import KMeans
import re
from tqdm import tqdm

def extract_bag_number(url):
    match = re.search(r'/MISC/(BAG_\d+)/', url)
    if match:
        return match.group(1)
    return None

def extract_main_colors(image_path, num_colors=5, sampling_rate=10):
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            return []

        cropped_image = image[300:, :]
        cv2.imwrite(image_path, cropped_image)

        image_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

        # Sample
        sampled_pixels = image_rgb[::sampling_rate, ::sampling_rate]

        # Reshape the sampled pixels to be a list of pixels
        image_flat = sampled_pixels.reshape((-1, 3))

        # Apply K-means clustering and get main colors
        if len(image_flat) < num_colors:
            num_colors = len(image_flat)

        kmeans = KMeans(n_clusters=num_colors)
        kmeans.fit(image_flat)
        main_colors = kmeans.cluster_centers_.astype(np.uint8)

        # Sort colors by decreasing frequency
        unique, counts = np.unique(kmeans.labels_, return_counts=True)
        counts = counts / np.sum(counts)  # normalize counts
        sorted_indices = np.argsort(-counts)
        main_colors = main_colors[sorted_indices]

        return main_colors
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return []

def getColorsOfImgs(images_dir, js_file_path):
    colors = []
    image_files = [f for f in os.listdir(images_dir) if f.endswith(".jpg")]

    with open(js_file_path, 'w') as js_file:
        js_file.write('const data = [\n')

        for filename in tqdm(image_files, desc="Processing images"):
            file_path = os.path.join(images_dir, filename)
            main_colors = extract_main_colors(file_path, sampling_rate=5)
            if main_colors.size > 0:  
                colors_rgb = [{"r": int(color[0]), "g": int(color[1]), "b": int(color[2])} for color in main_colors]
                colors.append({"file": filename, "colors_illu": colors_rgb})

                image_data = {
                    "name": filename,
                    "colors_illu": colors_rgb
                }
                js_file.write(json.dumps(image_data, indent=4) + ',\n')

        js_file.write('];\n')

img_dir_path = "images"
js_file_path = 'output_data.js'

getColorsOfImgs(img_dir_path, js_file_path)

print(f"Data written to {js_file_path}")
