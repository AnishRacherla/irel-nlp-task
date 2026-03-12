"""
Main pipeline orchestrator
Coordinates all modules to process educational videos
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from src.utils import ConfigLoader, setup_logger
from src.transcription import VideoTranscriber
from src.preprocessing import TextPreprocessor
from src.code_mixed_processor import CodeMixedProcessor
from src.concept_extractor.hybrid_extractor import HybridConceptExtractor
from src.prerequisite_mapper.hybrid_mapper import HybridPrerequisiteMapper
from src.visualizer import GraphVisualizer


class PedagogicalFlowPipeline:
    """Main pipeline for extracting pedagogical flow from educational videos"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize pipeline
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.get_all()
        
        # Setup logger
        self.logger = setup_logger("pedagogical_flow_pipeline")
        
        self.logger.info("=" * 80)
        self.logger.info("Pedagogical Flow Extractor Pipeline Initialized")
        self.logger.info("=" * 80)
        
        # Initialize modules
        self.transcriber = VideoTranscriber(self.config, self.logger)
        self.preprocessor = TextPreprocessor(self.config, self.logger)
        self.code_mixed_processor = CodeMixedProcessor(self.config, self.logger)
        self.concept_extractor = HybridConceptExtractor(self.config, self.logger)
        self.prerequisite_mapper = HybridPrerequisiteMapper(self.config, self.logger)
        self.visualizer = GraphVisualizer(self.config, self.logger)
    
    def process_single_video(self, video_id: str, url: str, language: str = "auto",
                           domain: str = "Computer Science") -> Optional[Dict[str, Any]]:
        """
        Process a single video through the complete pipeline
        
        Args:
            video_id: Unique identifier for the video
            url: Video URL
            language: Language code or 'auto'
            domain: Academic domain
        
        Returns:
            Complete processing result
        """
        self.logger.info("=" * 80)
        self.logger.info(f"Processing Video: {video_id}")
        self.logger.info(f"URL: {url}")
        self.logger.info(f"Domain: {domain}")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Transcription
            self.logger.info("[1/6] Transcribing video...")
            transcript_data = self.transcriber.process_video(url, video_id, language)
            
            if transcript_data is None:
                self.logger.error(f"Failed to transcribe video: {video_id}")
                return None
            
            transcript_text = transcript_data.get('text', '')
            self.logger.info(f"Transcription complete. Length: {len(transcript_text)} characters")
            
            # Step 2: Preprocessing (Traditional NLP)
            self.logger.info("[2/6] Preprocessing transcript with spaCy/NLTK...")
            preprocessing_data = self.preprocessor.preprocess(transcript_text)
            self.logger.info(f"Preprocessing complete. Sentences: {len(preprocessing_data.get('sentences', []))}, "
                           f"Noun phrases: {len(preprocessing_data.get('noun_phrases', []))}, "
                           f"Cue phrases: {len(preprocessing_data.get('cue_phrases', []))}")
            
            # Step 3: Code-mixed language processing (Hybrid)
            self.logger.info("[3/6] Processing code-mixed language...")
            processed_language = self.code_mixed_processor.process_transcript(transcript_text, domain)
            standardized_text = processed_language.get('processed_text', transcript_text)
            
            # Step 4: Concept extraction (Hybrid: KeyBERT + spaCy + Embeddings + LLM)
            self.logger.info("[4/6] Extracting concepts with hybrid NLP + LLM...")
            concepts_data = self.concept_extractor.extract_and_validate(
                standardized_text, preprocessing_data, domain
            )
            concepts = concepts_data.get('concepts', [])
            
            if not concepts:
                self.logger.warning("No concepts extracted!")
                return None
            
            self.logger.info(f"Extracted {len(concepts)} concepts")
            
            # Step 5: Prerequisite mapping (Hybrid: Multiple signals + LLM)
            self.logger.info("[5/6] Mapping prerequisite relationships with hybrid approach...")
            prerequisite_data = self.prerequisite_mapper.map_prerequisites(
                concepts, standardized_text, preprocessing_data
            )
            
            self.logger.info(f"Mapped {len(prerequisite_data.get('prerequisites', []))} relationships")
            
            # Step 6: Visualization and output
            self.logger.info("[6/6] Generating visualizations and outputs...")
            
            # Prepare complete result
            complete_result = {
                'video_id': video_id,
                'url': url,
                'domain': domain,
                'language': language,
                'detected_language': transcript_data.get('language', 'unknown'),
                'transcript': {
                    'original': transcript_text,
                    'standardized': standardized_text,
                    'length': len(transcript_text)
                },
                'preprocessing': {
                    'sentence_count': len(preprocessing_data.get('sentences', [])),
                    'noun_phrase_count': len(preprocessing_data.get('noun_phrases', [])),
                    'cue_phrase_count': len(preprocessing_data.get('cue_phrases', [])),
                    'statistics': preprocessing_data.get('statistics', {})
                },
                'language_processing': processed_language,
                'concepts': concepts_data,
                'prerequisites': prerequisite_data,
                'metadata': {
                    'total_concepts': len(concepts),
                    'total_relationships': len(prerequisite_data.get('prerequisites', [])),
                    'extraction_approach': 'hybrid_nlp_llm'
                }
            }
            
            # Convert prerequisite format for visualizer
            relationships_for_viz = []
            for prereq in prerequisite_data.get('prerequisites', []):
                relationships_for_viz.append({
                    'source': prereq.get('prerequisite_id', prereq.get('prerequisite')),
                    'target': prereq.get('target_id', prereq.get('target')),
                    'confidence': prereq.get('confidence', 0.5),
                    'strength': prereq.get('strength', 'moderate')
                })
            
            # Enrich each concept with its prerequisite/enables info
            concept_id_to_name = {c['id']: c['name'] for c in concepts}
            prereq_map = {}   # concept_id -> list of {id, name, confidence} it requires
            enables_map = {}  # concept_id -> list of {id, name, confidence} it unlocks
            for rel in relationships_for_viz:
                src, tgt, conf = rel['source'], rel['target'], rel.get('confidence', 0.5)
                enables_map.setdefault(src, []).append({'id': tgt, 'name': concept_id_to_name.get(tgt, tgt), 'confidence': conf})
                prereq_map.setdefault(tgt, []).append({'id': src, 'name': concept_id_to_name.get(src, src), 'confidence': conf})

            enriched_concepts = []
            for c in concepts:
                enriched = dict(c)
                enriched['prerequisites'] = prereq_map.get(c['id'], [])
                enriched['enables'] = enables_map.get(c['id'], [])
                enriched_concepts.append(enriched)

            viz_data = {
                'concepts': enriched_concepts,
                'relationships': relationships_for_viz
            }
            
            # Generate all output formats
            output_files = self.visualizer.generate_all_outputs(
                viz_data, 
                video_id,
                title=f"{domain}: {video_id}"
            )
            
            complete_result['output_files'] = {k: str(v) for k, v in output_files.items()}
            
            self.logger.info("=" * 80)
            self.logger.info(f"Successfully processed video: {video_id}")
            self.logger.info(f"Concepts: {len(concepts)}")
            self.logger.info(f"Relationships: {len(prerequisite_data.get('prerequisites', []))}")
            self.logger.info(f"Output files: {len(output_files)}")
            self.logger.info("=" * 80)
            self.logger.info(f"Relationships: {len(prerequisite_data.get('relationships', []))}")
            self.logger.info(f"Output files: {len(output_files)}")
            self.logger.info("=" * 80)
            
            return complete_result
            
        except Exception as e:
            self.logger.error(f"Error processing video {video_id}: {str(e)}", exc_info=True)
            return None
    
    def process_all_configured_videos(self) -> List[Dict[str, Any]]:
        """
        Process all videos configured in config.yaml
        
        Returns:
            List of processing results
        """
        video_sources = self.config_loader.get_video_sources()
        
        if not video_sources:
            self.logger.warning("No video sources configured in config.yaml")
            return []
        
        results = []
        
        for video_key, video_data in video_sources.items():
            url = video_data.get('url', '')
            
            if not url:
                self.logger.warning(f"Skipping {video_key}: No URL provided")
                continue
            
            result = self.process_single_video(
                video_id=video_key,
                url=url,
                language=video_data.get('language', 'auto'),
                domain=video_data.get('domain', 'Computer Science')
            )
            
            if result:
                results.append(result)
        
        return results
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary report for all processed videos
        
        Args:
            results: List of processing results
        
        Returns:
            Summary report
        """
        if not results:
            return {'error': 'No results to summarize'}
        
        summary = {
            'total_videos': len(results),
            'videos': [],
            'aggregate_stats': {
                'total_concepts': 0,
                'total_relationships': 0,
                'domains': set(),
                'languages': set()
            }
        }
        
        for result in results:
            video_summary = {
                'video_id': result.get('video_id'),
                'url': result.get('url'),
                'domain': result.get('domain'),
                'language': result.get('language'),
                'detected_language': result.get('detected_language'),
                'main_topic': result.get('concepts', {}).get('main_topic'),
                'concept_count': result.get('metadata', {}).get('total_concepts', 0),
                'relationship_count': result.get('metadata', {}).get('total_relationships', 0),
                'output_files': result.get('output_files', {})
            }
            
            summary['videos'].append(video_summary)
            
            # Aggregate stats
            summary['aggregate_stats']['total_concepts'] += video_summary['concept_count']
            summary['aggregate_stats']['total_relationships'] += video_summary['relationship_count']
            summary['aggregate_stats']['domains'].add(result.get('domain'))
            summary['aggregate_stats']['languages'].add(result.get('detected_language'))
        
        # Convert sets to lists for JSON serialization
        summary['aggregate_stats']['domains'] = list(summary['aggregate_stats']['domains'])
        summary['aggregate_stats']['languages'] = list(summary['aggregate_stats']['languages'])
        
        # Save summary
        summary_path = Path(self.config.get('paths', {}).get('output_dir', 'outputs')) / 'summary_report.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Summary report saved: {summary_path}")
        
        return summary
