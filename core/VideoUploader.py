from google.cloud import storage
from datetime import timedelta
import requests
import os
import time


class VideoUploader:
    def __init__(self,credentials_path=r"D:\python\QuantumMind\clod_credentials.json",bucket_name="luminar-img-uploader"):
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def request_url(self,file_name: str, content_type: str="video/mp4", expiration_minutes: int = 15) -> str:
            blob = self.bucket.blob(file_name)
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="PUT",
                content_type=content_type,
            )
            print(url)
            return url
        