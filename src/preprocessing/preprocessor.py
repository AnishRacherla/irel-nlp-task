"""
Text preprocessing module
Handles sentence segmentation, tokenization, and POS tagging
"""

from typing import Dict, List, Any
import re
import spacy
import nltk
from nltk.corpus import stopwords


class TextPreprocessor:
    """Preprocess transcript text using NLP tools"""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize text preprocessor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.nlp = None
        self.stopwords = set()
        
        # Download required NLTK data
        self._download_nltk_data()
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            self.stopwords = set(stopwords.words('english'))
        except Exception as e:
            self.logger.warning(f"Could not download NLTK data: {str(e)}")
    
    def _load_spacy_model(self):
        """Load spaCy model lazily"""
        if self.nlp is None:
            try:
                self.logger.info("Loading spaCy model...")
                self.nlp = spacy.load('en_core_web_sm')
                self.logger.info("spaCy model loaded successfully")
            except OSError:
                self.logger.warning("spaCy model not found. Downloading...")
                import os
                os.system("python -m spacy download en_core_web_sm")
                self.nlp = spacy.load('en_core_web_sm')
    
    def segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into sentences
        
        Args:
            text: Input text
        
        Returns:
            List of sentences
        """
        self._load_spacy_model()
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        return sentences
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
        
        Returns:
            List of tokens
        """
        self._load_spacy_model()
        doc = self.nlp(text)
        tokens = [token.text for token in doc if not token.is_space]
        return tokens
    
    def pos_tag(self, text: str) -> List[tuple]:
        """
        POS tagging for text
        
        Args:
            text: Input text
        
        Returns:
            List of (token, pos_tag) tuples
        """
        self._load_spacy_model()
        doc = self.nlp(text)
        pos_tags = [(token.text, token.pos_) for token in doc]
        return pos_tags
    
    def extract_noun_phrases(self, text: str) -> List[str]:
        """
        Extract noun phrases from text
        
        Args:
            text: Input text
        
        Returns:
            List of noun phrases
        """
        self._load_spacy_model()
        doc = self.nlp(text)
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        return noun_phrases
    
    def remove_filler_words(self, text: str) -> str:
        """
        Remove common filler words
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        filler_words = ['um', 'uh', 'er', 'ah', 'like', 'you know', 'basically', 'actually']
        
        # Create pattern for filler words
        pattern = r'\b(' + '|'.join(re.escape(word) for word in filler_words) + r')\b'
        cleaned = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def analyze_dependencies(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze grammatical dependencies
        
        Args:
            text: Input text
        
        Returns:
            List of dependency relationships
        """
        self._load_spacy_model()
        doc = self.nlp(text)
        
        dependencies = []
        for token in doc:
            dep_info = {
                'text': token.text,
                'dep': token.dep_,
                'head': token.head.text,
                'pos': token.pos_,
                'children': [child.text for child in token.children]
            }
            dependencies.append(dep_info)
        
        return dependencies
    
    def find_cue_phrases(self, text: str) -> List[Dict[str, Any]]:
        """
        Find prerequisite cue phrases in text
        
        Args:
            text: Input text
        
        Returns:
            List of cue phrases with context
        """
        # Prerequisite cue phrases
        cue_patterns = {
            'prerequisite': [
                r'before (?:understanding |learning |studying )?([^,.]+)',
                r'requires? (?:knowledge of |understanding of )?([^,.]+)',
                r'needs? (?:to know |to understand )?([^,.]+)',
                r'must (?:know |understand |learn )([^,.]+) (?:before|first)',
                r'should (?:know |understand |learn )([^,.]+) (?:before|first)',
                r'after (?:understanding |learning )([^,.]+)',
                r'builds? (?:on |upon )([^,.]+)',
                r'extends? ([^,.]+)',
                r'based on ([^,.]+)',
                r'depends? on ([^,.]+)'
            ]
        }
        
        cue_matches = []
        
        for cue_type, patterns in cue_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    cue_matches.append({
                        'type': cue_type,
                        'pattern': pattern,
                        'match': match.group(0),
                        'concept': match.group(1).strip(),
                        'position': match.start()
                    })
        
        return cue_matches
    
    def preprocess(self, text: str) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with all preprocessing results
        """
        self.logger.info("Preprocessing text...")
        
        # Clean filler words
        cleaned_text = self.remove_filler_words(text)
        
        # Segment sentences
        sentences = self.segment_sentences(cleaned_text)
        
        # Tokenize
        tokens = self.tokenize(cleaned_text)
        
        # POS tagging
        pos_tags = self.pos_tag(cleaned_text)
        
        # Extract noun phrases
        noun_phrases = self.extract_noun_phrases(cleaned_text)
        
        # Find cue phrases
        cue_phrases = self.find_cue_phrases(cleaned_text)
        
        # Analyze dependencies (on first few sentences for efficiency)
        sample_text = ' '.join(sentences[:10]) if len(sentences) > 10 else cleaned_text
        dependencies = self.analyze_dependencies(sample_text)
        
        result = {
            'original_text': text,
            'cleaned_text': cleaned_text,
            'sentences': sentences,
            'tokens': tokens,
            'pos_tags': pos_tags,
            'noun_phrases': noun_phrases,
            'cue_phrases': cue_phrases,
            'dependencies': dependencies,
            'statistics': {
                'sentence_count': len(sentences),
                'token_count': len(tokens),
                'noun_phrase_count': len(noun_phrases),
                'cue_phrase_count': len(cue_phrases)
            }
        }
        
        self.logger.info(f"Preprocessing complete. Sentences: {len(sentences)}, "
                        f"Tokens: {len(tokens)}, NPs: {len(noun_phrases)}, "
                        f"Cues: {len(cue_phrases)}")
        
        return result
