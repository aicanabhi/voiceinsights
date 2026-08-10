import requests

from app.services.transcript_normalizer import words_to_utterances


class ElevenLabsService:

    BASE_URL = "https://api.elevenlabs.io/v1/speech-to-text"

    supports_diarization = True

    def __init__(self,api_key: str):
        self.api_key = api_key

    def transcribe(self, file_path: str, model: str):

        headers = {
            "xi-api-key": self.api_key
        }

        with open(file_path, "rb") as audio_file:

            files = {
                "file": audio_file
            }

            data = {
                "model_id": model,
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

        # ElevenLabs returns one entry per word; group them into utterances so
        # every provider hands back the same shape.
        speaker_segments = words_to_utterances(
            result.get("words") or []
        )

        return {
            "transcript": result.get("text"),
            "language": result.get("language_code"),
            "speaker_segments": speaker_segments
        }