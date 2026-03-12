# Code-Mixed Pedagogical Flow Extractor

Automatically extracts educational concepts and their prerequisite relationships from YouTube lecture videos — including videos where the instructor code-mixes between English, Hindi, and Telugu. The output is a directed prerequisite graph that makes the pedagogical structure of a lecture explicit.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Video Sources](#video-sources)
3. [Architecture](#architecture)
4. [Pipeline Stages](#pipeline-stages)
5. [Output Structure](#output-structure)
6. [Setup Instructions](#setup-instructions)
7. [Running in Google Colab (Recommended)](#running-in-google-colab-recommended)
8. [Running Locally](#running-locally)
9. [Configuration](#configuration)

---

## Problem Statement

Indian educational YouTube channels frequently teach in a code-mixed style — the instructor speaks English but inserts Hindi or Telugu technical terms, filler phrases, and explanations mid-sentence. Standard NLP pipelines trained on clean English fail on this input because:

- Transliterated words (`"iska matlab hai"`, `"undi"`) are not in any English vocabulary.
- Stopword lists miss language-specific fillers.
- Concept extractors based on frequency alone surface phrases like *"Our Python Learning Journey"* instead of *"Data Types"*.

This system adds a translation/standardisation layer before concept extraction and uses Groq's Llama 3.3 70B as the final arbiter to keep only genuine educational concepts.

---

## Video Sources

| ID | URL | Language Mix | Domain |
|---|---|---|---|
| video_1 | [youtu.be/DWpVGpNfDmM](https://www.youtube.com/watch?v=DWpVGpNfDmM&list=PLdo5W4Nhv31bbKJzrsKfMpo_grxuLl8LU&index=8) | English + Hindi | Computer Science (Python) |
| video_2 | [youtu.be/SkE2kD2U4tU](https://www.youtube.com/watch?v=SkE2kD2U4tU) | English + Telugu | Physics (Computer Science ) |
| video_3 | [youtu.be/-kGMwaROIZk](https://www.youtube.com/watch?v=-kGMwaROIZk&list=PL724pdDXl9Q1KxL7dQ6HlyjO7tbJzfh5f) | English + Hindi | Computer Science (Python) |
| video_4 | [youtu.be/SkE2kD2U4tU](https://www.youtube.com/watch?v=SkE2kD2U4tU) | English + Telugu | Physics (Magnetism) |
| video_5 | [youtu.be/98BzS5Oz5E4](https://www.youtube.com/watch?v=98BzS5Oz5E4) | English + Hindi | Computer Science |

Videos were selected to test the pipeline across two domains (CS and Physics) and a non-English languages (Hindi and English) to verify domain-agnostic and language-agnostic behaviour.

---

## Architecture

```
YouTube URL
    │
    ▼
┌─────────────────────────────┐
│  1. Transcription           │  OpenAI Whisper (large-v3, GPU)
│     yt-dlp → audio → text  │  → timestamped transcript
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  2. Preprocessing           │  spaCy + NLTK
│     tokenise, NP extract,   │  → sentences, noun phrases,
│     cue phrase detection,   │    cue phrase matches,
│     dependency parse        │    dependency trees
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  3. Code-Mixed Processing   │  Hardcoded dict (Telugu/Hindi)
│     translate non-English   │  → Google Translate fallback
│     tokens to English       │  → standardised transcript
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  4. Concept Extraction      │  4-signal hybrid:
│     KeyBERT (GPU)           │    keybert_score  ×0.7
│     + NP frequency          │    + np_score     ×0.2
│     + Wikipedia boost       │    + temporal     ×0.1
│     + Groq LLM validation   │  → Groq Llama validates/filters
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  5. Prerequisite Mapping    │  4-signal hybrid:
│     cue phrases             │    confidence boosted by
│     + temporal order        │    signal diversity
│     + semantic similarity   │  → Groq Llama selects and
│     + dependency parse      │    labels relationship type
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  6. Visualisation           │  NetworkX DiGraph
│     JSON + GraphML + DOT    │  Hierarchical BFS layout
│     + PNG + HTML (pyvis)    │  prerequisites at top ↓
└─────────────────────────────┘
```

---

## Pipeline Stages

### Stage 1 — Transcription (`src/transcription/transcribe.py`)

`yt-dlp` downloads the audio track; Whisper `large-v3` converts it to text with timestamps. `large-v3` is chosen because it is OpenAI's highest-accuracy Whisper model — it handles code-mixed speech (Hindi/Telugu words inside English sentences) and informal pronunciation significantly better than smaller variants like `base` or `small`. Transcripts are stored under `data/transcripts/`.

### Stage 2 — Preprocessing (`src/preprocessing/preprocessor.py`)

spaCy (`en_core_web_sm`) tokenises the text and extracts **noun phrases** — the key insight here is that educational concepts are almost always nouns or noun phrases (*"Binary Search Tree"*, *"Magnetic Flux"*), so restricting candidates to NPs immediately removes a large amount of verb-phrase and adverbial junk. A dependency parser is also run to capture syntactic relationships between tokens.

Ten **cue-phrase regex patterns** are applied to find explicit pedagogical signals in the transcript — expressions like *"requires"*, *"builds on"*, *"before understanding"*, *"depends on"*, and *"once you know"*. When an instructor says *"before understanding loops, you need to know variables"*, the cue phrase *"before understanding"* directly encodes a prerequisite relationship. NLTK provides sentence segmentation and stopword filtering.

### Stage 3 — Code-Mixed Language Processing (`src/code_mixed_processor/language_processor.py`)

A two-layer translation cascade:
1. **Hardcoded dictionary** (priority) — common Telugu and Hindi technical terms and filler words mapped to English equivalents (e.g. `"undi"` → `"is"`, `"matlab"` → `"means"`, `"karke"` → `"by doing"`). The dictionary is applied first because it preserves the exact intended meaning — a human-verified translation is more reliable than a statistical one for recurring domain-specific terms.
2. **Google Translate fallback** (`deep_translator`) — sentence-level translation for anything not covered by the dictionary. The dictionary has limited vocabulary by design, so Google Translate handles the long tail of less common words and full non-English sentences.

**Rationale:** Prioritising the dictionary over a general-purpose translator avoids translation drift on high-frequency technical terms. Google Translate then covers everything the dictionary misses, keeping the output fully in English before concept extraction begins.

### Stage 4 — Concept Extraction (`src/concept_extractor/hybrid_extractor.py`)

Four signals are computed per candidate phrase:

| Signal | Weight | Description |
|---|---|---|
| KeyBERT score | 0.70 | Cosine similarity of keyphrase embedding to full-doc embedding |
| NP frequency | 0.20 | Normalised count in spaCy noun phrase list |
| Temporal position | 0.10 | Earlier = more foundational; penalises late-appearing terms |
| Wikipedia boost | +0.35 | If the phrase (or its first word) has a Wikipedia page it is likely a real concept |

**Blacklist filtering** removes generic academic phrases (*"learning journey"*, *"enough python"*, *"this learning"*) before scoring.

**Wikipedia-based domain boost** replaces a hardcoded `technical_patterns` list. Checking Wikipedia page existence with `wikipediaapi` is domain-agnostic: it boosts *Magnetic Flux* in a physics video the same way it boosts *Binary Search Tree* in a CS video. Results are cached in memory to avoid redundant HTTP calls.

**Groq Llama 3.3 70B** then receives the top-20 candidates and the full transcript. It returns up to 15 validated concepts with names, descriptions, importance scores, and categories. If the API call fails the pipeline falls back to a rule-based filter (which is why `validation_method: "rule_based_free"` appears in the JSON when Groq is unavailable).

### Stage 5 — Prerequisite Mapping (`src/prerequisite_mapper/hybrid_mapper.py`)

Four NLP signals generate candidate prerequisite pairs:

| Signal | Confidence | Rationale |
|---|---|---|
| Cue phrase match | 0.80 | Explicit pedagogical intent (*"requires"*, *"builds on"*) |
| Temporal order | 0.50–0.70 | Concepts introduced earlier are usually prerequisites |
| Semantic similarity | cosine × 0.7 | Related concepts are often in the same dependency chain |
| Dependency parse | 0.50 | Subject/object relations in the same sentence suggest coupling |

Candidates from all four signals are merged: pairs that appear in multiple signals get a confidence boost (up to +0.2), making multi-signal agreement the strongest predictor. **Groq Llama 3.3 70B** then validates the merged list, labels each relationship as `strict_prerequisite`, `recommended_prerequisite`, or `related`, and provides a one-sentence pedagogical rationale. Low-confidence pairs (< 0.5) are discarded.

**Rationale for LLM as final stage:** NLP signals alone cannot distinguish *"A is mentioned before B"* from *"A is a genuine prerequisite of B"*. The LLM has world knowledge about subject matter dependencies (e.g. it knows Variables must precede Loops) and can reject spurious temporal correlations.

### Stage 6 — Visualisation (`src/visualizer/graph_builder.py`)

A custom **BFS-based hierarchical layout** places root concepts (in-degree = 0) at the top and dependents progressively lower, so the graph can be read top-to-bottom as a learning path. Arrows always point **prerequisite → dependent**.

Three output formats are produced:
- **PNG** (`matplotlib`) — static high-resolution image for reports.
- **HTML** (`pyvis`) — interactive: zoom, drag, hover tooltips showing confidence and pedagogical rationale.
- **GraphML / DOT / JSON** — machine-readable formats for downstream processing.

---

## Output Structure

Each video produces a `{video_id}_complete_output.json` file with this structure:

```json
{
  "concepts": [
    {
      "id": "concept_1",
      "name": "Data Types",
      "description": "...",
      "importance": 4,
      "category": "fundamental",
      "is_valid": true,
      "validation_method": "groq_llm",
      "nlp_scores": {
        "keybert": 0.61,
        "np_frequency": 0.51,
        "temporal_position": 0.08,
        "combined": 0.53
      },
      "prerequisites": [
        { "id": "concept_2", "name": "Variables", "confidence": 0.91 }
      ],
      "enables": [
        { "id": "concept_5", "name": "Lists", "confidence": 0.84 }
      ]
    }
  ],
  "relationships": [
    {
      "source": "concept_2",
      "target": "concept_1",
      "confidence": 0.91,
      "strength": "strong",
      "relationship_type": "strict_prerequisite"
    }
  ]
}
```

**Rationale for the output structure:**

- **`prerequisites` and `enables` embedded in each concept** — a consumer can look up a single concept and immediately know what to teach before it and what it unlocks, without joining across the `relationships` array.
- **`validation_method` field** — transparency flag. `groq_llm` means the LLM confirmed the concept; `rule_based_free` means the API was unavailable and the concept passed only the NLP filter. Downstream consumers can choose to trust only LLM-validated concepts.
- **`nlp_scores` preserved** — allows debugging and re-ranking without re-running the full pipeline.
- **`strength` field on relationships** — `strong` (confidence > 0.85), `moderate` (> 0.70), `weak` (≥ 0.50) — lets UIs render edge weight visually without recomputing thresholds.
- **`relationship_type` field** — one of `strict_prerequisite` (must learn first), `recommended_prerequisite` (helpful but not mandatory), or `related` (connected concepts at similar level). Set by Groq Llama during prerequisite validation.

---

## Setup Instructions

### Prerequisites

- Python 3.9+
- `ffmpeg` (for audio extraction)
- A free [Groq API key](https://console.groq.com/) — the free tier (14,400 req/day, 500K tokens/day) is sufficient for all 5 videos.

### Install

```bash
git clone https://github.com/AnishRacherla/irel-nlp-task.git
cd irel-nlp-task
pip install -r requirements.txt
pip install -e .
python -m spacy download en_core_web_sm
```

On Linux, install ffmpeg:
```bash
sudo apt-get install -y ffmpeg
```

### Configure API key

Edit `config/config.yaml` and set your Groq API key:

```yaml
api_keys:
  groq_api_key: "gsk_..."
```

---

## Running in Google Colab (Recommended)

The notebook `irel_colab_notebook.ipynb` automates everything on a free T4 GPU.

1. Open the notebook in Colab.
2. Set `VIDEO_ID` in **cell 1** (`video_1` through `video_5`).
3. Run all cells top to bottom (Runtime → Run all).
4. **Cell 9** shows the interactive directed graph.
5. **Cell 10** downloads all outputs as a zip.

To process a different video after the first run: edit `VIDEO_ID` in cell 1 → re-run cell 7.

| Scenario | Cells to run |
|---|---|
| First time / new session | All cells (1 → 10) |
| After a code change | Cell 2 (pull) → Cell 7 (run) |
| Change video | Edit `VIDEO_ID` in cell 1 → Cell 7 |
| Process all 5 videos | Set `RUN_ALL = True` in cell 1 → Cell 7 |

---

## Running Locally

```bash
# Process a single video
python example_usage.py --video-id video_1

# Process all configured videos
python main.py --process-all
```

Outputs are written to:
```
outputs/
  graphs/          # JSON, GraphML, DOT files
  visualizations/  # PNG static graph, HTML interactive graph
```

---

## Configuration

All settings are in `config/config.yaml`. Key options:

| Section | Key | Default | Description |
|---|---|---|---|
| `transcription` | `whisper_model_size` | `large-v3` | Whisper model size (`tiny`, `base`, `small`, `medium`, `large-v3`) |
| `concept_extraction` | `groq_model` | `llama-3.3-70b-versatile` | Groq model for concept validation |
| `concept_extraction` | `max_concepts_per_video` | `20` | Maximum concepts to extract |
| `concept_extraction` | `min_concept_confidence` | `0.7` | Minimum score to keep a candidate |
| `prerequisite_mapping` | `confidence_threshold` | `0.6` | Minimum relationship confidence |
| `language_processing` | `primary_languages` | `[en, hi, ta, te, kn]` | Languages to handle in code-mixing |