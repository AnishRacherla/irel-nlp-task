# Quick Start Guide

This guide will get you up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Internet connection

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
cd irel
```

### 2. Quick Setup (Windows)

Run the automated setup script:

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

This script will:
- Check Python installation
- Install FFmpeg (if Chocolatey is available)
- Create virtual environment
- Install all dependencies
- Create .env file

### 3. Configure API Key

Edit `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Add Your Videos

Edit `config/config.yaml` and add 5 video URLs:

```yaml
video_sources:
  video_1:
    url: "https://youtube.com/watch?v=YOUR_VIDEO_ID"
    language: "Hindi-English"
    domain: "Computer Science"
    duration_minutes: 10
```

### 5. Test Setup

```bash
python test_setup.py
```

This will verify:
- ✓ All packages installed
- ✓ FFmpeg available
- ✓ API key configured
- ✓ Config file valid

### 6. Run Pipeline

Process all videos:

```bash
python main.py --process-all
```

Or process a single video:

```bash
python main.py --video-id video_1
```

## What Happens Next?

The pipeline will:

1. **Download** videos and extract audio (~1-2 min per video)
2. **Transcribe** using Whisper (~2-3 min per video)
3. **Process** language and extract concepts (~30 sec per video)
4. **Map** prerequisite relationships (~30 sec per video)
5. **Generate** visualizations and outputs (~10 sec per video)

**Total time**: ~5-8 minutes per video

## View Results

After processing, check:

```
outputs/
├── graphs/
│   ├── video_1_complete_output.json
│   ├── video_1_graph.graphml
│   └── ...
├── visualizations/
│   ├── video_1_interactive_graph.html  ← Open this in browser!
│   ├── video_1_graph.png
│   └── ...
└── summary_report.json
```

**Open the interactive visualization** in your browser to explore the concept dependency graph!

## Common First-Time Issues

### Issue: FFmpeg not found

**Solution**:
```powershell
# Windows (with Chocolatey)
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### Issue: API key error

**Solution**: Make sure .env has the correct key:
```
OPENAI_API_KEY=sk-proj-...  # Should start with sk-
```

### Issue: Video download fails

**Solution**: 
- Verify the URL is accessible
- Try a different video
- Update yt-dlp: `pip install --upgrade yt-dlp`

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [example_usage.py](example_usage.py) for programmatic usage
- Explore the generated visualizations
- Customize config.yaml for your needs

## Support

If you encounter issues:
1. Run `python test_setup.py` to diagnose
2. Check the log files in `outputs/*.log`
3. Review [README.md](README.md) troubleshooting section

---

**Tip**: Start with just 1-2 videos to test the pipeline before processing all 5!
