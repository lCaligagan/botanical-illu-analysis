import os
import json
import requests
import re

# Function to extract BAG_number from URL
def extract_bag_number(url):
    match = re.search(r'/MISC/(BAG_\d+)/', url)
    if match:
        return match.group(1)
    return None

# Define function to download a file from a URL
def download_file(url, destination):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        print(f"Failed to download {url}")

# Load the JSON file
with open('iiif_data.json', 'r') as file:
    data = json.load(file)

# Extract manifest URLs
manifests = data.get('manifests', [])

# Create directory for images
os.makedirs('downloads', exist_ok=True)

# Iterate over each manifest URL
for manifest in manifests:
    manifest_url = manifest.get('@id')
    if manifest_url:
        print(f"Processing manifest: {manifest_url}")
        manifest_response = requests.get(manifest_url)
        if manifest_response.status_code == 200:
            manifest_data = manifest_response.json()

            # Extract and download images
            sequences = manifest_data.get('sequences', [])
            for sequence in sequences:
                canvases = sequence.get('canvases', [])
                for canvas in canvases:
                    images = canvas.get('images', [])
                    for image in images:
                        resource = image.get('resource', {})
                        image_url = resource.get('@id')
                        if image_url:
                            bag_number = extract_bag_number(image_url)
                            if bag_number:
                                image_filename = os.path.join('downloads', f"{bag_number}.jpg")
                                print(f"Downloading image: {image_url}")
                                download_file(image_url, image_filename)
                            else:
                                print(f"Could not extract BAG_number from URL: {image_url}")
        else:
            print(f"Failed to retrieve manifest: {manifest_url}")
