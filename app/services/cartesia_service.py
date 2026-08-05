import requests

from app.core.config import settings


class CartesiaService:

    def __init__(self, api_key: str):
        self.api_key = api_key

    def transcribe(
        self,
        file_path: str,
        model:str
    ):

        url = "https://api.cartesia.ai/stt"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Cartesia-Version": "2026-03-01"
        }

        files = {
            "file": open(file_path, "rb")
        }

        data = {
            "model": model,
            "language": "en"
        }

        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data
        )

        print("Status Code:", response.status_code)
        print(response.text)

        response.raise_for_status()

        result = response.json()

        return {
            "transcript": result["text"],
            "language": result.get("language", "hi"),
            "speaker_segments": []
        }