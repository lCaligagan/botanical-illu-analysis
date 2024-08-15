import os
from PIL import Image
from tqdm import tqdm

def resize_images(input_folder, output_folder, new_height, crop_height=None):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
      
    images_arr = [file for file in os.listdir(input_folder) if file.lower().endswith(".jpg")]
    
    for file in tqdm(images_arr, desc="Resizing images"):
        img_path = os.path.join(input_folder, file)
        img = Image.open(img_path)
        original_width, original_height = img.size

        if crop_height:
            if original_height > original_width:
                crop_box = (0, crop_height, original_width, original_height)
            else:
                crop_box = (crop_height, 0, original_width, original_height)
            
            img = img.crop(crop_box)
            print(f"Cropped {file} to {img.size}")
        
        ratio = img.height / img.width
        new_width = int(new_height * img.width / img.height)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        new_file = f"{os.path.splitext(file)[0]}_small.jpg"
        img.save(os.path.join(output_folder, new_file))


if __name__ == "__main__":
    input_folder = "downloads_raw"
    output_folder = "images_cropped_resized"
    height = 450
    crop_height = 210  

    resize_images(input_folder, output_folder, height, crop_height)
