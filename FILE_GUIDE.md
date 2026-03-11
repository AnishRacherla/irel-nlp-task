# Project File Guide

A comprehensive guide to all files in this project and their purposes.

## 📖 Documentation Files

### README.md
**Purpose**: Main documentation  
**Contents**: 
- Project overview and problem statement
- Architecture diagram
- Setup instructions
- Usage guide
- Methodology and design decisions
- Output format specifications
- Troubleshooting guide

**When to read**: First file to read for understanding the project

### QUICKSTART.md
**Purpose**: Get started in 5 minutes  
**Contents**:
- Step-by-step setup (condensed)
- Quick configuration guide
- First run instructions
- Common issues and solutions

**When to read**: When you want to get running quickly without reading full README

### ARCHITECTURE.md
**Purpose**: Technical deep-dive  
**Contents**:
- Detailed system architecture
- Module design explanations
- Data flow diagrams
- Design decision rationale
- Performance considerations
- Scalability discussion

**When to read**: Understanding technical decisions, extending the system

### VIDEO_SELECTION_GUIDE.md
**Purpose**: Help find appropriate videos  
**Contents**:
- Video requirements checklist
- Recommended YouTube channels
- Search strategies
- Evaluation criteria
- Selection template
- Example selections

**When to read**: Before selecting your 5 videos

### PROJECT_SUMMARY.md
**Purpose**: Project completion guide  
**Contents**:
- What you have (complete checklist)
- Next steps breakdown
- Tips for strong submission
- Quick command reference
- Troubleshooting

**When to read**: After setup, before running pipeline

### LICENSE
**Purpose**: Software license  
**Contents**: MIT License text  
**Note**: Free to use, modify, and distribute

## ⚙️ Configuration Files

### config/config.yaml
**Purpose**: Main configuration file  
**Contents**:
- Video sources (your 5 videos)
- Transcription settings (Whisper model)
- Language processing settings
- Concept extraction settings
- Prerequisite mapping settings
- Output format preferences
- File paths

**When to edit**: 
- Adding your video URLs
- Changing Whisper model size
- Adjusting confidence thresholds
- Modifying output formats

### .env.example
**Purpose**: Template for environment variables  
**Contents**: API key placeholders  
**Usage**: Copy to `.env` and add your actual API keys

**Note**: The actual `.env` file should NEVER be committed to Git

## 🐍 Main Python Files

### main.py
**Purpose**: Entry point for the application  
**What it does**:
- Parses command-line arguments
- Initializes the pipeline
- Processes videos (single or batch)
- Displays progress and results

**Usage**:
```bash
python main.py --process-all          # Process all videos
python main.py --video-id video_1     # Process one video
```

### test_setup.py
**Purpose**: Verify installation and configuration  
**What it checks**:
- Python packages installed
- FFmpeg available
- API key configured
- Config file valid
- Videos added

**Usage**:
```bash
python test_setup.py
```

**When to run**: After setup, before processing videos

### validate_submission.py
**Purpose**: Pre-submission validation  
**What it checks**:
- All required files present
- Videos configured
- Pipeline run successfully
- README customized
- Git initialized

**Usage**:
```bash
python validate_submission.py
```

**When to run**: Before submitting your project

### example_usage.py
**Purpose**: Code examples for programmatic usage  
**Contents**:
- How to use pipeline from Python code
- How to access individual modules
- How to customize configuration
- Example workflows

**When to use**: Building custom applications on top of the pipeline

## 📦 Source Code Modules

### src/pipeline.py
**Purpose**: Main pipeline orchestrator  
**Key class**: `PedagogicalFlowPipeline`  
**What it does**:
- Coordinates all modules
- Manages workflow
- Handles errors
- Generates summary reports

**Key methods**:
- `process_single_video()`: Process one video
- `process_all_configured_videos()`: Process all from config
- `generate_summary_report()`: Create overall summary

### src/utils/config_loader.py
**Purpose**: Configuration management  
**Key class**: `ConfigLoader`  
**What it does**:
- Loads YAML configuration
- Handles environment variables
- Creates directories
- Provides config access

**Key methods**:
- `get(key)`: Get config value
- `get_video_sources()`: Get video list
- `get_api_key(provider)`: Get API key

### src/utils/logger.py
**Purpose**: Logging system  
**What it provides**:
- Colored console output
- File logging
- Log level management
- Timestamp formatting

**Function**: `setup_logger(name)` - Create logger instance

### src/transcription/transcribe.py
**Purpose**: Video transcription  
**Key class**: `VideoTranscriber`  
**What it does**:
- Downloads videos (yt-dlp)
- Extracts audio
- Transcribes with Whisper
- Saves transcripts as JSON

**Key methods**:
- `download_video()`: Get video from URL
- `transcribe_audio()`: Audio → Text
- `process_video()`: Complete pipeline

**Technology**: OpenAI Whisper, yt-dlp

### src/code_mixed_processor/language_processor.py
**Purpose**: Language analysis and standardization  
**Key class**: `CodeMixedProcessor`  
**What it does**:
- Detects languages (langdetect)
- Identifies code-mixing patterns
- Maps colloquial → standard terms
- Standardizes terminology

**Key methods**:
- `detect_languages()`: Identify languages
- `identify_code_mixing()`: Analyze mixing
- `standardize_terminology()`: Term mapping
- `process_transcript()`: Complete processing

**Technology**: langdetect, OpenAI GPT, regex for Indic scripts

### src/concept_extractor/extractor.py
**Purpose**: Concept extraction  
**Key class**: `ConceptExtractor`  
**What it does**:
- Extracts concepts via LLM
- Scores importance (1-5)
- Categorizes by difficulty
- Refines and deduplicates

**Key methods**:
- `extract_concepts()`: LLM-based extraction
- `refine_concepts()`: Deduplication
- `categorize_concepts()`: Organization
- `extract_and_refine()`: Complete pipeline

**Technology**: OpenAI GPT-4o-mini

**Output**: List of concepts with metadata

### src/prerequisite_mapper/mapper.py
**Purpose**: Prerequisite relationship mapping  
**Key class**: `PrerequisiteMapper`  
**What it does**:
- Identifies prerequisites
- Maps concept dependencies
- Builds graph structure
- Scores relationship confidence

**Key methods**:
- `map_prerequisites()`: Extract relationships
- `build_dependency_graph()`: Create graph
- `identify_foundational_concepts()`: Find entry points
- `map_and_build()`: Complete pipeline

**Technology**: OpenAI GPT-4o-mini, NetworkX

**Output**: Dependency graph with nodes and edges

### src/visualizer/graph_builder.py
**Purpose**: Graph visualization and output  
**Key class**: `GraphVisualizer`  
**What it does**:
- Saves JSON, GraphML, DOT formats
- Generates interactive HTML (PyVis)
- Creates static PNG (Matplotlib)
- Color-codes by importance

**Key methods**:
- `save_json()`: Export as JSON
- `save_graphml()`: Export as GraphML
- `create_interactive_visualization()`: HTML graph
- `create_static_visualization()`: PNG image
- `generate_all_outputs()`: All formats

**Technology**: NetworkX, PyVis, Matplotlib

## 🔧 Setup and Build Files

### requirements.txt
**Purpose**: Python dependencies  
**Contents**: List of required packages with versions  
**Usage**: `pip install -r requirements.txt`

**Key packages**:
- openai (GPT API)
- openai-whisper (Transcription)
- yt-dlp (Video download)
- networkx (Graph processing)
- pyvis (Interactive visualization)
- matplotlib (Static visualization)

### setup.ps1
**Purpose**: Automated setup script (Windows PowerShell)  
**What it does**:
- Checks Python installation
- Checks/installs FFmpeg
- Creates virtual environment
- Installs dependencies
- Creates .env file

**Usage**: 
```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

### .gitignore
**Purpose**: Git ignore rules  
**What it excludes**:
- Python cache (`__pycache__`)
- Virtual environment (`venv/`)
- API keys (`.env`)
- Downloaded videos (large files)
- Generated outputs (reproducible)
- IDE config files

**Important**: Prevents accidentally committing sensitive data

## 📊 Data Directories (Generated)

### data/
Created during pipeline execution. Contains:

**data/videos/**
- Downloaded video files (MP4)
- Excluded from Git (size)

**data/audio/**
- Extracted audio files (MP3)
- Intermediate files for transcription

**data/transcripts/**
- JSON transcript files
- Contains text, segments, language

**Structure**:
```
data/
├── videos/
│   └── video_1.mp4
├── audio/
│   └── video_1.mp3
└── transcripts/
    └── video_1_transcript.json
```

### outputs/
Generated visualizations and results. Contains:

**outputs/graphs/**
- `{video_id}_complete_output.json` - Full results
- `{video_id}_graph.json` - Graph data only
- `{video_id}_graph.graphml` - GraphML format
- `{video_id}_graph.dot` - GraphViz format

**outputs/visualizations/**
- `{video_id}_interactive_graph.html` - Interactive visualization ⭐
- `{video_id}_graph.png` - Static image

**outputs/**
- `summary_report.json` - Overall summary
- `*.log` - Log files

## 🏗️ Package Structure

### src/
Main source code package

```
src/
├── __init__.py                      # Package marker
├── pipeline.py                      # Main orchestrator
│
├── utils/
│   ├── __init__.py
│   ├── config_loader.py             # Configuration
│   └── logger.py                    # Logging
│
├── transcription/
│   ├── __init__.py
│   └── transcribe.py                # Video → Text
│
├── code_mixed_processor/
│   ├── __init__.py
│   └── language_processor.py        # Language analysis
│
├── concept_extractor/
│   ├── __init__.py
│   └── extractor.py                 # Concept extraction
│
├── prerequisite_mapper/
│   ├── __init__.py
│   └── mapper.py                    # Relationship mapping
│
└── visualizer/
    ├── __init__.py
    └── graph_builder.py             # Visualization
```

## 📋 File Usage Flow

### Setup Phase
1. Read `README.md` or `QUICKSTART.md`
2. Review `VIDEO_SELECTION_GUIDE.md`
3. Run `setup.ps1` (or manual setup)
4. Edit `.env` (copy from `.env.example`)
5. Edit `config/config.yaml`
6. Run `test_setup.py`

### Execution Phase
1. Run `main.py --process-all`
2. Pipeline uses:
   - `config/config.yaml` → Configuration
   - `src/pipeline.py` → Orchestration
   - `src/transcription/` → Video → Text
   - `src/code_mixed_processor/` → Language processing
   - `src/concept_extractor/` → Concept identification
   - `src/prerequisite_mapper/` → Dependency mapping
   - `src/visualizer/` → Output generation
3. Generates files in `outputs/`

### Validation Phase
1. Run `validate_submission.py`
2. Check `outputs/summary_report.json`
3. Open `outputs/visualizations/*.html`
4. Verify all outputs look correct

### Submission Phase
1. Read `PROJECT_SUMMARY.md`
2. Update `README.md` (video links, demo)
3. Initialize Git (if not done)
4. Commit and push to GitHub
5. Upload demo video
6. Submit links

## 🎯 Most Important Files

### For Understanding the Project:
1. **README.md** - Complete overview
2. **ARCHITECTURE.md** - Technical details
3. **src/pipeline.py** - Main logic

### For Running the Project:
1. **config/config.yaml** - Your videos and settings
2. **.env** - Your API keys
3. **main.py** - Execution entry point

### For Results:
1. **outputs/visualizations/*.html** - Interactive graphs (BEST)
2. **outputs/graphs/*_complete_output.json** - Full data
3. **outputs/summary_report.json** - Overall summary

### For Troubleshooting:
1. **test_setup.py** - Verify setup
2. **outputs/*.log** - Error logs
3. **QUICKSTART.md** - Common issues

## 💡 Tips

- **Start with**: QUICKSTART.md
- **Refer to**: README.md
- **Deep dive**: ARCHITECTURE.md
- **Before submitting**: validate_submission.py
- **For videos**: VIDEO_SELECTION_GUIDE.md

---

**Need more help?** Each Python file has extensive docstrings. Use:
```python
help(ModuleName)
help(ClassName)
help(function_name)
```

Or read the source code - it's well-commented!
