"""
Prerequisite mapping module (Hybrid Approach)
Uses cue phrases + temporal order + dependency parsing + embeddings + LLM validation
"""

from typing import Dict, List, Any, Tuple
import openai
import json
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class HybridPrerequisiteMapper:
    """Map prerequisite relationships using hybrid NLP + LLM approach"""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize hybrid prerequisite mapper
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.openai_api_key = config.get('api_keys', {}).get('openai_api_key', '')
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        self.embedding_model = None
        
        # Prerequisite cue phrases (signals)
        self.prerequisite_cues = [
            r'before\s+(?:understanding|learning|studying)?\s*([^,.]+),?\s*(?:you\s+)?(?:need|must|should|have\s+to)',
            r'requires?\s+(?:understanding\s+of\s+)?([^,.]+)',
            r'builds?\s+(?:up)?on\s+([^,.]+)',
            r'assumes?\s+(?:knowledge\s+of\s+)?([^,.]+)',
            r'prerequisite\s+(?:is|are)\s+([^,.]+)',
            r'first\s+(?:you\s+)?(?:need|must)\s+(?:to\s+)?(?:understand|know|learn)\s+([^,.]+)',
            r'depends?\s+on\s+([^,.]+)',
            r'based\s+on\s+([^,.]+)',
            r'after\s+(?:learning|understanding)\s+([^,.]+)',
            r'once\s+(?:you\s+)?(?:understand|know)\s+([^,.]+)'
        ]
    
    def _load_embedding_model(self):
        """Load embedding model lazily"""
        if self.embedding_model is None:
            self.logger.info("Loading sentence transformer for prerequisite mapping...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Embedding model loaded")
    
    def detect_cue_phrase_prerequisites(self, text: str, concepts: List[Dict[str, Any]], 
                                       preprocessing_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect prerequisites using cue phrases
        
        Args:
            text: Full text
            concepts: List of extracted concepts
            preprocessing_data: Preprocessing output with cue phrases
        
        Returns:
            List of prerequisite relationships detected by cues
        """
        relationships = []
        detected_cue_phrases = preprocessing_data.get('cue_phrases', [])
        
        # Analyze each cue phrase occurrence
        for cue_info in detected_cue_phrases:
            # cue_info has: type, pattern, match, concept, position
            match_text = cue_info.get('match', '')
            pattern = cue_info.get('pattern', '')
            cue_concept = cue_info.get('concept', '')
            
            # Try to identify concepts in the cue phrase match
            mentioned_concepts = []
            for concept in concepts:
                if concept['name'].lower() in match_text.lower() or concept['name'].lower() in cue_concept.lower():
                    mentioned_concepts.append(concept)
            
            # If we have at least 2 concepts in a cue phrase sentence, likely a prerequisite
            if len(mentioned_concepts) >= 2:
                # Pattern analysis to determine direction
                if any(p in pattern.lower() for p in ['before', 'first', 'prerequisite', 'requires', 'depends']):
                    # First concept is prerequisite of second
                    relationships.append({
                        'prerequisite': mentioned_concepts[0]['id'],
                        'target': mentioned_concepts[1]['id'],
                        'confidence': 0.8,
                        'signal': 'cue_phrase',
                        'evidence': match_text,
                        'cue_pattern': pattern
                    })
                elif any(p in pattern.lower() for p in ['builds on', 'based on', 'after']):
                    # Second concept is prerequisite of first
                    relationships.append({
                        'prerequisite': mentioned_concepts[1]['id'],
                        'target': mentioned_concepts[0]['id'],
                        'confidence': 0.8,
                        'signal': 'cue_phrase',
                        'evidence': match_text,
                        'cue_pattern': pattern
                    })
        
        self.logger.info(f"Cue phrase analysis found {len(relationships)} potential prerequisites")
        return relationships
    
    def compute_temporal_order_prerequisites(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Infer prerequisites from temporal order (earlier concepts are potential prerequisites)
        
        Args:
            concepts: List of concepts with temporal positions
        
        Returns:
            List of temporal-based prerequisite relationships
        """
        relationships = []
        
        # Sort concepts by temporal position
        concepts_with_position = [c for c in concepts if 'nlp_scores' in c and 'temporal_position' in c['nlp_scores']]
        concepts_with_position.sort(key=lambda x: x['nlp_scores']['temporal_position'])
        
        # For each concept, earlier concepts are potential prerequisites
        for i, target_concept in enumerate(concepts_with_position):
            for j in range(max(0, i - 3), i):  # Look at up to 3 preceding concepts
                prereq_concept = concepts_with_position[j]
                
                temporal_gap = target_concept['nlp_scores']['temporal_position'] - prereq_concept['nlp_scores']['temporal_position']
                
                # Only if there's meaningful gap (not adjacent/overlapping)
                if temporal_gap > 0.10:  # Meaningful separation between concepts
                    confidence = min(0.7, 0.5 + temporal_gap)  # Larger gap = higher confidence (up to 0.7)
                    
                    relationships.append({
                        'prerequisite': prereq_concept['id'],
                        'target': target_concept['id'],
                        'confidence': confidence,
                        'signal': 'temporal_order',
                        'evidence': f"{prereq_concept['name']} appears before {target_concept['name']}",
                        'temporal_gap': temporal_gap
                    })
        
        self.logger.info(f"Temporal analysis found {len(relationships)} potential prerequisites")
        return relationships
    
    def compute_semantic_similarity_prerequisites(self, concepts: List[Dict[str, Any]], 
                                                  threshold: float = 0.55) -> List[Dict[str, Any]]:
        """
        Compute semantic similarity to identify related concepts
        
        Args:
            concepts: List of concepts
            threshold: Similarity threshold (stricter: 0.55 for quality relationships)
        
        Returns:
            List of similarity-based relationships
        """
        self._load_embedding_model()
        
        relationships = []
        
        # Get concept names and descriptions
        concept_texts = [f"{c['name']} {c.get('description', '')}" for c in concepts]
        
        if len(concept_texts) < 2:
            return relationships
        
        # Compute embeddings
        embeddings = self.embedding_model.encode(concept_texts)
        similarity_matrix = cosine_similarity(embeddings)
        
        # Analyze similarities
        for i, concept_i in enumerate(concepts):
            for j, concept_j in enumerate(concepts):
                if i >= j:  # Skip self and duplicates
                    continue
                
                sim_score = similarity_matrix[i][j]
                
                if sim_score > threshold:
                    # Higher similarity suggests relationship
                    # If we have temporal info, use it to determine direction
                    temporal_i = concept_i.get('nlp_scores', {}).get('temporal_position', 0.5)
                    temporal_j = concept_j.get('nlp_scores', {}).get('temporal_position', 0.5)
                    
                    if temporal_i < temporal_j:
                        # i comes before j, so i is prerequisite of j
                        prereq_id = concept_i['id']
                        target_id = concept_j['id']
                    else:
                        prereq_id = concept_j['id']
                        target_id = concept_i['id']
                    
                    relationships.append({
                        'prerequisite': prereq_id,
                        'target': target_id,
                        'confidence': sim_score * 0.7,  # Downweight semantic signal
                        'signal': 'semantic_similarity',
                        'evidence': f"High semantic similarity ({sim_score:.2f})",
                        'similarity_score': sim_score
                    })
        
        self.logger.info(f"Semantic analysis found {len(relationships)} potential prerequisites")
        return relationships
    
    def analyze_dependency_structure(self, preprocessing_data: Dict[str, Any], 
                                    concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze dependency parse trees for prerequisite signals
        
        Args:
            preprocessing_data: Preprocessing output with dependency info
            concepts: List of concepts
        
        Returns:
            List of dependency-based relationships
        """
        relationships = []
        dependencies = preprocessing_data.get('dependencies', [])
        
        # Look for specific dependency patterns that signal prerequisites
        prerequisite_dep_patterns = [
            ('nsubj', 'requires', 'dobj'),  # X requires Y
            ('nsubj', 'depends', 'prep'),   # X depends on Y
            ('nsubj', 'based', 'prep'),     # X based on Y
        ]
        
        for dep_info in dependencies:
            sentence = dep_info.get('sentence', '')
            deps = dep_info.get('dependencies', [])
            
            # Find concepts in this sentence
            mentioned_concepts = [c for c in concepts if c['name'].lower() in sentence.lower()]
            
            if len(mentioned_concepts) >= 2:
                # Check for prerequisite patterns in dependencies
                for dep in deps:
                    if dep['dep'] in ['nsubj', 'dobj', 'prep', 'pobj']:
                        relationships.append({
                            'prerequisite': mentioned_concepts[0]['id'],
                            'target': mentioned_concepts[1]['id'],
                            'confidence': 0.5,
                            'signal': 'dependency_parse',
                            'evidence': sentence,
                            'dependency': dep
                        })
                        break  # One relationship per sentence
        
        self.logger.info(f"Dependency analysis found {len(relationships)} potential prerequisites")
        return relationships
    
    def merge_prerequisite_signals(self, all_relationships: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Merge prerequisite signals from multiple sources
        
        Args:
            all_relationships: List of relationship lists from different signals
        
        Returns:
            Merged and deduplicated relationships with combined confidence
        """
        # Flatten
        flat_rels = [rel for sublist in all_relationships for rel in sublist]
        
        # Group by (prerequisite, target) pair
        grouped = {}
        for rel in flat_rels:
            key = (rel['prerequisite'], rel['target'])
            if key not in grouped:
                grouped[key] = {
                    'prerequisite': rel['prerequisite'],
                    'target': rel['target'],
                    'signals': [],
                    'confidences': [],
                    'evidence': []
                }
            grouped[key]['signals'].append(rel['signal'])
            grouped[key]['confidences'].append(rel['confidence'])
            grouped[key]['evidence'].append(rel.get('evidence', ''))
        
        # Compute combined confidence
        merged = []
        for key, rel_data in grouped.items():
            # Multiple signals increase confidence
            num_signals = len(rel_data['signals'])
            avg_confidence = np.mean(rel_data['confidences'])
            
            # Boost if multiple independent signals agree
            signal_diversity = len(set(rel_data['signals']))
            boost = min(0.2, signal_diversity * 0.1)
            
            combined_confidence = min(0.95, avg_confidence + boost)
            
            merged.append({
                'prerequisite': rel_data['prerequisite'],
                'target': rel_data['target'],
                'confidence': combined_confidence,
                'signals': rel_data['signals'],
                'num_signals': num_signals,
                'evidence': list(set(rel_data['evidence'])),
                'status': 'candidate'
            })
        
        # Sort by confidence
        merged.sort(key=lambda x: x['confidence'], reverse=True)
        
        self.logger.info(f"Merged into {len(merged)} unique prerequisite relationships")
        return merged
    
    def llm_validate_prerequisites(self, prerequisite_candidates: List[Dict[str, Any]], 
                                  concepts: List[Dict[str, Any]], 
                                  text: str) -> List[Dict[str, Any]]:
        """
        Validate prerequisites using ONLY traditional NLP (FREE - no API calls)
        
        Args:
            prerequisite_candidates: Candidate relationships from NLP
            concepts: List of all concepts
            text: Original text
        
        Returns:
            Validated prerequisites using rule-based filtering
        """
        self.logger.info("FREE MODE: Using rule-based validation (no LLM)")
        
        # Use completely free rule-based validation
        return self._fallback_prerequisites(prerequisite_candidates)
    
    def _fallback_prerequisites(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rule-based prerequisite validation (completely free)"""
        validated = []
        
        for rel in candidates:
            confidence = rel['confidence']
            num_signals = rel.get('num_signals', 1)
            
            # Balanced threshold: good confidence OR multiple signals  
            if (confidence > 0.75 and num_signals >= 1) or (confidence > 0.65 and num_signals >= 2):
                # Determine strength based on confidence and signals
                if confidence > 0.85 or num_signals >= 4:
                    strength = 'strong'
                elif confidence > 0.75 or num_signals >= 3:
                    strength = 'moderate'
                else:
                    strength = 'weak'
                
                validated.append({
                    'prerequisite': rel['prerequisite'],
                    'prerequisite_id': rel['prerequisite'],
                    'target': rel['target'],
                    'target_id': rel['target'],
                    'confidence': confidence,
                    'strength': strength,
                    'is_valid': True,
                    'validation_method': 'rule_based_free',
                    'signals': rel['signals'],
                    'num_signals': num_signals,
                    'pedagogical_reasoning': f"Based on {num_signals} NLP signals with {confidence:.2f} confidence"
                })
        
        # Sort by confidence and return top results
        validated.sort(key=lambda x: (x['num_signals'], x['confidence']), reverse=True)
        
        self.logger.info(f"Rule-based validation: {len(validated[:15])} prerequisites (FREE)")
        return validated[:15]
    
    def map_prerequisites(self, concepts: List[Dict[str, Any]], text: str, 
                         preprocessing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete hybrid prerequisite mapping pipeline
        
        Args:
            concepts: Extracted concepts
            text: Standardized text
            preprocessing_data: Preprocessing output
        
        Returns:
            Validated prerequisite relationships
        """
        self.logger.info("Starting hybrid prerequisite mapping")
        
        # Signal 1: Cue phrase analysis
        cue_relationships = self.detect_cue_phrase_prerequisites(text, concepts, preprocessing_data)
        
        # Signal 2: Temporal order
        temporal_relationships = self.compute_temporal_order_prerequisites(concepts)
        
        # Signal 3: Semantic similarity
        semantic_relationships = self.compute_semantic_similarity_prerequisites(concepts)
        
        # Signal 4: Dependency parsing
        dependency_relationships = self.analyze_dependency_structure(preprocessing_data, concepts)
        
        # Merge all signals
        merged_relationships = self.merge_prerequisite_signals([
            cue_relationships,
            temporal_relationships,
            semantic_relationships,
            dependency_relationships
        ])
        
        # LLM validation
        validated_relationships = self.llm_validate_prerequisites(merged_relationships, concepts, text)
        
        return {
            'prerequisites': validated_relationships,
            'total_prerequisites': len(validated_relationships),
            'mapping_statistics': {
                'cue_phrase_signals': len(cue_relationships),
                'temporal_signals': len(temporal_relationships),
                'semantic_signals': len(semantic_relationships),
                'dependency_signals': len(dependency_relationships),
                'merged_candidates': len(merged_relationships),
                'validated_prerequisites': len(validated_relationships)
            }
        }
