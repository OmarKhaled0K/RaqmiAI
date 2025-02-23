import boto3
import time
from src.core.config import settings
import requests
class TranscribeAdapter:
    def __init__(self):
        self.client = boto3.client(
            'transcribe',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def detect_language(self, text: str) -> str:
        """Simple heuristic for language detection"""
        if any('\u0600' <= char <= '\u06FF' for char in text):
            return 'ar-SA'
        return 'en-US'

    def transcribe_audio(self, media_uri: str) -> str:
        job_name = f"transcribe_{int(time.time())}"
        
        self.client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': media_uri},
            MediaFormat='wav',
            LanguageCode=settings.AWS_TRANSCRIBE_LANGUAGE,
            Settings={
                'ShowSpeakerLabels': False,
                'ChannelIdentification': False
            }
        )

        while True:
            result = self.client.get_transcription_job(TranscriptionJobName=job_name)
            status = result['TranscriptionJob']['TranscriptionJobStatus']
            if status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)

        if status == 'FAILED':
            raise Exception("Transcription failed")

        transcript_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript = requests.get(transcript_uri).json()['results']['transcripts'][0]['transcript']
        return transcript