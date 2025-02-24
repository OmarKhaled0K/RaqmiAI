from fastapi import APIRouter, UploadFile, HTTPException
from src.adapters.aws.s3_adapter import S3Adapter
from src.adapters.aws.transcribe_adapter import TranscribeAdapter
from src.services.llm.anthropic_handler import ClaudeHandler
from src.adapters.aws.polly_adapter import PollyAdapter
import time
# from src.core.logging import logger

router = APIRouter()

@router.post("/process-audio")
async def process_audio(file: UploadFile):
    try:
        # 1. Upload to S3
        s3_start_time = time.time()
        s3 = S3Adapter()
        s3_url = await s3.upload_audio(file.file, file.filename)
        s3_end_time = time.time()
        s3_time = s3_end_time - s3_start_time
        print(f"S3 upload time: {s3_time} seconds")
        print(s3_url)
        
        # 2. Transcribe audio
        transcribe_start_time = time.time()
        transcribe = TranscribeAdapter()
        text = transcribe.transcribe_audio(s3_url)
        transcribe_end_time = time.time()
        transcribe_time = transcribe_end_time - transcribe_start_time
        print(f"Transcribe time: {transcribe_time} seconds")
        print(text)
        
        # 3. Generate LLM response
        llm_start_time = time.time()
        claude = ClaudeHandler()
        response_text = claude.generate_response(text)
        llm_end_time = time.time()
        llm_time = llm_end_time - llm_start_time
        print(f"LLM time: {llm_time} seconds")
        print(response_text)
        
        # 4. Convert to speech
        polly_start_time = time.time()
        polly = PollyAdapter()
        audio_url = polly.synthesize_speech(response_text)
        polly_end_time = time.time()
        polly_time = polly_end_time - polly_start_time
        print(f"Polly time: {polly_time} seconds")
        print(audio_url)
        
        return {
            "input_audio": s3_url,
            "transcription": text,
            "response_audio": audio_url,
            "response_text": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))