"""
Main entry point for Code-Mixed Pedagogical Flow Extractor
"""

import argparse
import sys
from pathlib import Path

from src.pipeline import PedagogicalFlowPipeline
from src.utils import setup_logger


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Code-Mixed edagogical Flow Extractor - Extract concept dependencies from educational videos'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--video-id',
        type=str,
        help='Process specific video by ID (as defined in config)'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='Process video from URL (requires --video-id)'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        default='auto',
        help='Language code or "auto" for auto-detection (default: auto)'
    )
    
    parser.add_argument(
        '--domain',
        type=str,
        default='Computer Science',
        help='Academic domain (default: Computer Science)'
    )
    
    parser.add_argument(
        '--process-all',
        action='store_true',
        help='Process all videos configured in config.yaml'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        pipeline = PedagogicalFlowPipeline(args.config)
        
        if args.process_all:
            # Process all configured videos
            print("\n" + "=" * 80)
            print("Processing all configured videos...")
            print("=" * 80 + "\n")
            
            results = pipeline.process_all_configured_videos()
            
            if results:
                # Generate summary report
                summary = pipeline.generate_summary_report(results)
                
                print("\n" + "=" * 80)
                print("PIPELINE COMPLETED SUCCESSFULLY")
                print("=" * 80)
                print(f"\nProcessed {len(results)} videos successfully")
                print(f"Total concepts extracted: {summary['aggregate_stats']['total_concepts']}")
                print(f"Total relationships mapped: {summary['aggregate_stats']['total_relationships']}")
                print(f"\nSummary report saved to: outputs/summary_report.json")
                print("\nOutput files generated for each video:")
                for video in summary['videos']:
                    print(f"\n  {video['video_id']}:")
                    print(f"    - Concepts: {video['concept_count']}")
                    print(f"    - Relationships: {video['relationship_count']}")
                    print(f"    - Interactive visualization: {video['output_files'].get('interactive_viz', 'N/A')}")
            else:
                print("\nNo videos processed. Please check your configuration.")
                return 1
        
        elif args.url and args.video_id:
            # Process single video from command line
            print("\n" + "=" * 80)
            print(f"Processing single video: {args.video_id}")
            print("=" * 80 + "\n")
            
            result = pipeline.process_single_video(
                video_id=args.video_id,
                url=args.url,
                language=args.language,
                domain=args.domain
            )
            
            if result:
                print("\n" + "=" * 80)
                print("PROCESSING COMPLETED SUCCESSFULLY")
                print("=" * 80)
                print(f"\nVideo ID: {result['video_id']}")
                print(f"Domain: {result['domain']}")
                print(f"Main Topic: {result['metadata']['main_topic']}")
                print(f"Concepts extracted: {result['metadata']['total_concepts']}")
                print(f"Relationships mapped: {result['metadata']['total_relationships']}")
                print(f"\nOutput files:")
                for output_type, output_path in result['output_files'].items():
                    print(f"  - {output_type}: {output_path}")
            else:
                print("\nFailed to process video. Check logs for details.")
                return 1
        
        elif args.video_id:
            # Process specific video from config
            video_sources = pipeline.config_loader.get_video_sources()
            
            if args.video_id not in video_sources:
                print(f"\nError: Video ID '{args.video_id}' not found in configuration.")
                print(f"Available video IDs: {', '.join(video_sources.keys())}")
                return 1
            
            video_data = video_sources[args.video_id]
            
            result = pipeline.process_single_video(
                video_id=args.video_id,
                url=video_data.get('url'),
                language=video_data.get('language', 'auto'),
                domain=video_data.get('domain', 'Computer Science')
            )
            
            if result:
                print("\nProcessing completed successfully!")
            else:
                print("\nFailed to process video. Check logs for details.")
                return 1
        
        else:
            # No valid arguments provided
            parser.print_help()
            print("\nExamples:")
            print("  # Process all configured videos:")
            print("  python main.py --process-all")
            print("\n  # Process specific video from config:")
            print("  python main.py --video-id video_1")
            print("\n  # Process video from URL:")
            print("  python main.py --video-id my_video --url 'https://youtube.com/...' --domain 'Physics'")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        return 130
    
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
