import requests

from app.core.config import settings


class CartesiaService:

    def transcribe(
        self,
        file_path: str
    ):

        url = "https://api.cartesia.ai/stt"

        headers = {
            "Authorization": f"Bearer {settings.CARTESIA_API_KEY}",
            "Cartesia-Version": "2026-03-01"
        }

        files = {
            "file": open(file_path, "rb")
        }

        data = {
            "model": "ink-whisper",
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