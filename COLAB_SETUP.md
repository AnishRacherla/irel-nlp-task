# 🌐 Google Colab Setup Guide

This guide shows how to run the **Code-Mixed Pedagogical Flow Extractor** on Google Colab (100% FREE).

---

## 📋 Prerequisites

1. **GitHub Repository** (Recommended): Push your code to GitHub first
   ```bash
   # On your local machine
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/irel.git
   git push -u origin main
   ```

2. **Google Account**: For accessing Google Colab

---

## 🚀 Quick Start (Copy-Paste in Colab)

### Step 1: Clone Your Repository

```python
# Clone from GitHub
!git clone https://github.com/YOUR_USERNAME/irel.git
%cd irel
```

**Alternative (No GitHub):**
- Click folder icon (📁) on left sidebar
- Upload your entire `irel` folder
- Then run: `%cd irel`

---

### Step 2: Install Dependencies

```python
# System dependencies (FFmpeg for audio)
!apt-get update -qq
!apt-get install -y ffmpeg

# Python packages
!pip install -r requirements.txt

# spaCy model
!python -m spacy download en_core_web_sm

# NLTK data
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

---

### Step 3: Install Local Source Code

```python
# Install 'src' package in editable mode
!pip install -e .

# Verify installation
from src.pipeline import PedagogicalFlowPipeline
print("✅ Installation successful!")
```

---

### Step 4: Process a Video

**Option A: Command Line**
```python
# Process video_2 (English/Hinglish - fastest, best quality)
!python example_usage.py --video-id video_2
```

**Option B: Python Code**
```python
from src.pipeline import PedagogicalFlowPipeline

# Initialize pipeline
pipeline = PedagogicalFlowPipeline('config/config.yaml')

# Process video
result = pipeline.process_single_video(
    video_id='video_2',
    url='https://www.youtube.com/watch?v=IlWB81vEH7g',
    language='en',
    domain='Computer Science'
)

# Show results
print(f"✅ Extracted {result['metadata']['total_concepts']} concepts")
print(f"🔗 Mapped {result['metadata']['total_relationships']} relationships")
```

---

### Step 5: View Results in Colab

```python
# Display interactive graph
from IPython.display import IFrame, display
display(IFrame('outputs/visualizations/video_2_interactive_graph.html', width=1000, height=600))
```

```python
# View extracted concepts (JSON)
import json
with open('outputs/graphs/video_2_complete_output.json', 'r') as f:
    data = json.load(f)
    
print(f"📊 Concepts: {len(data['concepts'])}")
print(f"🔗 Relationships: {len(data['relationships'])}")

# Show top 5 concepts
print("\n📚 Top Concepts:")
for concept in data['concepts'][:5]:
    print(f"  {concept['id']}: {concept['name']} (importance: {concept['importance']})")
```

---

### Step 6: Download Results

```python
from google.colab import files

# Download interactive graph
files.download('outputs/visualizations/video_2_interactive_graph.html')

# Download JSON output
files.download('outputs/graphs/video_2_complete_output.json')

# Download static PNG
files.download('outputs/visualizations/video_2_graph.png')
```

---

## 🎯 Process Multiple Videos

```python
# Process all configured videos
!python main.py --process-all

# Or process specific videos
!python example_usage.py --video-id video_1
!python example_usage.py --video-id video_2
!python example_usage.py --video-id video_3
```

---

## ⚡ Performance Tips for Colab

### 1. **Use GPU (Faster Whisper)**
- Go to: **Runtime → Change runtime type → GPU**
- Whisper will run 3-5x faster on GPU

```python
# Verify GPU is available
import torch
print(f"GPU available: {torch.cuda.is_available()}")
print(f"GPU name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

### 2. **Mount Google Drive (Save Outputs)**
```python
from google.colab import drive
drive.mount('/content/drive')

# Save outputs to Drive
!cp -r outputs /content/drive/MyDrive/irel_outputs
```

### 3. **Clear Cache Between Runs**
```python
# Clear cached transcripts to force reprocessing
!rm -rf data/transcripts/*
!rm -rf data/audio/*
!rm -rf outputs/*
```

---

## 🐛 Troubleshooting

### Error: "No module named 'src'"
**Solution**: Install in editable mode
```python
%cd /content/irel  # Make sure you're in project root
!pip install -e .
```

### Error: "FFmpeg not found"
**Solution**: Install FFmpeg
```python
!apt-get update -qq
!apt-get install -y ffmpeg
!ffmpeg -version  # Verify
```

### Error: "spaCy model not found"
**Solution**: Download model
```python
!python -m spacy download en_core_web_sm
```

### Video Takes Too Long (>10 min)
**Solution 1**: Use GPU runtime
**Solution 2**: Use `tiny` or `base` Whisper model
```python
# Edit config/config.yaml
import yaml

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

config['transcription']['whisper_model_size'] = 'tiny'  # Fastest

with open('config/config.yaml', 'w') as f:
    yaml.dump(config, f)
```

---

## 📊 Expected Runtime (Colab FREE Tier)

| Whisper Model | CPU Time | GPU Time | Quality |
|---------------|----------|----------|---------|
| `tiny`        | 1-2 min  | 30 sec   | ~80%    |
| `base`        | 3-5 min  | 1 min    | ~90%    |
| `small`       | 8-12 min | 2-3 min  | ~95%    |
| `medium`      | 30+ min  | 8-10 min | ~98%    |

**Recommendation**: Use `base` model with GPU (best speed/quality balance)

---

## 🎓 Complete Colab Notebook Template

See [dummy.ipynb](dummy.ipynb) for a ready-to-use Colab notebook with all steps pre-configured.

---

## 💾 Save Your Work

Colab instances time out after 12 hours. Always save important data:

```python
# Option 1: Download to computer
from google.colab import files
!tar -czf irel_outputs.tar.gz outputs/
files.download('irel_outputs.tar.gz')

# Option 2: Save to Google Drive
from google.colab import drive
drive.mount('/content/drive')
!cp -r outputs /content/drive/MyDrive/irel_results/
```

---

## ✅ Validation

Check everything works:
```python
!python validate_submission.py
```

---

## 🔗 Useful Links

- **Original Repo**: `https://github.com/YOUR_USERNAME/irel`
- **Colab Notebook**: Open `dummy.ipynb` in Google Colab
- **iREL 2026**: https://irel.iitgn.ac.in/

---

## 📝 Notes

- Colab gives 12 hours of continuous runtime (FREE tier)
- GPU is faster but limited to ~4-6 hours/day
- All outputs are saved in `outputs/` folder
- Cache is preserved during session (transcripts not re-downloaded)
- Session resets when runtime disconnects

Enjoy extracting pedagogical flows! 🚀
