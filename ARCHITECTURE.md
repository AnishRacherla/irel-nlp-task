# Architecture & Design Decisions

This document provides in-depth technical details about the system architecture and design decisions.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Module Design](#module-design)
3. [Data Flow](#data-flow)
4. [Design Decisions](#design-decisions)
5. [Performance Considerations](#performance-considerations)
6. [Scalability](#scalability)

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Configuration Layer                      │
│  (config.yaml, .env, ConfigLoader)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                    Pipeline Orchestrator                     │
│  (PedagogicalFlowPipeline)                                  │
│  - Manages workflow                                          │
│  - Coordinates modules                                       │
│  - Handles errors and logging                               │
└───┬──────┬─────────┬─────────┬──────────┬──────────────────┘
    │      │         │         │          │
    v      v         v         v          v
┌───────┐ ┌──────┐ ┌───────┐ ┌───────┐ ┌──────────┐
│Trans- │ │Code- │ │Concept│ │Prereq.│ │Visualiz- │
│criber │ │Mixed │ │Extract│ │Mapper │ │ation     │
│       │ │Proc. │ │       │ │       │ │          │
└───────┘ └──────┘ └───────┘ └───────┘ └──────────┘
    │        │         │         │          │
    v        v         v         v          v
┌─────────────────────────────────────────────────────────────┐
│                      Data Persistence                        │
│  (File system: JSON, GraphML, HTML, PNG)                    │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Patterns

1. **Pipeline Pattern**: Sequential processing stages with clear inputs/outputs
2. **Dependency Injection**: Modules receive configuration and dependencies
3. **Strategy Pattern**: Pluggable algorithms (e.g., different LLM providers)
4. **Factory Pattern**: Graph builder creates multiple output formats
5. **Singleton Pattern**: Logger and configuration management

## Module Design

### 1. Transcription Module

**Purpose**: Convert video/audio to text transcripts

**Components**:
- `VideoTranscriber`: Main class
  - `download_video()`: YouTube-DL integration
  - `transcribe_audio()`: Whisper integration
  - `process_video()`: Complete pipeline

**Technology Choice**:
- **Whisper**: Selected for multilingual capability and code-mixed robustness
- **yt-dlp**: Universal video downloader supporting 1000+ sites

**Design Decisions**:
- **Caching**: Transcripts cached to disk to avoid re-processing
- **Lazy Loading**: Whisper model loaded only when needed (memory efficiency)
- **Segmentation**: Preserves timestamps for temporal analysis

**Data Flow**:
```
Video URL → Download → Audio Extraction → Whisper → JSON Transcript
```

### 2. Code-Mixed Language Processor

**Purpose**: Standardize colloquial and code-mixed terminology

**Components**:
- `CodeMixedProcessor`: Main class
  - `detect_languages()`: Language identification
  - `identify_code_mixing()`: Code-mixing analysis
  - `standardize_terminology()`: Term mapping

**Methodology**:

1. **Detection Layer**:
   - langdetect for probabilistic language ID
   - Unicode range matching for Indic scripts
   - Confidence scoring

2. **Standardization Layer**:
   - LLM-based contextual mapping
   - Maintains original→standard mapping
   - Domain-aware standardization

**Example**:
```
Input:  "Hum array ko sort karenge using bubble sort"
Output: "We will sort the array using bubble sort"

Mapping: {
  "hum": "we",
  "ko": "the",
  "karenge": "will"
}
```

**Design Decisions**:
- **LLM over Dictionary**: Context-aware, handles unseen terms
- **Preserve Original**: Maintains both versions for transparency
- **Domain Awareness**: Standardization considers CS/Physics/etc. context

### 3. Concept Extractor

**Purpose**: Identify educational concepts from transcripts

**Components**:
- `ConceptExtractor`: Main class
  - `extract_concepts()`: LLM-based extraction
  - `refine_concepts()`: Deduplication and refinement
  - `categorize_concepts()`: Organize by difficulty

**Extraction Strategy**:

```python
Prompt Engineering Approach:
├── System Context: "You are an expert in {domain} education"
├── Task Description: "Extract core technical concepts"
├── Output Schema: JSON with structured concept data
└── Examples: Few-shot examples for consistency
```

**Concept Schema**:
```json
{
  "id": "concept_1",
  "name": "Binary Search",
  "description": "Algorithm for finding...",
  "importance": 4,           // 1-5 scale
  "keywords": [...],
  "time_segment": "early",   // Pedagogical flow
  "category": "fundamental"  // Difficulty level
}
```

**Design Decisions**:
- **Importance Scoring**: Enables prioritization
- **Temporal Tracking**: Preserves teaching sequence
- **Deduplication**: Removes similar concepts
- **Categorization**: Fundamental/Intermediate/Advanced

### 4. Prerequisite Mapper

**Purpose**: Establish dependency relationships between concepts

**Components**:
- `PrerequisiteMapper`: Main class
  - `map_prerequisites()`: Relationship extraction
  - `build_dependency_graph()`: Graph construction
  - `identify_foundational_concepts()`: Entry point detection

**Relationship Types**:

| Type | Meaning | Example |
|------|---------|---------|
| **strict_prerequisite** | A must precede B | Arrays → Sorting |
| **recommended_prerequisite** | A helps understand B | Math → Algorithms |
| **related** | A and B are related | Queues ↔ Stacks |
| **builds_on** | B extends A | Sorting → QuickSort |

**Graph Construction**:

```python
Graph Structure:
Nodes: {Concepts with metadata}
Edges: {Directed relationships with confidence scores}

Properties:
- Directed: Prerequisites have directionality
- Weighted: Confidence scores (0.0 - 1.0)
- Attributed: Rich metadata on nodes and edges
```

**Design Decisions**:
- **Flow-Based Analysis**: Uses teaching order, not just keywords
- **Confidence Scores**: Enables threshold-based filtering
- **Multiple Relationship Types**: Captures nuanced dependencies
- **Graph Representation**: Standard format for further analysis

### 5. Visualization Module

**Purpose**: Generate multiple output formats

**Components**:
- `GraphVisualizer`: Main class
  - `build_networkx_graph()`: Internal graph representation
  - `create_interactive_visualization()`: PyVis HTML
  - `create_static_visualization()`: Matplotlib PNG
  - `save_graphml() / save_dot()`: Standard formats

**Output Formats**:

1. **JSON**: Primary machine-readable format
2. **GraphML**: Compatible with Gephi, Cytoscape
3. **DOT**: GraphViz format
4. **Interactive HTML**: PyVis network visualization
5. **Static PNG**: High-resolution matplotlib output

**Visualization Features**:
- Color-coded by importance (red = high, green = low)
- Edge styles by relationship type (solid, dashed, dotted)
- Interactive hover for details
- Force-directed layout for clarity

## Data Flow

### Complete Pipeline Flow

```
1. Video Input
   ↓
2. Download & Extract Audio
   ↓ [MP3 file]
3. Transcribe (Whisper)
   ↓ [JSON: {text, segments, language}]
4. Language Analysis
   ↓ [Detected languages, code-mixing patterns]
5. Standardize Terminology
   ↓ [Standardized text + mappings]
6. Extract Concepts
   ↓ [List of concepts with metadata]
7. Map Prerequisites
   ↓ [Dependency graph structure]
8. Generate Visualizations
   ↓ [JSON, GraphML, HTML, PNG]
9. Save Outputs
   └→ [Multiple files in outputs/]
```

### Data Structures

**Transcript Object**:
```python
{
  "text": str,              # Full transcript
  "segments": [             # Timestamped segments
    {
      "start": float,
      "end": float,
      "text": str
    }
  ],
  "language": str           # Detected language
}
```

**Concept Object**:
```python
{
  "id": str,
  "name": str,
  "description": str,
  "importance": int,        # 1-5
  "keywords": [str],
  "time_segment": str,      # "early", "middle", "late"
  "category": str           # "fundamental", "intermediate", "advanced"
}
```

**Relationship Object**:
```python
{
  "source_id": str,
  "source_name": str,
  "target_id": str,
  "target_name": str,
  "relationship_type": str,  # Type of prerequisite
  "confidence": float,       # 0.0 - 1.0
  "reasoning": str           # Why this relationship exists
}
```

**Graph Object**:
```python
{
  "nodes": [Concept],
  "edges": [Relationship],
  "node_count": int,
  "edge_count": int,
  "statistics": {...}
}
```

## Design Decisions

### 1. Why LLMs for NLP Tasks?

**Decision**: Use GPT-4o-mini for concept extraction and prerequisite mapping

**Rationale**:
- **Context Understanding**: Better than rule-based or keyword approaches
- **Code-Mixing**: Handles mixed languages without separate models
- **Zero-Shot**: No training data required
- **Flexibility**: Easy to adapt to new domains
- **Quality**: State-of-the-art accuracy

**Trade-offs**:
- ✓ Pros: High quality, flexible, minimal engineering
- ✗ Cons: API costs, latency, requires internet

**Alternatives Considered**:
| Approach | Pros | Cons | Selected? |
|----------|------|------|-----------|
| Rule-based | Fast, cheap | Brittle, low accuracy | ❌ |
| spaCy NER | Fast, offline | Poor for code-mixed | ❌ |
| Custom Fine-tuned Model | Good accuracy | Requires training data | ❌ |
| **LLM (GPT)** | **High accuracy, flexible** | **API costs** | **✅** |

### 2. Why Whisper for Transcription?

**Decision**: OpenAI Whisper (medium model)

**Rationale**:
- **Multilingual**: 99 languages including Indic languages
- **Code-Mixing**: Handles mixed languages in single audio
- **Accuracy**: State-of-the-art (~95% WER on clean audio)
- **Open Source**: Free, runs locally
- **Timestamps**: Provides segment-level timing

**Model Size Selection**:
| Model | Size | Speed | Accuracy | Selected |
|-------|------|-------|----------|----------|
| Tiny | 39M | Fastest | 70% | ❌ |
| Base | 74M | Fast | 80% | ❌ |
| Small | 244M | Medium | 85% | ❌ |
| **Medium** | **769M** | **Moderate** | **95%** | **✅** |
| Large | 1550M | Slow | 98% | ❌ |

**Rationale**: Medium model offers best speed/accuracy trade-off for 10-minute videos.

### 3. Why Multi-Format Output?

**Decision**: Generate JSON, GraphML, DOT, HTML, and PNG outputs

**Rationale**:
- **JSON**: Primary format, easy to parse programmatically
- **GraphML/DOT**: Standard formats for graph analysis tools
- **Interactive HTML**: Best for human exploration and presentations
- **Static PNG**: Reports, papers, and documentation

**Design Philosophy**: "Generate once, use everywhere"

### 4. Why Caching Transcripts?

**Decision**: Cache transcripts and intermediate results

**Rationale**:
- **Performance**: Whisper transcription is slow (~2-3 min per video)
- **Cost**: Avoids redundant OpenAI API calls
- **Debugging**: Enables testing downstream modules independently
- **Reproducibility**: Same transcript for multiple runs

**Implementation**:
```python
if transcript_exists():
    return load_cached_transcript()
else:
    transcript = transcribe_video()
    cache_transcript(transcript)
    return transcript
```

### 5. Why Confidence Scores?

**Decision**: Include confidence scores on all relationships

**Rationale**:
- **Filtering**: Users can set their own thresholds
- **Quality Control**: Identify uncertain relationships
- **Transparency**: Show confidence in extracted knowledge
- **Tradeoffs**: Balance precision vs. recall

**Usage Example**:
```python
# High-confidence only (precision)
strict_prereqs = filter(lambda r: r.confidence > 0.8, relationships)

# Include moderate confidence (recall)
all_prereqs = filter(lambda r: r.confidence > 0.5, relationships)
```

## Performance Considerations

### Time Complexity

| Module | Complexity | Typical Time |
|--------|------------|--------------|
| Download | O(n) video length | 1-2 min |
| Transcription | O(n) audio length | 2-3 min |
| Language Processing | O(1) API calls | 20-30 sec |
| Concept Extraction | O(1) API calls | 15-20 sec |
| Prerequisite Mapping | O(c²) concepts | 20-30 sec |
| Visualization | O(n + e) graph | 5-10 sec |

**Total**: ~5-8 minutes per 10-minute video

### Memory Requirements

- **Whisper Model**: ~3 GB RAM (medium model)
- **Audio Buffer**: ~100 MB per 10-minute video
- **Transcript Data**: ~50 KB text
- **Graph Data**: ~500 KB for 20 concepts

**Recommended**: 8 GB RAM minimum

### Optimization Strategies

1. **Lazy Loading**: Load Whisper model only when needed
2. **Caching**: Cache transcripts and intermediate results
3. **Batch Processing**: Process multiple videos sequentially
4. **Model Selection**: Use smaller Whisper model if needed
5. **API Optimization**: Combine multiple LLM queries when possible

## Scalability

### Current Limitations

- **Sequential Processing**: Videos processed one at a time
- **Local Execution**: Single machine
- **LLM Rate Limits**: OpenAI API rate limits

### Scaling Strategies

**Horizontal Scaling** (Process Multiple Videos):
```python
# Option 1: Threading (I/O bound operations)
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process_video, vid) for vid in videos]

# Option 2: Multiprocessing (CPU bound operations)
with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_video, videos)

# Option 3: Distributed (Cloud)
# - Use AWS Lambda for serverless processing
# - Use Kubernetes for container orchestration
```

**Vertical Scaling** (Faster Processing):
- Use GPU for Whisper (10x faster)
- Use larger batch sizes
- Cache more aggressively

### Production Deployment

For production use:

1. **API Management**:
   - Rate limit handling
   - Retry logic with exponential backoff
   - Circuit breaker pattern

2. **Data Pipeline**:
   - Message queue (RabbitMQ, Kafka)
   - Workflow orchestration (Apache Airflow)
   - Distributed storage (S3, GCS)

3. **Monitoring**:
   - Metrics (Prometheus)
   - Logging (ELK stack)
   - Alerting (PagerDuty)

4. **Quality Assurance**:
   - Automated testing
   - Manual validation samples
   - Feedback loop for improvements

## Future Enhancements

### Technical Improvements

1. **Multi-Video Alignment**:
   - Compare concepts across videos
   - Build unified knowledge graph
   - Identify common teaching patterns

2. **Real-Time Processing**:
   - Stream transcription
   - Incremental concept extraction
   - Live visualization updates

3. **Fine-Tuned Models**:
   - Custom Whisper for Indian accents
   - Domain-specific concept extraction
   - Specialized prerequisite detection

4. **Advanced Visualization**:
   - 3D graph layouts
   - Temporal evolution of concepts
   - Difficulty progression paths

5. **Quality Metrics**:
   - Automatic quality scoring
   - Concept coverage analysis
   - Learning path validation

### Research Directions

- Automatic curriculum generation from video collections
- Personalized learning path recommendations
- Cross-lingual concept alignment
- Knowledge graph reasoning for missing prerequisites

---

This architecture is designed to be:
- **Modular**: Easy to replace/upgrade components
- **Extensible**: Add new features without breaking existing code
- **Maintainable**: Clear separation of concerns
- **Scalable**: Can grow from prototype to production

For questions about specific design decisions, see the [README](README.md) or open an issue.
