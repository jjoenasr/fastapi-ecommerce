from supabase import create_client, Client
from fastapi import UploadFile
from uuid import uuid4
from config import settings
import os

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

# Upload to s3 bucket and return url
def upload_image(image: UploadFile, bucket_name: str = "products") -> str:
    # Get the file extension
    ext = os.path.splitext(image.filename)[1].lower()
    
    # Check if the extension is valid
    if ext not in {".jpg", ".jpeg", ".png"}:
        raise ValueError("Invalid image format. Only .jpg, .jpeg, and .png are allowed.")
    
    # Generate a unique filename
    filename = f"{uuid4().hex}{ext}"

    ## Set the file options
    mime_type = image.content_type
    
    # Upload the image to the specified bucket
    try:
        # Open the image file and upload
        file_data = image.file.read()
        response = supabase.storage.from_(bucket_name).upload(filename, file_data, file_options={'content-type': mime_type})

        # Check if the upload was successful
        if not response:
            raise Exception(f"Upload failed")
        
        return filename
    except Exception as e:
        raise Exception(f"An error occurred during the upload: {e}")

def get_supabase() -> Client:
    return supabase