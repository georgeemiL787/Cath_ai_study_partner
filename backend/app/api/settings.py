"""
Settings API endpoints for AI Study Partner
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
from pathlib import Path
from ..services import service_manager

router = APIRouter()

class SettingsRequest(BaseModel):
    # AI Settings
    llm_provider: Optional[str] = None  # gemini|openai|deepseek|auto
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: Optional[str] = None
    deepseek_model: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    
    # Capture Settings
    screen_fps: Optional[int] = None
    audio_enabled: Optional[bool] = None
    audio_sample_rate: Optional[int] = None
    audio_chunk_size: Optional[int] = None
    
    # OCR Settings
    ocr_engine: Optional[str] = None
    ocr_language: Optional[str] = None
    ocr_preprocess: Optional[bool] = None
    
    # STT Settings
    stt_engine: Optional[str] = None
    whisper_model: Optional[str] = None
    stt_language: Optional[str] = None
    
    # Privacy Settings
    privacy_mode: Optional[str] = None
    data_retention_days: Optional[int] = None
    encryption_enabled: Optional[bool] = None
    
    # Export Settings
    export_formats: Optional[list] = None
    anki_deck_name: Optional[str] = None
    # Branding / Persona
    assistant_name: Optional[str] = None
    brand_name: Optional[str] = None

class SettingsResponse(BaseModel):
    success: bool
    settings: Dict[str, Any]
    message: Optional[str] = None

# Settings file path
SETTINGS_FILE = Path("data/settings.json")

def ensure_settings_dir():
    """Ensure the settings directory exists"""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_default_settings() -> Dict[str, Any]:
    """Load default settings"""
    return {
        # AI Settings
        "llm_provider": "gemini",
        "openai_api_key": "",
        "gemini_api_key": "",
        "deepseek_api_key": "",
        "deepseek_base_url": "https://api.deepseek.com",
        "deepseek_model": "deepseek-chat",
        "model": "gpt-4-turbo-preview",
        "max_tokens": 1000,
        "temperature": 0.7,
        
        # Capture Settings
        "screen_fps": 1,
        "audio_enabled": True,
        "audio_sample_rate": 16000,
        "audio_chunk_size": 1024,
        
        # OCR Settings
        "ocr_engine": "tesseract",
        "ocr_language": "eng",
        "ocr_preprocess": True,
        
        # STT Settings
        "stt_engine": "whisper",
        "whisper_model": "base",
        "stt_language": "en",
        
        # Privacy Settings
        "privacy_mode": "local",
        "data_retention_days": 30,
        "encryption_enabled": True,
        
        # Export Settings
        "export_formats": ["anki", "csv", "pdf"],
        "anki_deck_name": "AI Study Partner",
        # Branding / Persona
        "assistant_name": "AI Study Partner",
        "brand_name": "AI Study Partner"
    }

def load_settings() -> Dict[str, Any]:
    """Load settings from file"""
    ensure_settings_dir()
    
    if not SETTINGS_FILE.exists():
        return load_default_settings()
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        # Merge with defaults to ensure all keys exist
        default_settings = load_default_settings()
        default_settings.update(settings)
        return default_settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return load_default_settings()

def save_settings(settings: Dict[str, Any]) -> bool:
    """Save settings to file"""
    try:
        ensure_settings_dir()
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    """Get current settings"""
    try:
        settings = load_settings()
        return SettingsResponse(
            success=True,
            settings=settings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load settings: {str(e)}")

@router.post("/settings", response_model=SettingsResponse)
async def update_settings(request: SettingsRequest):
    """Update settings"""
    try:
        # Load current settings
        current_settings = load_settings()
        
        # Update only provided fields
        update_data = request.dict(exclude_unset=True)
        current_settings.update(update_data)
        
        # Save updated settings
        if save_settings(current_settings):
            # Apply settings to running services (best effort)
            try:
                await service_manager.apply_settings(current_settings)
            except Exception as e:
                print(f"Warning: Failed to apply settings at runtime: {e}")
            return SettingsResponse(
                success=True,
                settings=current_settings,
                message="Settings updated successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save settings")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@router.post("/settings/reset", response_model=SettingsResponse)
async def reset_settings():
    """Reset settings to default values"""
    try:
        default_settings = load_default_settings()
        if save_settings(default_settings):
            return SettingsResponse(
                success=True,
                settings=default_settings,
                message="Settings reset to default values"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to reset settings")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset settings: {str(e)}")

@router.get("/settings/validate")
async def validate_settings():
    """Validate current settings"""
    try:
        settings = load_settings()
        
        # Check if OpenAI API key is set
        has_openai_key = bool(settings.get("openai_api_key", "").strip())
        
        # Check if required directories exist
        data_dir_exists = Path("data").exists()
        vector_db_dir_exists = Path("data/vector_db").exists()
        
        return {
            "success": True,
            "validation": {
                "has_openai_key": has_openai_key,
                "data_dir_exists": data_dir_exists,
                "vector_db_dir_exists": vector_db_dir_exists,
                "settings_file_exists": SETTINGS_FILE.exists()
            },
            "recommendations": [
                "Set OpenAI API key for AI features" if not has_openai_key else None,
                "Create data directory" if not data_dir_exists else None,
                "Create vector database directory" if not vector_db_dir_exists else None
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate settings: {str(e)}")

