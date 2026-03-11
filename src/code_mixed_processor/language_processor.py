"""
Code-mixed language processing module (Hybrid Approach)
Three-stage normalization: Dictionary → Translation → LLM Refinement
"""

from typing import Dict, List, Any, Tuple
import re
from langdetect import detect_langs
import openai
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False


class CodeMixedProcessor:
    """Process and standardize code-mixed educational content using hybrid approach"""
    
    # Dictionary of common Telugu-English code-mixed terms
    TELUGU_DICT = {
        # Common verbs
        'cheyyi': 'do', 'cheyyandi': 'do', 'chesthanu': 'will do', 'chesanu': 'did',
        'chesthunna': 'doing', 'chesthunnanu': 'doing', 'chesthunnaru': 'doing',
        'cheyyali': 'must do', 'cheyyandi': 'please do', 'chesthunnamu': 'we are doing',
        'undhi': 'is', 'undi': 'is', 'unnai': 'is', 'unnayi': 'are',
        'avutundi': 'will be', 'ayyindi': 'became', 'avthundi': 'will be',
        'chudandi': 'see', 'choodalem': 'can see', 'chusthanu': 'will see',
        'artham': 'understand', 'arthamaindi': 'understood', 'ardhamavutundi': 'will understand',
        'chesanu': 'did', 'chestham': 'we do', 'chestunnaru': 'you are doing',
        'kavali': 'need', 'kavalenu': 'don\'t need', 'kavalsindi': 'needed',
        'randi': 'come', 'vacchaanu': 'will come', 'vellani': 'let\'s go',
        'pettandi': 'put', 'pettochu': 'can put', 'pettali': 'must put',
        'teesuko': 'take', 'teesukovachu': 'can take', 'teesukovali': 'must take',
        'ivvandi': 'give', 'ichchanu': 'gave', 'istham': 'will give',
        
        # Common prepositions
        'lo': 'in', 'ki': 'to', 'nundi': 'from', 'tho': 'with', 'kosam': 'for',
        'varaku': 'until', 'daggara': 'near', 'pai': 'on', 'lagga': 'with',
        
        # Common pronouns
        'memu': 'we', 'meemu': 'we', 'nenu': 'I', 'neenu': 'I',
        'meeru': 'you', 'miru': 'you', 'idi': 'this', 'idhi': 'this',
        'adi': 'that', 'adhi': 'that', 'evaru': 'who', 'ekkada': 'where',
        'ela': 'how', 'enta': 'how much', 'eppudu': 'when',
        
        # Common adjectives
        'manchidi': 'good', 'manchidhi': 'good', 'baagundi': 'good',
        'cheddha': 'bad', 'pedda': 'big', 'chinna': 'small',
        'kotha': 'new', 'kotha': 'new', 'patha': 'old',
        'modati': 'first', 'modatidi': 'first', 'rendu': 'second',
        
        # Common conjunctions
        'mariyu': 'and', 'kani': 'but', 'ayithe': 'if', 'ante': 'means',
        'kaabatti': 'because', 'kuda': 'also', 'leda': 'or',
        
        # Technical/coding terms Telugu
        'anni': 'all', 'antha': 'all', 'konni': 'some', 'okati': 'one',
        'rendu': 'two', 'moodu': 'three', 'naalugu': 'four', 'aidhu': 'five',
        'program': 'program', 'code': 'code', 'coding': 'coding',
        'problem': 'problem', 'problemu': 'problem',
        'example': 'example', 'time': 'time', 'start': 'start',
        'mistakes': 'mistakes', 'mistake': 'mistake',
        'correct': 'correct', 'hash': 'hash', 'map': 'map', 'mapper': 'mapper',
        'data': 'data', 'structure': 'structure',
        'array': 'array', 'list': 'list', 'class': 'class',
        'das': 'this', 'dss': 'this', 'mankamat': 'moment',
        # Additional video-specific terms
        'nankamatruin': 'nunc pro tunc', 'chaisaanne': 'doing',
        'stahtchetharur': 'structure', 'kani': 'but',
        'tho': 'with', 'ante': 'means', 'par': 'for',
        'la': '', 'lla': '',  # Remove filler syllables
        
        # Common phrases
        'chala': 'very', 'koncham': 'little', 'baaga': 'very',
        'assalu': 'not at all', 'andhuke': 'that\'s why',
    }
    
    # Dictionary of common Hindi-English code-mixed terms
    HINGLISH_DICT = {
        # Common verbs
        'karna': 'do', 'karenge': 'will do', 'karte': 'do', 'karta': 'does',
        'hona': 'be', 'hai': 'is', 'ho': 'be', 'hoga': 'will be', 'honge': 'will be',
        'dekhna': 'see', 'dekho': 'see', 'dekhenge': 'will see',
        'samajhna': 'understand', 'samjho': 'understand', 'samajhenge': 'will understand',
        'banana': 'make', 'banate': 'make', 'banayenge': 'will make',
        'lena': 'take', 'lo': 'take', 'lete': 'take', 'lenge': 'will take',
        'dena': 'give', 'do': 'give', 'dete': 'give', 'denge': 'will give',
        'aana': 'come', 'aata': 'comes', 'aayega': 'will come',
        'jaana': 'go', 'jata': 'goes', 'jayega': 'will go',
        'rakhna': 'keep', 'rakho': 'keep', 'rakhenge': 'will keep',
        'milna': 'get', 'milega': 'will get', 'milte': 'get',
        
        # Common prepositions
        'mein': 'in', 'me': 'in', 'par': 'on', 'ke': 'of', 'ka': 'of', 'ki': 'of',
        'se': 'from', 'ko': 'to', 'tak': 'until',
        
        # Common pronouns
        'hum': 'we', 'main': 'I', 'tum': 'you', 'aap': 'you',
        'yeh': 'this', 'ye': 'this', 'woh': 'that', 'wo': 'that',
        'yahan': 'here', 'wahan': 'there', 'kahan': 'where',
        
        # Common adverbs
        'ab': 'now', 'phir': 'then', 'bahut': 'very', 'thoda': 'little',
        'jyada': 'more', 'kam': 'less', 'bilkul': 'exactly',
        'kaise': 'how', 'kya': 'what', 'kyun': 'why', 'kab': 'when',
        
        # Common adjectives
        'accha': 'good', 'bura': 'bad', 'bada': 'big', 'chota': 'small',
        'naya': 'new', 'purana': 'old', 'pehla': 'first', 'dusra': 'second',
        
        # Common conjunctions
        'aur': 'and', 'ya': 'or', 'lekin': 'but', 'agar': 'if',
        'tab': 'then', 'jab': 'when', 'kyunki': 'because',
        
        # Common phrases
        'iske baad': 'after this', 'isse pehle': 'before this',
        'matlab': 'means', 'yaani': 'that is',
        
        # Technical terms in Hindi
        'saari': 'all', 'sabhi': 'all', 'koi': 'any', 'ek': 'one',
        'do': 'two', 'teen': 'three', 'char': 'four', 'paanch': 'five'
    }
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize code-mixed processor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.openai_api_key = config.get('api_keys', {}).get('openai_api_key', '')
        
        # Initialize Google Translator for fallback
        self.translator = None
        if TRANSLATOR_AVAILABLE:
            try:
                self.translator = GoogleTranslator(source='auto', target='en')
                self.logger.info("Google Translator initialized for fallback translation")
            except Exception as e:
                self.logger.warning(f"Could not initialize Google Translator: {e}")
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def detect_languages(self, text: str) -> List[Tuple[str, float]]:
        """
        Detect languages in text
        
        Args:
            text: Input text
        
        Returns:
            List of (language_code, probability) tuples
        """
        try:
            langs = detect_langs(text)
            return [(lang.lang, lang.prob) for lang in langs]
        except Exception as e:
            self.logger.warning(f"Language detection failed: {str(e)}")
            return []
    
    def identify_code_mixing(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for code-mixing patterns
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with code-mixing analysis
        """
        # Detect languages
        languages = self.detect_languages(text)
        
        # Simple heuristic: if multiple languages detected with significant probability
        is_code_mixed = len([l for l in languages if l[1] > 0.3]) > 1
        
        # Identify common Indic language patterns
        indic_patterns = {
            'devanagari': re.findall(r'[\u0900-\u097F]+', text),  # Hindi
            'tamil': re.findall(r'[\u0B80-\u0BFF]+', text),
            'telugu': re.findall(r'[\u0C00-\u0C7F]+', text),
            'kannada': re.findall(r'[\u0C80-\u0CFF]+', text),
        }
        
        return {
            'is_code_mixed': is_code_mixed,
            'detected_languages': languages,
            'indic_scripts': {k: v for k, v in indic_patterns.items() if v},
            'has_indic_script': any(indic_patterns.values())
        }
    
    def dictionary_normalize(self, text: str) -> Dict[str, Any]:
        """
        Stage 1: Dictionary-based normalization of common terms
        Uses Telugu + Hindi dictionaries, then Google Translate fallback
        
        Args:
            text: Input text
        
        Returns:
            Normalized text and mappings
        """
        normalized_text = text
        applied_mappings = {}
        
        # Combine Telugu and Hindi dictionaries
        combined_dict = {**self.TELUGU_DICT, **self.HINGLISH_DICT}
        
        # Sort by length (longer phrases first)
        sorted_dict = sorted(combined_dict.items(), key=lambda x: len(x[0]), reverse=True)
        
        for native_term, english_term in sorted_dict:
            # Case-insensitive replacement with word boundaries
            pattern = r'\b' + re.escape(native_term) + r'\b'
            if re.search(pattern, normalized_text, re.IGNORECASE):
                normalized_text = re.sub(pattern, english_term, normalized_text, flags=re.IGNORECASE)
                applied_mappings[native_term] = english_term
        
        self.logger.info(f"Dictionary normalization: {len(applied_mappings)} terms replaced")
        
        # Google Translate fallback for remaining non-English sentences (better context than word-by-word)
        if self.translator:
            try:
                # Strategy: Translate sentence-by-sentence for better context
                sentences = normalized_text.split('. ')
                translated_sentences = []
                translate_count = 0
                
                for sentence in sentences:
                    # Check if sentence has Telugu/Hindi patterns  
                    has_indic_script = bool(re.search(r'[\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF]', sentence))
                    has_transliterated = bool(re.search(r'(nka|nnu|ndi|atte|tte|lla|dda|chh|tho|ante|kani|anni|chey|cheyyandi|problemu|mankamat|mapper)', sentence.lower()))
                    
                    # Only translate if appears to have Indic content
                    if has_indic_script or has_transliterated:
                        try:
                            translated_sentence = self.translator.translate(sentence)
                            if translated_sentence and translated_sentence.strip() != sentence.strip():
                                translated_sentences.append(translated_sentence)
                                translate_count += 1
                            else:
                                translated_sentences.append(sentence)
                        except Exception as e:
                            self.logger.debug(f"Translation failed for sentence: {e}")
                            translated_sentences.append(sentence)
                    else:
                        translated_sentences.append(sentence)
                
                if translate_count > 0:
                    normalized_text = '. '.join(translated_sentences)
                    self.logger.info(f"Google Translate fallback: {translate_count} sentences translated")
            except Exception as e:
                self.logger.warning(f"Google Translate fallback failed: {e}")
        
        return {
            'normalized_text': normalized_text,
            'mappings': applied_mappings,
            'method': 'dictionary+translate'
        }
    
    def translate_indic_scripts(self, text: str) -> Dict[str, Any]:
        """
        Stage 2: Detect and translate Indic scripts
        
        Args:
            text: Input text
        
        Returns:
            Translated text and detected scripts
        """
        # Identify Indic script patterns
        indic_patterns = {
            'devanagari': (r'[\u0900-\u097F]+', 'Hindi'),
            'tamil': (r'[\u0B80-\u0BFF]+', 'Tamil'),
            'telugu': (r'[\u0C00-\u0C7F]+', 'Telugu'),
            'kannada': (r'[\u0C80-\u0CFF]+', 'Kannada'),
        }
        
        detected_scripts = {}
        for script_name, (pattern, language) in indic_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_scripts[script_name] = {
                    'language': language,
                    'matches': matches,
                    'count': len(matches)
                }
        
        translated_text = text
        
        # For now, just identify scripts (translation would require IndicTrans or Google Translate API)
        # In production, you would use IndicTrans or translation API here
        if detected_scripts:
            self.logger.info(f"Detected {len(detected_scripts)} Indic scripts")
            self.logger.warning("Indic script translation not implemented. Using LLM for refinement.")
        
        return {
            'text': translated_text,
            'detected_scripts': detected_scripts,
            'method': 'script_detection'
        }
    
    def llm_refine(self, text: str, domain: str = "Computer Science") -> Dict[str, Any]:
        """
        Stage 3: SKIPPED IN FREE MODE (no LLM needed)
        
        Args:
            text: Input text (after dictionary and translation)
            domain: Academic domain
        
        Returns:
            Text from stage 2 (no LLM refinement)
        """
        self.logger.info("FREE MODE: Skipping LLM refinement (Stage 3)")
        
        return {
            'refined_text': text,
            'additional_mappings': {},
            'technical_terms': [],
            'method': 'free_mode_skip'
        }
    
    def standardize_terminology(self, text: str, domain: str = "Computer Science") -> Dict[str, Any]:
        """
        Three-stage hybrid normalization
        
        Args:
            text: Input text with colloquial terminology
            domain: Academic domain
        
        Returns:
            Dictionary with standardized text and complete mappings
        """
        self.logger.info("Starting three-stage normalization")
        
        # Stage 1: Dictionary-based
        stage1_result = self.dictionary_normalize(text)
        
        # Stage 2: Script detection and translation
        stage2_result = self.translate_indic_scripts(stage1_result['normalized_text'])
        
        # Stage 3: LLM refinement
        stage3_result = self.llm_refine(stage2_result['text'], domain)
        
        # Combine all mappings
        all_mappings = {}
        all_mappings.update(stage1_result['mappings'])
        all_mappings.update(stage3_result.get('additional_mappings', {}))
        
        return {
            'original_text': text,
            'stage1_output': stage1_result['normalized_text'],
            'stage2_output': stage2_result['text'],
            'standardized_text': stage3_result['refined_text'],
            'term_mappings': all_mappings,
            'detected_scripts': stage2_result['detected_scripts'],
            'technical_terms': stage3_result.get('technical_terms', []),
            'statistics': {
                'dictionary_replacements': len(stage1_result['mappings']),
                'detected_scripts': len(stage2_result['detected_scripts']),
                'llm_refinements': len(stage3_result.get('additional_mappings', {})),
                'total_mappings': len(all_mappings)
            }
        }
    
    def process_transcript(self, transcript: str, domain: str = "Computer Science") -> Dict[str, Any]:
        """
        Complete processing pipeline for code-mixed transcript
        
        Args:
            transcript: Raw transcript text
            domain: Academic domain
        
        Returns:
            Processed transcript with language analysis and standardization
        """
        self.logger.info("Processing code-mixed transcript")
        
        # Analyze code-mixing
        code_mixing_analysis = self.identify_code_mixing(transcript)
        self.logger.info(f"Code-mixing detected: {code_mixing_analysis['is_code_mixed']}")
        self.logger.info(f"Detected languages: {code_mixing_analysis['detected_languages']}")
        
        # Standardize terminology
        standardization = self.standardize_terminology(transcript, domain)
        
        # Combine results
        return {
            'original_transcript': transcript,
            'code_mixing_analysis': code_mixing_analysis,
            'standardization': standardization,
            'processed_text': standardization.get('standardized_text', transcript)
        }
