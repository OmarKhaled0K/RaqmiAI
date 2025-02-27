from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from src.adapters.aws.s3_adapter import S3Adapter
from src.adapters.aws.transcribe_adapter import TranscribeAdapter
from src.adapters.aws.transcribe_streaming_adapter import AudioTranscriptionService
from src.services.llm.anthropic_handler import ClaudeHandler
from src.adapters.aws.polly_adapter import PollyAdapter
import time
import tempfile
import os
from typing import Dict, Optional
from pydantic import BaseModel

# Create router with a meaningful prefix
router = APIRouter(prefix="/audio-processing", tags=["Audio Processing"])

# Define request and response models
class TranscriptionRequest(BaseModel):
    s3_url: str

class TextProcessingRequest(BaseModel):
    text: str

class AudioProcessingResponse(BaseModel):
    input_audio: Optional[str] = None
    transcription: Optional[str] = None
    response_text: Optional[str] = None
    response_audio: Optional[str] = None
    processing_time: Dict[str, float]
    total_time: float

# Helper functions
async def create_temp_audio_file(file: UploadFile) -> str:
    """Create a temporary file from the uploaded audio file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_audio:
        content = await file.read()
        temp_audio.write(content)
        return temp_audio.name

def clean_temp_file(file_path: str) -> None:
    """Clean up temporary file."""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Warning: Failed to delete temporary file {file_path}: {str(e)}")


# API Endpoints
@router.post("/complete", response_model=AudioProcessingResponse, 
             summary="Process audio through the complete pipeline")
async def process_audio_complete(file: UploadFile = File(...)):
    """
    Process audio through the complete pipeline:
    1. Upload audio to S3
    2. Transcribe audio to text
    3. Generate LLM response
    4. Convert response to speech
    """
    start_time = time.time()
    processing_times = {}
    
    try:
        # 1. Upload to S3
        s3_start_time = time.time()
        s3_adapter = S3Adapter()
        s3_url = await s3_adapter.upload_audio(file.file, file.filename)
        processing_times["s3_upload"] = time.time() - s3_start_time
        
        # 2. Transcribe audio
        transcribe_start_time = time.time()
        transcribe_adapter = TranscribeAdapter()
        transcription = transcribe_adapter.transcribe_audio(s3_url)
        processing_times["transcription"] = time.time() - transcribe_start_time
        
        # 3. Generate LLM response
        llm_start_time = time.time()
        claude_handler = ClaudeHandler()
        response_text = claude_handler.generate_response(transcription)
        processing_times["llm_processing"] = time.time() - llm_start_time
        
        # 4. Convert to speech
        polly_start_time = time.time()
        polly_adapter = PollyAdapter()
        audio_url = polly_adapter.synthesize_speech(response_text)
        processing_times["speech_synthesis"] = time.time() - polly_start_time
        
        total_time = time.time() - start_time
        
        return AudioProcessingResponse(
            input_audio=s3_url,
            transcription=transcription,
            response_text=response_text,
            response_audio=audio_url,
            processing_time=processing_times,
            total_time=total_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")


@router.post("/upload", summary="Upload audio file to S3")
async def upload_audio(file: UploadFile = File(...)):
    """Upload an audio file to S3 and return the S3 URL."""
    try:
        start_time = time.time()
        s3_adapter = S3Adapter()
        s3_url = await s3_adapter.upload_audio(file.file, file.filename)
        processing_time = time.time() - start_time
        
        return {
            "input_audio": s3_url,
            "processing_time": processing_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")


@router.post("/transcribe", summary="Transcribe audio from S3 URL")
async def transcribe_audio(request: TranscriptionRequest):
    """Transcribe audio from an S3 URL."""
    try:
        start_time = time.time()
        transcribe_adapter = TranscribeAdapter()
        transcription = transcribe_adapter.transcribe_audio(request.s3_url)
        processing_time = time.time() - start_time
        
        return {
            "transcription": transcription,
            "processing_time": processing_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/generate-response", summary="Generate LLM response from text")
async def generate_response(request: TextProcessingRequest):
    """Generate a response from Claude using the provided text."""
    try:
        start_time = time.time()
        claude_handler = ClaudeHandler()
        response_text = claude_handler.generate_response(request.text)
        processing_time = time.time() - start_time
        
        return {
            "response_text": response_text,
            "processing_time": processing_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {str(e)}")


@router.post("/synthesize-speech", summary="Convert text to speech using Amazon Polly")
async def synthesize_speech(request: TextProcessingRequest):
    """Convert text to speech using Amazon Polly."""
    try:
        start_time = time.time()
        polly_adapter = PollyAdapter()
        audio_url = polly_adapter.synthesize_speech(request.text)
        processing_time = time.time() - start_time
        
        return {
            "response_audio": audio_url,
            "processing_time": processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")


# Streaming endpoints
@router.post("/streaming/transcribe", summary="Transcribe audio using streaming")
async def transcribe_streaming(file: UploadFile = File(...), language: str = "en-US"):
    """Transcribe audio using AWS Transcribe streaming service."""
    audio_path = None
    
    try:
        # Create transcription service
        transcription_service = AudioTranscriptionService()
        
        # Create temp file for processing
        audio_path = await create_temp_audio_file(file)
        
        # Process the audio file
        start_time = time.time()
        transcript = await transcription_service.process_audio_file(audio_path, language)
        processing_time = time.time() - start_time
        
        if not transcript:
            return JSONResponse(
                status_code=422,
                content={"error": "Failed to transcribe audio"}
            )
        
        return {
            "transcript": transcript,
            "processing_time": processing_time
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Transcription failed: {str(e)}"}
        )
    finally:
        if audio_path:
            clean_temp_file(audio_path)


@router.post("/streaming/text-to-speech", summary="Process text to speech")
async def process_text_to_speech(request: TextProcessingRequest):
    """
    Process text through LLM and speech synthesis:
    1. Generate LLM response
    2. Convert to speech
    """
    start_time = time.time()
    processing_times = {}
    
    try:
        # 1. Generate LLM response
        llm_start_time = time.time()
        claude_handler = ClaudeHandler()
        response_text = claude_handler.generate_response(request.text)
        processing_times["llm_processing"] = time.time() - llm_start_time
        
        # 2. Convert to speech
        polly_start_time = time.time()
        polly_adapter = PollyAdapter()
        audio_url = polly_adapter.synthesize_speech(response_text)
        processing_times["speech_synthesis"] = time.time() - polly_start_time
        
        total_time = time.time() - start_time
        
        return {
            "response_text": response_text,
            "response_audio": audio_url,
            "processing_time": processing_times,
            "total_time": total_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")


@router.post("/streaming/complete", summary="Process audio with streaming services")
async def process_audio_streaming_complete(file: UploadFile = File(...), language: str = "en-US"):
    """
    Process audio through the complete pipeline using streaming services:
    1. Transcribe audio using streaming
    2. Generate LLM response
    3. Convert response to speech
    """
    start_time = time.time()
    processing_times = {}
    audio_path = None
    
    try:
        # 1. Transcribe audio
        transcribe_start_time = time.time()
        transcription_service = AudioTranscriptionService()
        
        # Create temp file for processing
        audio_path = await create_temp_audio_file(file)
        
        # Process the audio file
        transcript = await transcription_service.process_audio_file(audio_path, language)
        processing_times["transcription"] = time.time() - transcribe_start_time
        
        if not transcript:
            return JSONResponse(
                status_code=422,
                content={"error": "Failed to transcribe audio"}
            )
        
        # 2. Generate LLM response
        llm_start_time = time.time()
        claude_handler = ClaudeHandler()
        response_text = claude_handler.generate_response(transcript)
        processing_times["llm_processing"] = time.time() - llm_start_time
        
        # 3. Convert to speech
        polly_start_time = time.time()
        polly_adapter = PollyAdapter()
        audio_url = polly_adapter.synthesize_speech(response_text)
        processing_times["speech_synthesis"] = time.time() - polly_start_time
        
        total_time = time.time() - start_time
        
        return {
            "transcription": transcript,
            "response_text": response_text,
            "response_audio": audio_url,
            "processing_time": processing_times,
            "total_time": total_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
    finally:
        if audio_path:
            clean_temp_file(audio_path)