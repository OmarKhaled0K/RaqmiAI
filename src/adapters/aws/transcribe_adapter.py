import boto3
import time
from src.core.config import settings
import requests

import asyncio
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from src.core.config import settings
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
            LanguageCode='ar-AE',
            Settings={
                'ShowSpeakerLabels': False,
                'ChannelIdentification': False,
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


from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.full_transcript = []

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            if not result.is_partial:  # Only collect final results
                for alt in result.alternatives:
                    self.full_transcript.append(alt.transcript)


import asyncio
from fastapi import UploadFile

# Audio parameters (adjust as needed)
SAMPLE_RATE = 44100  # Hz, e.g., 44.1 kHz
BYTES_PER_SAMPLE = 2  # 16-bit audio
CHANNEL_NUMS = 1  # Mono
CHUNK_SIZE = 1024 * 8  # 8 KB chunks
REGION = "us-west-2"  # AWS region

class TranscribeAdapterStreaming:
    async def transcribe_audio_streaming(self, file: UploadFile):
        # Initialize the client
        client = TranscribeStreamingClient(region=REGION)
        
        # Start the transcription stream
        stream = await client.start_stream_transcription(
            language_code="ar-AE",
            media_sample_rate_hz=SAMPLE_RATE,
            media_encoding="pcm",
        )
        print(f"stream : {stream}")
        # Instantiate the handler
        handler = MyEventHandler(stream.output_stream)
        print(f"handler : {handler}")

        async def write_chunks():
            """
            Read audio in chunks and send to the stream with delays
            to simulate real-time streaming.
            """
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                # Send the chunk to the transcription stream
                await stream.input_stream.send_audio_event(audio_chunk=chunk)
                
                # Calculate the duration of the chunk and sleep
                samples_in_chunk = len(chunk) / (BYTES_PER_SAMPLE * CHANNEL_NUMS)
                duration = samples_in_chunk / SAMPLE_RATE
                await asyncio.sleep(duration)
            
            # End the stream after all chunks are sent
            await stream.input_stream.end_stream()

        # Run writing chunks and handling events concurrently
        await asyncio.gather(write_chunks(), handler.handle_events())
        print(f"full_transcript : {handler.full_transcript}")

        # Combine the transcription segments
        full_transcript = " ".join(handler.full_transcript)
        return full_transcript