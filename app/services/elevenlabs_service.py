import requests

from app.core.config import settings


class ElevenLabsService:

    BASE_URL = "https://api.elevenlabs.io/v1/speech-to-text"

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY

    def transcribe(self, file_path: str):

        headers = {
            "xi-api-key": self.api_key
        }

        with open(file_path, "rb") as audio_file:

            files = {
                "file": audio_file
            }

            data = {
                "model_id": "scribe_v2",
                "diarize": "true"
            }

            response = requests.post(
                self.BASE_URL,
                headers=headers,
                files=files,
                data=data
            )

        if response.status_code != 200:
            raise Exception(response.text)

        result = response.json()

        speaker_segments = []

        for word in result.get("words", []):

            speaker_segments.append(
                {
                    "speaker": word.get("speaker_id"),
                    "start": word.get("start"),
                    "end": word.get("end"),
                    "text": word.get("text")
                }
            )

        return {
            "transcript": result.get("text"),
            "language": result.get("language_code"),
            "speaker_segments": speaker_segments
        }