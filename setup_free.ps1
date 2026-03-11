# 🎉 COMPLETELY FREE SETUP
# No API keys needed! Uses only traditional NLP

Write-Host "=" * 60 -ForegroundColor Green
Write-Host "  Code-Mixed Pedagogical Flow Extractor (FREE VERSION)" -ForegroundColor Green
Write-Host "  100% FREE - No API costs!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""

# Step 1: Install Python packages
Write-Host "[1/4] Installing Python packages..." -ForegroundColor Cyan
pip install openai-whisper yt-dlp pydub ffmpeg-python spacy nltk keybert scikit-learn langdetect networkx matplotlib plotly graphviz pyvis pandas numpy pyyaml python-dotenv requests tqdm colorama sentence-transformers

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Package installation failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Download spaCy model
Write-Host ""
Write-Host "[2/4] Downloading spaCy English model..." -ForegroundColor Cyan
python -m spacy download en_core_web_sm

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: spaCy model download failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Download NLTK data
Write-Host ""
Write-Host "[3/4] Downloading NLTK data..." -ForegroundColor Cyan
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: NLTK data download failed!" -ForegroundColor Red
    exit 1
}

# Step 4: Check FFmpeg
Write-Host ""
Write-Host "[4/4] Checking FFmpeg..." -ForegroundColor Cyan
$ffmpegCheck = Get-Command ffmpeg -ErrorAction SilentlyContinue

if ($null -eq $ffmpegCheck) {
    Write-Host "WARNING: FFmpeg not found!" -ForegroundColor Yellow
    Write-Host "To install FFmpeg:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://ffmpeg.org/download.html" -ForegroundColor Yellow
    Write-Host "  2. Or use Chocolatey: choco install ffmpeg" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✓ FFmpeg found: $($ffmpegCheck.Source)" -ForegroundColor Green
}

# Success message
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "✓ FREE SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Cost: $0.00 (completely free!)" -ForegroundColor Green
Write-Host "Uses: KeyBERT, spaCy, NLTK, embeddings (no LLM)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit config/config.yaml and add your video URL" -ForegroundColor White
Write-Host "  2. Run: python example_usage.py --video-id video_1" -ForegroundColor White
Write-Host ""
Write-Host "Your video is already configured:" -ForegroundColor Yellow
Write-Host "  video_1: https://www.youtube.com/watch?v=XV-lIaO00H8" -ForegroundColor White
Write-Host ""
