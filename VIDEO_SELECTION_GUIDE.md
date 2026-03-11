# Video Selection Guide

This guide will help you find and select appropriate code-mixed educational videos for the iREL recruitment task.

## Requirements Checklist

Your 5 videos should meet these criteria:

- [ ] **Duration**: Approximately 10 minutes each
- [ ] **Language**: Heavily code-mixed (e.g., Hinglish, Tamil-English, Telugu-English)
- [ ] **Domain**: Technical educational content (CS, Physics, Engineering)
- [ ] **Quality**: Clear audio, single speaker preferred
- [ ] **Accessibility**: Publicly available (YouTube, etc.)
- [ ] **Content**: Structured lesson with clear concept progression

## Recommended Sources

### 1. YouTube Channels (Code-Mixed CS Content)

**Hindi-English Channels**:
- Jenny's Lectures CS IT: https://www.youtube.com/@JennyslecturesCSIT
  - Topics: Data Structures, Algorithms, DBMS, Networks
  - Language: Hinglish
  - Example: "What is Binary Search Tree in Hindi"

- CodeWithHarry: https://www.youtube.com/@CodeWithHarry
  - Topics: Programming, Web Development, DSA
  - Language: Hinglish
  - Example: "Python Tutorial for Beginners in Hindi"

- Gate Smashers: https://www.youtube.com/@GateSmashers
  - Topics: Computer Science fundamentals
  - Language: Hinglish
  - Example: "Process Synchronization in Hindi"

**Tamil-English Channels**:
- CS Guru: https://www.youtube.com/@CSGuru1
  - Topics: Computer Science concepts
  - Language: Tamil-English mix

**Telugu-English Channels**:
- Sundeep Saradhi Kanthety: https://www.youtube.com/@SundeepSaradhiKanthety
  - Topics: Computer Science, Programming
  - Language: Telugu-English mix

### 2. Topic Suggestions

Good topics for concept dependency extraction:

**Computer Science**:
- Data Structures: Arrays → Linked Lists → Trees → Graphs
- Sorting Algorithms: Comparison → Bubble Sort → Quick Sort
- Object-Oriented Programming: Classes → Objects → Inheritance
- Database: Tables → Keys → Normalization → Joins
- Networking: OSI Model → TCP/IP → HTTP

**Physics**:
- Mechanics: Force → Motion → Energy → Momentum
- Electricity: Charge → Current → Voltage → Resistance
- Waves: Frequency → Wavelength → Amplitude → Wave Equation

**Mathematics**:
- Calculus: Functions → Limits → Derivatives → Integration
- Linear Algebra: Vectors → Matrices → Determinants → Eigenvalues

## How to Search

### YouTube Search Queries

**For Hinglish Content**:
```
"data structures in hindi"
"algorithms explained in hindi"
"computer networks hindi"
"DBMS tutorial hindi"
"operating system in hindi"
```

**For Tamil-English**:
```
"computer science tamil"
"programming tamil"
"data structures tamil"
```

**For Telugu-English**:
```
"computer science telugu"
"programming tutorial telugu"
"data structures telugu"
```

### Filtering Tips

1. **Duration Filter**: Use YouTube filters → Duration → 10-20 minutes
2. **View Count**: Higher views often indicate better quality
3. **Recent**: Newer videos typically have better audio quality
4. **Comments**: Check comments to verify language mix
5. **Preview**: Watch first 2 minutes to verify code-mixing level

## Evaluation Criteria

Rate each video on these dimensions before selecting:

### 1. Code-Mixing Level (Required: High)

- ✅ **High**: Frequent switching between languages (ideal)
  - Example: "Hum ek array create karenge with integers"
  
- ⚠️ **Medium**: Occasional mixing (acceptable)
  - Example: Mostly Hindi with English technical terms
  
- ❌ **Low**: Mostly one language (not suitable)
  - Example: Pure Hindi or pure English

### 2. Technical Depth (Required: Moderate to High)

- ✅ **Good**: Clear concept progression with prerequisites
  - Example: Explains arrays before discussing sorting
  
- ⚠️ **Okay**: Some concepts but limited depth
  
- ❌ **Poor**: Too basic or too fragmented

### 3. Audio Quality (Required: Clear)

- ✅ **Clear**: Easy to understand, minimal background noise
- ⚠️ **Acceptable**: Some noise but intelligible
- ❌ **Poor**: Heavy noise, hard to understand

### 4. Structure (Preferred: Well-organized)

- ✅ **Structured**: Clear introduction → explanation → examples → conclusion
- ⚠️ **Moderate**: Some structure but jumps around
- ❌ **Unstructured**: Random flow

## Sample Video Selection Template

Use this template for documenting your selected videos:

```yaml
video_1:
  # Basic Info
  url: "https://youtube.com/watch?v=..."
  title: "Binary Search Tree Explained in Hindi"
  channel: "Jenny's Lectures CS IT"
  duration_minutes: 12
  
  # Language Info
  language: "Hindi-English"
  primary_language: "Hindi"
  code_mixing_level: "High"  # High/Medium/Low
  example_phrases:
    - "Node create karenge"
    - "Left subtree mein smaller values honge"
  
  # Content Info
  domain: "Computer Science"
  topic: "Data Structures"
  subtopic: "Binary Search Trees"
  concepts_preview:
    - "Binary Tree basics"
    - "Search property"
    - "Insertion algorithm"
    - "Node structure"
  
  # Quality Metrics
  audio_quality: "Clear"
  teaching_style: "Structured"
  difficulty_level: "Intermediate"
  
  # Why This Video?
  selection_reason: |
    - Heavy code-mixing between Hindi and English
    - Clear concept progression (trees → binary trees → BST)
    - Well-structured lesson with examples
    - Good audio quality
    - Strong prerequisite relationships to extract
```

## Diversity Recommendations

For a strong submission, aim for diversity:

### Language Diversity
- ✅ 2-3 different code-mixed language pairs
- Example: 2 Hinglish + 1 Tamil-English + 1 Telugu-English + 1 Kannada-English

### Topic Diversity
- ✅ Different but related topics
- Example:
  1. Arrays (fundamental)
  2. Sorting Algorithms (builds on arrays)
  3. Recursion (independent concept)
  4. Trees (intermediate)
  5. Graph Traversal (advanced)

### Difficulty Diversity
- ✅ Mix of fundamental, intermediate, and advanced
- 2 fundamental + 2 intermediate + 1 advanced

## Red Flags to Avoid

❌ **Don't Select Videos That**:
- Have multiple speakers talking over each other
- Are pure tutorial recordings (no explanation)
- Have music/sound effects drowning out speech
- Are in pure English or pure Indic language (minimal mixing)
- Jump between unrelated topics
- Are lectures with student questions (hard to parse)
- Have poor audio quality (can't transcribe accurately)
- Violate copyright (use only publicly available content)

## Example Selection (Hypothetical)

Here's what a good selection might look like:

| # | Topic | Language | Difficulty | Reason |
|---|-------|----------|----------|--------|
| 1 | Arrays Basics | Hinglish | Fundamental | Foundation for DS |
| 2 | Binary Search | Hinglish | Intermediate | Builds on arrays |
| 3 | Recursion | Tamil-English | Intermediate | Different language |
| 4 | Linked Lists | Telugu-English | Intermediate | Another language |
| 5 | Binary Trees | Hinglish | Advanced | Complex prerequisites |

**Rationale**: 
- 3 different language pairs ✓
- Clear prerequisite flow ✓
- Mix of difficulty levels ✓
- All ~10 minutes ✓
- Technical depth ✓

## Verification Checklist

Before finalizing your selection, verify:

- [ ] All 5 videos are publicly accessible
- [ ] Each is approximately 10 minutes (8-15 min acceptable)
- [ ] Code-mixing is clearly present in all videos
- [ ] You can understand the audio reasonably well
- [ ] Topics have clear concept relationships
- [ ] At least 2 different code-mixed language pairs
- [ ] You've noted the exact time where concepts are introduced
- [ ] URLs are direct links (not playlists)
- [ ] Videos are downloadable (test with yt-dlp)

## Testing Video Selection

Before committing, test one video through the pipeline:

```bash
# Test single video
python main.py --video-id test_video \
    --url "https://youtube.com/watch?v=..." \
    --language "Hindi-English" \
    --domain "Computer Science"
```

Check:
- ✓ Transcription worked correctly
- ✓ Code-mixing detected
- ✓ Reasonable number of concepts extracted (5-15)
- ✓ Prerequisites make sense
- ✓ Visualization looks meaningful

## Pro Tips

1. **Start with popular channels**: They typically have better production quality

2. **Look for series**: Videos in a series often have better prerequisite flow
   - Example: "Data Structures Series Part 3: Binary Search"

3. **Check upload date**: Recent videos often have better audio quality

4. **Preview captions**: If auto-captions exist, review them for quality

5. **Watch at 1.5x speed**: Quickly assess if the video is suitable

6. **Document as you go**: Fill in the YAML template while selecting

7. **Have backups**: Select 7-8 videos, use best 5

## Final Recommendation

**Prioritize**:
1. Code-mixing level (most important for task)
2. Clear concept progression (prerequisite relationships)
3. Audio quality (affects transcription)
4. Technical depth (meaningful concepts)
5. Language diversity (shows robustness)

**Don't worry too much about**:
- Minor background noise
- Occasional stumbles by speaker
- Exact 10-minute duration (8-15 is fine)
- Perfect structure (real-world content is messy)

## Need Help?

If you're struggling to find videos:

1. Start with Jenny's Lectures (very popular Hinglish CS content)
2. Search for "explain in hindi" + your target topic
3. Browse channel playlists for structured series
4. Check video descriptions for timeline (shows structure)
5. Look at recommended videos from good ones you find

---

**Remember**: The goal is to demonstrate your pipeline's robustness on real, messy, code-mixed content. Don't spend too long finding "perfect" videos—find good ones and let your pipeline handle the complexity!
