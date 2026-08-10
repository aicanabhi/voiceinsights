from deepgram import DeepgramClient

from app.services.transcript_normalizer import normalize_utterances


class DeepgramService:

    supports_diarization = True

    def __init__(self, api_key:str):
        self.client = DeepgramClient(
            api_key=api_key
        )

    def transcribe(self, file_path: str, model: str, language:str):

        
        with open(file_path, "rb") as audio:
            audio_data = audio.read()

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

        speaker_segments = normalize_utterances(
            {
                "speaker": utt.speaker,
                "start": utt.start,
                "end": utt.end,
                "text": utt.transcript,
                "confidence": utt.confidence,
            }
            for utt in (response.results.utterances or [])
        )

        return {
            "transcript": transcript,
            "language": language,
            "speaker_segments": speaker_segments,
            "raw_response": response
        }