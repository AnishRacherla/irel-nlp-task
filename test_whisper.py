import whisper
import sys
from pathlib import Path

model = whisper.load_model('base')
try:
    audio_path = Path('data/audio/video_3.webm').resolve()
    print(f"Transcribing: {audio_path}")
    print(f"File exists: {audio_path.exists()}")
    result = model.transcribe(str(audio_path), verbose=False)
    print(f"Success! Length: {len(result['text'])} chars")
    print(f"Text preview: {result['text'][:200]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
