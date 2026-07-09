from deepgram import DeepgramClient

from app.core.config import settings


class DeepgramService:

    def __init__(self):
        # SDK reads DEEPGRAM_API_KEY automatically from environment,
        # but passing it explicitly is also supported.
        self.client = DeepgramClient(
            api_key=settings.DEEPGRAM_API_KEY
        )

    def transcribe(self, file_path: str):

        with open(file_path, "rb") as audio:
            audio_data = audio.read()

        response = self.client.listen.v1.media.transcribe_file(
            request=audio_data,
            model="nova-3",
            smart_format=True,
            punctuate=True,
            diarize=True,
            detect_language=True,
        )

        return response