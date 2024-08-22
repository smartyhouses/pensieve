from PIL import Image
import piexif
from PIL.PngImagePlugin import PngInfo
import json
from pathlib import Path

def write_image_metadata(image_path, metadata):
    img = Image.open(image_path)
    image_path_str = str(image_path)

    if image_path_str.lower().endswith((".jpg", ".jpeg", ".tiff")):
        exif_dict = piexif.load(image_path)
        updated_description = json.dumps(metadata).encode("utf-8")
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = updated_description
        exif_bytes = piexif.dump(exif_dict)
        img.save(image_path, exif=exif_bytes)
    elif image_path_str.lower().endswith(".png"):
        metadata_info = PngInfo()
        metadata_info.add_text("Description", json.dumps(metadata))
        img.save(image_path, "PNG", pnginfo=metadata_info)
    elif image_path_str.lower().endswith(".webp"):
        img.save(image_path, "WebP", quality=85, metadata=json.dumps(metadata))
    else:
        print(f"Skipping unsupported file format: {image_path_str}")


def get_image_metadata(image_path):
    img = Image.open(image_path)
    image_path_str = str(image_path)

    if image_path_str.lower().endswith((".jpg", ".jpeg", ".tiff")):
        exif_dict = piexif.load(str(image_path))  # Convert Path object to string
        existing_description = exif_dict["0th"].get(
            piexif.ImageIFD.ImageDescription, b"{}"
        )
        try:
            return json.loads(existing_description.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
    elif image_path_str.lower().endswith(".png"):
        existing_description = img.info.get("Description", "{}")
        try:
            return json.loads(existing_description)
        except json.JSONDecodeError:
            return {}
    elif image_path_str.lower().endswith(".webp"):
        existing_metadata = img.info.get("metadata", "{}")
        try:
            return json.loads(existing_metadata)
        except json.JSONDecodeError:
            return {}
    else:
        print(f"Unsupported file format: {image_path_str}")
        return None