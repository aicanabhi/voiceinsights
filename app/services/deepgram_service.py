from deepgram import DeepgramClient
from app.core.config import settings


class DeepgramService:

    def __init__(self):
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
            utterances=True,
            punctuate=True,
            diarize=True,
            detect_language=True,
        )

        alternative = response.results.channels[0].alternatives[0]

        transcript = alternative.transcript
        language = response.results.channels[0].detected_language

        speaker_segments = []

        for utt in response.results.utterances:
            speaker_segments.append({
                "speaker": utt.speaker,
                "start": utt.start,
                "end": utt.end,
                "text": utt.transcript,
                "confidence": utt.confidence
            })

        return {
            "transcript": transcript,
            "language": language,
            "speaker_segments": speaker_segments,
            "raw_response": response
        }