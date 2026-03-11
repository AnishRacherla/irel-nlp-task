"""
Quick test script to verify pipeline setup
"""

import sys
from pathlib import Path

def check_imports():
    """Check if all required packages are importable"""
    print("Checking package imports...")
    
    packages = {
        'openai': 'OpenAI',
        'whisper': 'Whisper',
        'yt_dlp': 'yt-dlp',
        'networkx': 'NetworkX',
        'matplotlib': 'Matplotlib',
        'pyvis': 'PyVis',
        'yaml': 'PyYAML',
        'langdetect': 'langdetect',
        'dotenv': 'python-dotenv'
    }
    
    failed = []
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - NOT FOUND")
            failed.append(name)
    
    return len(failed) == 0, failed


def check_api_key():
    """Check if API key is configured"""
    print("\nChecking API key configuration...")
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here':
        print("✗ OpenAI API key not configured")
        print("  Please edit .env and add your API key")
        return False
    elif not api_key.startswith('sk-'):
        print("⚠ API key format looks incorrect")
        return False
    else:
        print(f"✓ API key configured ({api_key[:7]}...)")
        return True


def check_config():
    """Check if configuration file exists and is valid"""
    print("\nChecking configuration...")
    
    config_path = Path('config/config.yaml')
    if not config_path.exists():
        print("✗ config/config.yaml not found")
        return False
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check video sources
        video_sources = config.get('video_sources', {})
        configured_videos = sum(1 for v in video_sources.values() if v.get('url', ''))
        
        print(f"✓ Configuration file valid")
        print(f"  Configured videos: {configured_videos}/5")
        
        if configured_videos < 5:
            print("  ⚠ Please add 5 video URLs to config.yaml")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading config: {str(e)}")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\nChecking FFmpeg...")
    
    import subprocess
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg installed: {version_line}")
            return True
        else:
            print("✗ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("✗ FFmpeg not found")
        print("  Please install FFmpeg: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"✗ Error checking FFmpeg: {str(e)}")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("iREL Pedagogical Flow Extractor - Setup Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    # Check imports
    imports_ok, failed = check_imports()
    checks.append(('Package imports', imports_ok))
    if not imports_ok:
        print(f"\n⚠ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    checks.append(('FFmpeg', ffmpeg_ok))
    
    # Check API key
    api_ok = check_api_key()
    checks.append(('API Key', api_ok))
    
    # Check config
    config_ok = check_config()
    checks.append(('Configuration', config_ok))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, status in checks:
        status_str = "✓ PASS" if status else "✗ FAIL"
        print(f"{name:.<30} {status_str}")
    
    all_ok = all(status for _, status in checks)
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ All checks passed! You're ready to run the pipeline.")
        print("\nNext step: python main.py --process-all")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
        print("\nSee README.md for detailed setup instructions.")
    print("=" * 60)
    
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
