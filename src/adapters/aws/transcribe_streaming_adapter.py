
import asyncio
import os
from typing import Dict, Optional
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
import aiofile
class TranscriptHandler(TranscriptResultStreamHandler):
    def __init__(self, stream):
        super().__init__(stream)
        self.full_transcript = ""
        
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        
        for result in results:
            if not result.is_partial:
                for alt in result.alternatives:
                    self.full_transcript += alt.transcript + " "
import os
import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor

class AudioTranscriptionService:
    def __init__(self, aws_region: str = "us-west-2"):
        self.aws_region = aws_region
        self._thread_pool = ThreadPoolExecutor()
        print("AudioTranscriptionService initialized...")
    
    async def convert_to_raw(self, input_file: str, output_file: str) -> bool:
        """Convert audio file to raw format required by Amazon Transcribe"""
        command = [
            "ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1", "-f", "s16le", output_file
        ]
        
        # Use run_in_executor to run subprocess.run in a thread pool
        print(f"Running ffmpeg command: {' '.join(command)}")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._thread_pool,
            lambda: subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        )
        
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr}")
            
        return result.returncode == 0
    
    async def transcribe_audio(self, raw_file_path: str, language_code: str = "ar-SA") -> str:
        """Transcribe audio file using Amazon Transcribe"""
        print(f"Creating TranscribeStreamingClient with region={self.aws_region}")
        client = TranscribeStreamingClient(region=self.aws_region)
        
        print(f"Starting stream transcription with language={language_code}")
        stream = await client.start_stream_transcription(
            language_code=language_code,
            media_sample_rate_hz=16000,
            media_encoding="pcm",
        )
        
        print("Creating transcript handler")
        handler = TranscriptHandler(stream.output_stream)
        
        async def write_chunks():
            print(f"Opening raw file for streaming: {raw_file_path}")
            async with aiofile.AIOFile(raw_file_path, 'rb') as afp:
                reader = aiofile.Reader(afp, chunk_size=1024 * 16)
                chunk_count = 0
                async for chunk in reader:
                    chunk_count += 1
                    if chunk_count % 10 == 0:
                        print(f"Sending chunk #{chunk_count} to stream")
                    await stream.input_stream.send_audio_event(audio_chunk=chunk)
                print(f"All chunks sent ({chunk_count} total). Ending stream.")
            await stream.input_stream.end_stream()
        
        print("Starting transcription process")
        await asyncio.gather(write_chunks(), handler.handle_events())
        print(f"Transcription complete. Result: '{handler.full_transcript.strip()}'")
        return handler.full_transcript.strip()
    
    async def process_audio_file(self, file_path: str, language_code: str = "ar-SA") -> Optional[str]:
        """Process an audio file and return its transcript"""
        print(f"Processing file: {file_path}...")
        # Create a temp file for the raw audio
        raw_path = file_path + ".raw"
        
        try:
            # Convert uploaded audio to the format needed by AWS Transcribe
            print("Starting conversion to raw format...")
            conversion_success = await self.convert_to_raw(file_path, raw_path)
            if not conversion_success:
                print("Conversion to raw format failed")
                return None
            
            print(f"Conversion successful. Raw file created at: {raw_path}")
            print(f"Starting transcription with language code: {language_code}")
            
            # Transcribe the audio
            transcript = await self.transcribe_audio(raw_path, language_code)
            print(f"Transcription completed successfully: '{transcript}'")
            return transcript
        except Exception as e:
            import traceback
            print(f"Transcription error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print("Traceback:")
            print(traceback.format_exc())
            return None
        finally:
            # Clean up temp raw file
            try:
                if os.path.exists(raw_path):
                    os.unlink(raw_path)
                    print(f"Cleaned up raw file: {raw_path}")
                else:
                    print(f"Raw file not found for cleanup: {raw_path}")
            except Exception as e:
                print(f"Error cleaning up: {str(e)}")