from fastapi import APIRouter, UploadFile, HTTPException
from src.adapters.aws.s3_adapter import S3Adapter
from src.adapters.aws.transcribe_adapter import TranscribeAdapter
from src.services.llm.anthropic_handler import ClaudeHandler
from src.adapters.aws.polly_adapter import PollyAdapter

router = APIRouter()

@router.post("/process-audio")
async def process_audio(file: UploadFile):
    try:
        # 1. Upload to S3
        s3 = S3Adapter()
        s3_url = await s3.upload_audio(file.file, file.filename)
        
        # 2. Transcribe audio
        transcribe = TranscribeAdapter()
        text = transcribe.transcribe_audio(s3_url)
        
        # 3. Generate LLM response
        claude = ClaudeHandler()
        response_text = claude.generate_response(text)
        
        # 4. Convert to speech
        polly = PollyAdapter()
        audio_url = polly.synthesize_speech(response_text)
        
        return {
            "input_audio": s3_url,
            "transcription": text,
            "response_audio": audio_url,
            "response_text": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))