from fastapi import APIRouter, UploadFile, HTTPException,File, UploadFile
from src.adapters.aws.s3_adapter import S3Adapter
from src.adapters.aws.transcribe_adapter import TranscribeAdapter,TranscribeAdapterStreaming
from src.adapters.aws.transcribe_streaming_adapter import AudioTranscriptionService
from src.services.llm.anthropic_handler import ClaudeHandler
from src.adapters.aws.polly_adapter import PollyAdapter
import time
import tempfile
import os
from typing import Dict, Optional
# from src.core.logging import logger
from io import BytesIO
router = APIRouter()

@router.post("/process-audio",tags=["Full-Audio-Processing-no-streaming"])
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

@router.post("/upload-audio",tags=["Audio"])
async def process_audio(file: UploadFile):
    try:
        # 1. Upload to S3
        s3_start_time = time.time()
        s3 = S3Adapter()
        s3_url = await s3.upload_audio(file.file, file.filename)
        s3_end_time = time.time()
        s3_time = s3_end_time - s3_start_time
        print(f"S3 upload time: {s3_time} seconds")
       
        return {
            "input_audio": s3_url,
            "time": s3_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/transcribe-audio",tags=["Transcribe"])
async def process_audio(s3_url: str):
    try:

        # 2. Transcribe audio
        transcribe_start_time = time.time()
        transcribe = TranscribeAdapter()
        text = transcribe.transcribe_audio(s3_url)
        transcribe_end_time = time.time()
        transcribe_time = transcribe_end_time - transcribe_start_time
        print(f"Transcribe time: {transcribe_time} seconds")
        print(text)
        
       
        
        return {
            "transcription": text,
            "time": transcribe_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/generate_response",tags=["LLM"])
async def process_audio(text: str):
    try:
        # Generate LLM response
        llm_start_time = time.time()
        claude = ClaudeHandler()
        response_text = claude.generate_response(text)
        llm_end_time = time.time()
        llm_time = llm_end_time - llm_start_time
        print(f"LLM time: {llm_time} seconds")
        print(response_text)
       
        
        return {
            "response_text": response_text,
            "time": llm_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/synthesize_speech",tags=["Polly"])
async def process_audio(response_text: str):
    try:
       
        
        # Convert to speech
        polly_start_time = time.time()
        polly = PollyAdapter()
        audio_url = polly.synthesize_speech(response_text)
        polly_end_time = time.time()
        polly_time = polly_end_time - polly_start_time
        print(f"Polly time: {polly_time} seconds")
        print(audio_url)
        
        return {

            "response_audio": audio_url,
            "time": polly_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/test-audio-streaming/", response_model=Dict[str, str],tags=["Audio-Streaming"])
async def transcribe_endpoint(file: UploadFile = File(...), language: str = "ar-SA"):
    """Endpoint to receive audio file and return transcript"""
    
    # Create transcription service
    transcription_service = AudioTranscriptionService()
    
    # Create temp file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_audio:
        # Write uploaded file to temp location
        content = await file.read()
        temp_audio.write(content)
        audio_path = temp_audio.name
        print(f"Audio path: {audio_path}")
    
    try:
        # Process the audio file
        transcript = await transcription_service.process_audio_file(audio_path, language)
        
        if transcript:
            return {"transcript": transcript}
        else:
            return {"error": "Failed to transcribe audio"}
    except Exception as e:
        return {"error": f"Transcription failed: {str(e)}"}
    finally:
        # Clean up temp input file
        try:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
        except:
            pass


@router.post("/process-audio/full",tags=["Full-Audio-Processing-Streaming"])
async def process_audio(file: UploadFile = File(...), language: str = "ar-SA"):
    try:
        
        
        # 1. Transcribe audio
        transcribe_start_time = time.time()
        transcription_service = AudioTranscriptionService()
        
        # Create temp file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_audio:
            # Write uploaded file to temp location
            content = await file.read()
            temp_audio.write(content)
            audio_path = temp_audio.name
            print(f"Audio path: {audio_path}")
        
        try:
            # Process the audio file
            transcript = await transcription_service.process_audio_file(audio_path, language)
            
            if not transcript:
                return {"error": "Failed to transcribe audio"}
        except Exception as e:
            return {"error": f"Transcription failed: {str(e)}"}
        finally:
            # Clean up temp input file
            try:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
            except:
                pass
        transcript_end_time = time.time()
        transcript_time = transcript_end_time - transcribe_start_time
        print(f"Transcript time: {transcript_time} seconds")

        # 2. Generate LLM response
        llm_start_time = time.time()
        claude = ClaudeHandler()
        response_text = claude.generate_response(transcript)
        llm_end_time = time.time()
        llm_time = llm_end_time - llm_start_time
        print(f"LLM time: {llm_time} seconds")
        print(response_text)
        
        # 3. Convert to speech
        polly_start_time = time.time()
        polly = PollyAdapter()
        audio_url = polly.synthesize_speech(response_text)
        polly_end_time = time.time()
        polly_time = polly_end_time - polly_start_time
        print(f"Polly time: {polly_time} seconds")
        print(audio_url)
        
        return {
            "transcription": transcript,
            "response_audio": audio_url,
            "response_text": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
