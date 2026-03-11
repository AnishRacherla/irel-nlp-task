"""
Example script demonstrating how to use the pipeline programmatically
Run with: python example_usage.py --video-id video_1
"""

import argparse
from src.pipeline import PedagogicalFlowPipeline


def example_process_video(video_id='video_1'):
    """Example: Process a single video from config"""
    
    print(f"\n🎬 Processing {video_id}...")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = PedagogicalFlowPipeline('config/config.yaml')
    
    # Get video config
    video_sources = pipeline.config_loader.get_video_sources()
    
    if video_id not in video_sources:
        print(f"❌ Error: {video_id} not found in config/config.yaml")
        print(f"Available videos: {', '.join(video_sources.keys())}")
        return None
    
    video_data = video_sources[video_id]
    
    # Process video
    result = pipeline.process_single_video(
        video_id=video_id,
        url=video_data.get('url', ''),
        language=video_data.get('language', 'auto'),
        domain=video_data.get('domain', 'Computer Science')
    )
    
    if result:
        print(f"\n✅ Successfully processed video!")
        print(f"📊 Extracted {result['metadata']['total_concepts']} concepts")
        print(f"🔗 Mapped {result['metadata']['total_relationships']} relationships")
        print(f"📁 Output files:")
        print(f"   - output/{video_id}_complete_output.json")
        print(f"   - output/{video_id}_interactive_graph.html")
        print(f"   - output/{video_id}_graph.png")
        print(f"\n🌐 Open output/{video_id}_interactive_graph.html in your browser!")
        
        # Show first 5 concepts
        concepts = result['concepts']['concepts']
        if concepts:
            print(f"\n📚 Top concepts extracted:")
            for concept in concepts[:5]:
                print(f"   - {concept['name']}: {concept['description']}")
    else:
        print(f"❌ Failed to process video")
    
    return result


def example_process_all():
    """Example: Process all configured videos"""
    
    print("\n📚 Processing all configured videos...")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = PedagogicalFlowPipeline('config/config.yaml')
    
    # Process all videos
    results = pipeline.process_all_configured_videos()
    
    if results:
        # Generate summary
        summary = pipeline.generate_summary_report(results)
        
        print(f"\n✅ Processed {summary['total_videos']} videos")
        print(f"📊 Total concepts: {summary['aggregate_stats']['total_concepts']}")
        print(f"🔗 Total relationships: {summary['aggregate_stats']['total_relationships']}")
        print(f"\n📁 Check output/ folder for all results")
    else:
        print(f"❌ No videos were processed")
    
    return results


def example_custom_config():
    """Example: Use custom configuration"""
    
    import yaml
    
    # Load and modify config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Modify settings
    config['transcription']['whisper_model_size'] = 'small'  # Use smaller model
    config['concept_extraction']['max_concepts_per_video'] = 10
    
    # Save temporary config
    with open('config/custom_config.yaml', 'w') as f:
        yaml.dump(config, f)
    
    # Use custom config
    pipeline = PedagogicalFlowPipeline('config/custom_config.yaml')
    # ... process videos


def example_access_components():
    """Example: Access individual pipeline components"""
    
    from src.utils import ConfigLoader
    from src.concept_extractor import ConceptExtractor
    from src.utils import setup_logger
    
    # Setup
    config_loader = ConfigLoader('config/config.yaml')
    logger = setup_logger()
    
    # Use individual component
    extractor = ConceptExtractor(config_loader.get_all(), logger)
    
    # Extract concepts from text
    sample_text = """
    In this lesson, we'll learn about binary search.
    Binary search is an algorithm that finds an element in a sorted array.
    First, you need to understand what arrays are...
    """
    
    concepts = extractor.extract_concepts(sample_text, domain='Computer Science')
    print(f"Extracted {len(concepts['concepts'])} concepts")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process educational videos')
    parser.add_argument('--video-id', type=str, default='video_1',
                        help='Video ID from config.yaml (default: video_1)')
    parser.add_argument('--all', action='store_true',
                        help='Process all configured videos')
    
    args = parser.parse_args()
    
    if args.all:
        print("\n📚 Processing all configured videos...")
        example_process_all()
    else:
        print(f"\n🎯 Processing single video: {args.video_id}")
        example_process_video(args.video_id)
