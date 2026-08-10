import base64
from deepgram import DeepgramClient
from app.core.config import settings



class DeepgramService:

    def __init__(self, api_key:str):
        self.client = DeepgramClient(
            api_key=api_key
        )

    def transcribe(self, file_path: str, model: str, language:str):

        
        with open(file_path, "rb") as audio:
            audio_data = audio.read()
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        response = self.client.listen.v1.media.transcribe_file(
            request=audio_data,
            model=model,
            smart_format=True,
            utterances=True,
            punctuate=True,
            diarize=True,
            detect_language=True,
            language=language
        )

        alternative = response.results.channels[0].alternatives[0]

        transcript = alternative.transcript
        language = response.results.channels[0].detected_language

        speaker_segments = []

        for utt in response.results.utterances:
            print(
                f"Speaker: {utt.speaker} | "
                f"Start: {utt.start} | "
                f"End: {utt.end} | "
                f"Text: {utt.transcript}"
            )

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
            "audio_base64": audio_base64,
            "raw_response": response
        }