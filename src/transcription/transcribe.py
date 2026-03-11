"""
Video transcription module using Whisper
"""

import whisper
import yt_dlp
from pathlib import Path
from typing import Dict, Any, Optional
import json
from tqdm import tqdm


class VideoTranscriber:
    """Handle video download and transcription"""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize transcriber
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.whisper_model = None
        
        # Get paths from config
        self.video_dir = Path(config.get('paths', {}).get('video_dir', 'data/videos'))
        self.audio_dir = Path(config.get('paths', {}).get('audio_dir', 'data/audio'))
        self.transcripts_dir = Path(config.get('paths', {}).get('transcripts_dir', 'data/transcripts'))
        
        # Ensure directories exist
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_whisper_model(self):
        """Load Whisper model lazily"""
        if self.whisper_model is None:
            model_size = self.config.get('transcription', {}).get('whisper_model_size', 'medium')
            self.logger.info(f"Loading Whisper model: {model_size}")
            self.whisper_model = whisper.load_model(model_size)
            self.logger.info("Whisper model loaded successfully")
    
    def download_video(self, url: str, video_id: str) -> Optional[Path]:
        """
        Download video from URL
        
        Args:
            url: Video URL
            video_id: Unique identifier for the video
        
        Returns:
            Path to downloaded audio file
        """
        try:
            self.logger.info(f"Downloading video: {video_id} from {url}")
            
            # Output template (will get actual extension from yt-dlp)
            output_template = str(self.audio_dir / f"{video_id}.%(ext)s")
            
            # Check if any audio file already exists for this video_id
            existing_files = list(self.audio_dir.glob(f"{video_id}.*"))
            if existing_files:
                audio_path = existing_files[0]
                self.logger.info(f"Audio file already exists: {audio_path}")
                return audio_path
            
            # yt-dlp options (NO FFmpeg postprocessing - download audio as-is)
            ydl_opts = {
                'format': 'bestaudio/best',  # Download best audio without conversion
                'outtmpl': output_template,
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Get the actual downloaded filename
                downloaded_file = ydl.prepare_filename(info)
            
            # Find the downloaded file (yt-dlp may use .webm, .m4a, .opus, etc.)
            audio_files = list(self.audio_dir.glob(f"{video_id}.*"))
            if audio_files:
                audio_path = audio_files[0]
                self.logger.info(f"Video downloaded successfully: {audio_path}")
                self.logger.info(f"Format: {audio_path.suffix} (Whisper supports this natively)")
                return audio_path
            else:
                self.logger.error(f"Downloaded file not found for {video_id}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error downloading video {video_id}: {str(e)}")
            return None
    
    def transcribe_audio(self, audio_path: Path, video_id: str, language: str = "auto") -> Optional[Dict[str, Any]]:
        """
        Transcribe audio using Whisper
        
        Args:
            audio_path: Path to audio file
            video_id: Unique identifier for the video
            language: Language code or 'auto' for auto-detection
        
        Returns:
            Transcription result dictionary
        """
        try:
            self.logger.info(f"Transcribing audio: {video_id}")
            
            # Load Whisper model
            self._load_whisper_model()
            
            # Transcribe
            if language == "auto":
                result = self.whisper_model.transcribe(str(audio_path), verbose=False)
            else:
                result = self.whisper_model.transcribe(str(audio_path), language=language, verbose=False)
            
            # Save transcript
            transcript_path = self.transcripts_dir / f"{video_id}_transcript.json"
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Transcription completed: {transcript_path}")
            self.logger.info(f"Detected language: {result.get('language', 'unknown')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio {video_id}: {str(e)}")
            return None
    
    def process_video(self, url: str, video_id: str, language: str = "auto") -> Optional[Dict[str, Any]]:
        """
        Complete pipeline: download and transcribe video
        
        Args:
            url: Video URL
            video_id: Unique identifier
            language: Language code or 'auto'
        
        Returns:
            Transcription result
        """
        # Check if transcript already exists
        transcript_path = self.transcripts_dir / f"{video_id}_transcript.json"
        if transcript_path.exists():
            self.logger.info(f"Loading existing transcript: {transcript_path}")
            with open(transcript_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Download video
        audio_path = self.download_video(url, video_id)
        if audio_path is None:
            return None
        
        # Transcribe
        return self.transcribe_audio(audio_path, video_id, language)
    
    def get_transcript_text(self, video_id: str) -> Optional[str]:
        """
        Get plain text transcript for a video
        
        Args:
            video_id: Unique identifier
        
        Returns:
            Plain text transcript
        """
        transcript_path = self.transcripts_dir / f"{video_id}_transcript.json"
        if not transcript_path.exists():
            return None
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('text', '')
    
    def get_transcript_segments(self, video_id: str) -> Optional[list]:
        """
        Get segmented transcript with timestamps
        
        Args:
            video_id: Unique identifier
        
        Returns:
            List of transcript segments
        """
        transcript_path = self.transcripts_dir / f"{video_id}_transcript.json"
        if not transcript_path.exists():
            return None
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('segments', [])
