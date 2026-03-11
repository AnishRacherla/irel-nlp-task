"""
Concept extraction module (Hybrid Approach)
Uses KeyBERT (full text, GPU) + NP extraction + Embeddings + Groq LLM validation
"""

from typing import Dict, List, Any, Tuple
import json
from collections import Counter
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from groq import Groq


class HybridConceptExtractor:
    """Extract technical concepts using hybrid NLP + LLM approach"""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize hybrid concept extractor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.groq_api_key = config.get('api_keys', {}).get('groq_api_key', '')
        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None
        self.groq_model = config.get('concept_extraction', {}).get('groq_model', 'llama-3.3-70b-versatile')
        
        # Initialize models
        self.keybert_model = None
        self.embedding_model = None
    
    def _load_models(self):
        """Load KeyBERT and embedding models lazily (uses GPU if available)"""
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.logger.info(f"Loading models on device: {device}")

        if self.embedding_model is None:
            self.logger.info("Loading sentence transformer model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            self.logger.info("Sentence transformer loaded")

        if self.keybert_model is None:
            self.logger.info("Loading KeyBERT model (full text, GPU-accelerated)...")
            self.keybert_model = KeyBERT(model=self.embedding_model)
            self.logger.info("KeyBERT loaded")
    
    def extract_keywords_keybert(self, text: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Extract keywords from the FULL text using KeyBERT (GPU-accelerated).
        Previously limited to noun phrases only due to runtime; GPU removes that constraint.

        Args:
            text: Full input text
            top_n: Number of keywords to extract

        Returns:
            List of (keyword, score) tuples
        """
        if not text.strip():
            return []

        self._load_models()
        self.logger.info("Extracting KeyBERT keywords from full text...")

        # Use n-gram range 1-3 on the complete text; MMR ensures diversity
        keywords = self.keybert_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words='english',
            use_mmr=True,
            diversity=0.5,
            top_n=top_n,
        )
        self.logger.info(f"KeyBERT extracted {len(keywords)} keywords from full text")
        return keywords
    
    def extract_noun_phrases(self, noun_phrases: List[str]) -> List[Tuple[str, float]]:
        """
        Process noun phrases with INTELLIGENT filtering (technical term detection)
        
        Args:
            noun_phrases: List of noun phrases from preprocessing
        
        Returns:
            List of (noun_phrase, frequency_score) tuples
        """
        # Expanded blacklist of generic/filler phrases and words
        blacklist_phrases = {
            'today', 'session', 'today\'s session', 'first step', 'next step',
            'lot', 'example', 'concept', 'concepts', 'these concepts',
            'thing', 'things', 'way', 'mind', 'our mind', 'time',
            'video', 'playlist', 'channel', 'tool', 'beginner', 'beginners',
            'web development', 'hello everyone', 'thank you',
            # NEW: Remove generic learning/journey phrases
            'learning journey', 'our journey', 'your journey', 'this learning',
            'our learning', 'your learning', 'programming journey',
            'enough python', 'intermediate python'
        }
        
        blacklist_words = {
            'today', 'tomorrow', 'yesterday', 'session', 'video', 'playlist',
            'channel', 'everyone', 'guys', 'basically', 'simply', 'just',
            'okay', 'alright', 'hello', 'welcome', 'thank', 'thanks',
            # NEW: Filter journey/learning as single words
            'journey', 'learning', 'area', 'point', 'work', 'what'
        }
        
        # Technical indicators (suggests educational concept)
        technical_patterns = [
            lambda w: w[0].isupper() and len(w) > 3,  # Capitalized technical terms
            lambda w: w.lower() in ['python', 'java', 'javascript', 'algorithm', 'data', 'structure',
                                     'machine', 'learning', 'neural', 'network', 'database', 'query',
                                     'binary', 'tree', 'graph', 'array', 'list', 'stack', 'queue',
                                     'sort', 'search', 'hash', 'table', 'api', 'server', 'client'],
        ]
        
        # Count frequencies
        phrase_counts = Counter(np.lower() for np in noun_phrases)
        
        # Normalize scores
        max_count = max(phrase_counts.values()) if phrase_counts else 1
        
        # INTELLIGENT filtering
        scored_phrases = []
        for phrase, count in phrase_counts.items():
            words = phrase.split()
            phrase_lower = phrase.lower()
            
            # Basic filters
            if len(words) < 2 or len(words) > 4:  # 2-4 words
                continue
            if phrase_lower in blacklist_phrases:  # Exact blacklist match
                continue
            if any(word.lower() in blacklist_words for word in words):  # Any blacklisted word
                continue
            if len(phrase) < 6:  # Too short
                continue
                
            # Quality scoring
            base_score = count / max_count
            
            # Boost score for technical indicators
            technical_boost = 0
            for word in words:
                for pattern in technical_patterns:
                    try:
                        if pattern(word):
                            technical_boost += 0.3
                            break
                    except:
                        pass
            
            # Boost for compound nouns (noun+noun patterns are usually technical)
            if len(words) >= 2 and words[0][0].islower() and words[1][0].islower():
                technical_boost += 0.2
            
            # Boost for mixed case (e.g., "Python Programming")
            if any(w[0].isupper() for w in words) and len(words) >= 2:
                technical_boost += 0.2
            
            final_score = base_score + technical_boost
            scored_phrases.append((phrase, final_score))
        
        # Sort by score
        sorted_phrases = sorted(scored_phrases, key=lambda x: x[1], reverse=True)
        
        # DEDUPLICATION: Remove similar/duplicate concepts
        deduplicated = []
        
        # Helper to strip common articles for better deduplication
        def strip_articles(phrase):
            words = phrase.lower().split()
            if words and words[0] in ['the', 'a', 'an', 'our', 'this', 'that', 'these', 'those', 'your', 'my']:
                return ' '.join(words[1:])
            return phrase.lower()
        
        # Helper to normalize plurals
        def normalize_plural(text):
            # Simple singular form (remove trailing 's')
            return text.rstrip('s') if text.endswith('s') and len(text) > 3 else text
        
        for phrase, score in sorted_phrases:
            # Check if similar concept already exists
            is_duplicate = False
            phrase_normalized = strip_articles(phrase)
            
            # Skip if too short after stripping articles
            if len(phrase_normalized) < 3:
                continue
            
            phrase_words = set(phrase_normalized.split())
            phrase_singular = normalize_plural(phrase_normalized)
            
            for existing_phrase, _ in deduplicated:
                existing_normalized = strip_articles(existing_phrase)
                existing_words = set(existing_normalized.split())
                existing_singular = normalize_plural(existing_normalized)
                
                # Check 1: Substring match (one phrase contains the other)
                if phrase_normalized in existing_normalized or existing_normalized in phrase_normalized:
                    is_duplicate = True
                    break
                
                # Check 2: Plural/singular match
                if phrase_singular == existing_singular:
                    is_duplicate = True
                    break
                
                # Check 3: Word overlap (70%+ words in common)
                overlap = len(phrase_words & existing_words) / max(len(phrase_words), len(existing_words))
                if overlap > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append((phrase, score))
            
            if len(deduplicated) >= 20:  # Stop at 20 unique concepts
                break
        
        self.logger.info(f"Deduplicated to {len(deduplicated)} unique concepts (from {len(phrase_counts)} total)")
        return deduplicated
    
    def cluster_concepts_by_similarity(self, concepts: List[str], threshold: float = 0.7) -> List[List[str]]:
        """
        Cluster similar concepts using embeddings
        
        Args:
            concepts: List of concept strings
            threshold: Similarity threshold for clustering
        
        Returns:
            List of concept clusters
        """
        if not concepts:
            return []
        
        self._load_models()
        
        # Get embeddings
        embeddings = self.embedding_model.encode(concepts)
        
        # Compute similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        # Simple clustering: group similar concepts
        used = set()
        clusters = []
        
        for i, concept in enumerate(concepts):
            if i in used:
                continue
            
            cluster = [concept]
            used.add(i)
            
            for j in range(i + 1, len(concepts)):
                if j not in used and similarity_matrix[i][j] > threshold:
                    cluster.append(concepts[j])
                    used.add(j)
            
            clusters.append(cluster)
        
        self.logger.info(f"Clustered {len(concepts)} concepts into {len(clusters)} groups")
        return clusters
    
    def merge_and_rank_concepts(self, keybert_keywords: List[Tuple[str, float]], 
                                noun_phrases: List[Tuple[str, float]],
                                segmented_sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Merge concepts from multiple sources and rank
        
        Args:
            keybert_keywords: Keywords from KeyBERT
            noun_phrases: Noun phrases from spaCy
            segmented_sentences: List of sentences for temporal analysis
        
        Returns:
            Ranked list of concept candidates
        """
        # Combine all concepts
        all_concepts = {}
        
        # Add KeyBERT keywords
        for keyword, score in keybert_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in all_concepts:
                all_concepts[keyword_lower] = {
                    'name': keyword,
                    'keybert_score': score,
                    'np_score': 0.0,
                    'temporal_position': 0.5  # default middle
                }
        
        # Add noun phrases
        for phrase, score in noun_phrases:
            phrase_lower = phrase.lower()
            if phrase_lower in all_concepts:
                all_concepts[phrase_lower]['np_score'] = score
            else:
                all_concepts[phrase_lower] = {
                    'name': phrase,
                    'keybert_score': 0.0,
                    'np_score': score,
                    'temporal_position': 0.5
                }
        
        # Determine temporal position
        num_sentences = len(segmented_sentences)
        for concept_key, concept_data in all_concepts.items():
            # Find first occurrence
            for idx, sentence in enumerate(segmented_sentences):
                if concept_data['name'].lower() in sentence.lower():
                    concept_data['temporal_position'] = idx / max(num_sentences, 1)
                    break
        
        # Calculate combined score
        for concept_data in all_concepts.values():
# Weighted combination: Prefer KeyBERT if available, otherwise NP
            if concept_data['keybert_score'] > 0:
                combined_score = (
                    concept_data['keybert_score'] * 0.7 +
                    concept_data['np_score'] * 0.2 +
                    (1 - concept_data['temporal_position']) * 0.1
                )
            else:
                combined_score = (
                    concept_data['np_score'] * 0.8 +
                    (1 - concept_data['temporal_position']) * 0.2
                )
            concept_data['combined_score'] = combined_score
        
        # Sort by combined score and take top candidates
        ranked_concepts = sorted(all_concepts.values(), key=lambda x: x['combined_score'], reverse=True)
        
        # Keep top 20 with minimum threshold
        filtered = [c for c in ranked_concepts if c['combined_score'] > 0.15][:20]
        
        self.logger.info(f"Merged and ranked {len(filtered)} concept candidates")
        return filtered
    
    def llm_validate_concepts(self, concept_candidates: List[Dict[str, Any]], 
                             text: str, domain: str = "Computer Science") -> List[Dict[str, Any]]:
        """
        Validate and enrich concepts using Groq LLM (free).
        Falls back to rule-based validation if no API key is configured.

        Args:
            concept_candidates: List of concept candidates from NLP extraction
            text: Original text
            domain: Academic domain

        Returns:
            Validated and enriched concepts
        """
        if not self.groq_client:
            self.logger.warning("No Groq API key configured — falling back to rule-based validation")
            return self._fallback_concepts(concept_candidates[:15])

        self.logger.info(f"Validating concepts with Groq ({self.groq_model})...")

        candidate_names = [c['name'] for c in concept_candidates[:20]]
        prompt = f"""You are an expert in {domain} education and curriculum design.

Below is a list of candidate concepts extracted from an educational transcript, followed by a short excerpt of that transcript.

Candidate concepts:
{json.dumps(candidate_names, indent=2)}

Transcript excerpt (first 3000 chars):
{text[:3000]}

Your tasks:
1. Keep only genuine educational concepts relevant to the transcript.
2. Remove generic/filler words that are not real concepts.
3. For each kept concept provide a brief description, importance (1-5), category (fundamental/intermediate/advanced), and 2-4 keywords/aliases.

Respond ONLY with valid JSON in exactly this format:
{{
    "concepts": [
        {{
            "id": "concept_1",
            "name": "Concept Name",
            "description": "Brief description",
            "importance": 4,
            "category": "fundamental|intermediate|advanced",
            "keywords": ["keyword1", "keyword2"],
            "is_valid": true,
            "validation_method": "groq_llm"
        }}
    ]
}}"""

        try:
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "system", "content": "You are an expert in educational content analysis. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            concepts = result.get('concepts', [])
            # Re-number IDs
            for i, c in enumerate(concepts):
                c['id'] = f"concept_{i+1}"
            self.logger.info(f"Groq validated {len(concepts)} concepts")
            return concepts
        except Exception as e:
            self.logger.error(f"Groq validation failed: {e} — falling back to rule-based")
            return self._fallback_concepts(concept_candidates[:15])
    
    def _fallback_concepts(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rule-based concept validation (completely free)"""
        concepts = []
        
        # Filter out low-quality concepts using rules
        for idx, candidate in enumerate(candidates):
            name = candidate['name'].strip()
            
            # Skip if too short or too long
            if len(name) < 3 or len(name) > 100:
                continue
            
            # Skip if all lowercase common words
            if name.lower() in ['the', 'this', 'that', 'these', 'those', 'and', 'or', 'but']:
                continue
            
            # Determine category based on temporal position
            temporal_pos = candidate['temporal_position']
            if temporal_pos < 0.33:
                category = 'fundamental'
            elif temporal_pos < 0.67:
                category = 'intermediate'
            else:
                category = 'advanced'
            
            # Calculate importance
            importance = min(5, max(1, int(candidate['combined_score'] * 5) + 1))
            
            concepts.append({
                'id': f"concept_{len(concepts)+1}",
                'name': name.title(),
                'description': f"Educational concept: {name}",
                'importance': importance,
                'category': category,
                'is_valid': True,
                'validation_method': 'rule_based_free',
                'nlp_scores': {
                    'keybert': candidate['keybert_score'],
                    'np_frequency': candidate['np_score'],
                    'temporal_position': candidate['temporal_position'],
                    'combined': candidate['combined_score']
                }
            })
        
        self.logger.info(f"Rule-based validation: {len(concepts)} concepts (FREE)")
        return concepts
    
    def extract_and_validate(self, text: str, preprocessing_data: Dict[str, Any], 
                            domain: str = "Computer Science") -> Dict[str, Any]:
        """
        Complete hybrid extraction pipeline
        
        Args:
            text: Standardized text
            preprocessing_data: Output from preprocessing module
            domain: Academic domain
        
        Returns:
            Extracted and validated concepts
        """
        self.logger.info("Starting hybrid concept extraction")
        
        # Signal 1: KeyBERT keywords
        self.logger.info("Signal 1: Extracting KeyBERT keywords...")
        keybert_keywords = self.extract_keywords_keybert(text)
        
        # Signal 2: Noun phrases from preprocessing
        self.logger.info("Signal 2: Processing noun phrases...")
        noun_phrases = self.extract_noun_phrases(preprocessing_data.get('noun_phrases', []))
        
        # Signal 3: Merge and rank
        self.logger.info("Signal 3: Merging and ranking concepts...")
        concept_candidates = self.merge_and_rank_concepts(
            keybert_keywords, 
            noun_phrases,
            preprocessing_data.get('sentences', [])
        )
        
        # Signal 4: LLM validation (FREE mode: rule-based)
        self.logger.info("Signal 4: Validating concepts...")
        validated_concepts = self.llm_validate_concepts(concept_candidates, text, domain)
        
        return {
            'concepts': validated_concepts,
            'total_concepts': len(validated_concepts),
            'domain': domain,
            'extraction_statistics': {
                'keybert_keywords': len(keybert_keywords),
                'noun_phrases': len(noun_phrases),
                'candidates_generated': len(concept_candidates),
                'concepts_validated': len(validated_concepts)
            }
        }
