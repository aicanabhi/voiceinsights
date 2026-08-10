import requests



class CartesiaService:

    # Cartesia's STT returns plain text with no speaker labels, so calls
    # transcribed here have no speaker breakdown and no call metrics.
    supports_diarization = False

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

        data = {
            "model": model,
            "language": "en"
        }

        with open(file_path, "rb") as audio_file:

            response = requests.post(
                url,
                headers=headers,
                files={"file": audio_file},
                data=data
            )

        response.raise_for_status()

        result = response.json()

        return {
            "transcript": result["text"],
            "language": result.get("language", "hi"),
            "speaker_segments": []
        }