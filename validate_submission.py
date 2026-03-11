"""
Pre-submission validation script
Checks if everything is ready for submission
"""

import sys
import json
from pathlib import Path
import yaml


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a required file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: NOT FOUND - {filepath}")
        return False


def check_config_videos():
    """Check if videos are configured"""
    print("\n" + "="*60)
    print("Checking Video Configuration")
    print("="*60)
    
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        video_sources = config.get('video_sources', {})
        configured_count = 0
        
        for video_id, video_data in video_sources.items():
            url = video_data.get('url', '')
            language = video_data.get('language', '')
            domain = video_data.get('domain', '')
            
            if url and url != '' and not url.startswith('http'):
                print(f"⚠️  {video_id}: Invalid URL format")
                continue
            
            if url and url != '':
                configured_count += 1
                print(f"✅ {video_id}:")
                print(f"   Language: {language}")
                print(f"   Domain: {domain}")
                print(f"   URL: {url[:50]}...")
            else:
                print(f"❌ {video_id}: No URL configured")
        
        print(f"\n{'✅' if configured_count >= 5 else '❌'} Videos configured: {configured_count}/5")
        
        if configured_count < 5:
            print("\n⚠️  You need to configure at least 5 videos!")
            print("   Edit config/config.yaml and add video URLs")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading config: {str(e)}")
        return False


def check_api_key():
    """Check if API key is configured"""
    print("\n" + "="*60)
    print("Checking API Configuration")
    print("="*60)
    
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OpenAI API key not found in .env")
        return False
    elif api_key == 'your_openai_api_key_here':
        print("❌ API key not configured (still using placeholder)")
        return False
    elif not api_key.startswith('sk-'):
        print("⚠️  API key format looks incorrect")
        return False
    else:
        print(f"✅ API key configured: {api_key[:10]}...")
        return True


def check_outputs():
    """Check if any outputs have been generated"""
    print("\n" + "="*60)
    print("Checking Generated Outputs")
    print("="*60)
    
    outputs_dir = Path('outputs')
    
    if not outputs_dir.exists():
        print("⚠️  No outputs directory found (pipeline not run yet)")
        return False
    
    # Check for graphs
    graphs = list(Path('outputs/graphs').glob('*.json')) if Path('outputs/graphs').exists() else []
    visualizations = list(Path('outputs/visualizations').glob('*.html')) if Path('outputs/visualizations').exists() else []
    
    if len(graphs) > 0:
        print(f"✅ Graphs generated: {len(graphs)} files")
    else:
        print("⚠️  No graph files found")
    
    if len(visualizations) > 0:
        print(f"✅ Visualizations generated: {len(visualizations)} files")
    else:
        print("⚠️  No visualization files found")
    
    summary_path = Path('outputs/summary_report.json')
    if summary_path.exists():
        print("✅ Summary report generated")
        
        with open(summary_path, 'r') as f:
            summary = json.load(f)
        
        print(f"   Videos processed: {summary.get('total_videos', 0)}")
        print(f"   Total concepts: {summary['aggregate_stats'].get('total_concepts', 0)}")
        print(f"   Total relationships: {summary['aggregate_stats'].get('total_relationships', 0)}")
        
        return True
    else:
        print("⚠️  Summary report not found")
        print("\nℹ️  Run: python main.py --process-all")
        return False


def check_readme_completeness():
    """Check if README has been customized"""
    print("\n" + "="*60)
    print("Checking README Completeness")
    print("="*60)
    
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            readme = f.read()
        
        checks = {
            'video_sources': '### Video 1:' in readme and '[Link]' not in readme,
            'demo_video': 'Demo Video:' in readme and '[Your Demo Video URL]' not in readme,
            'github_url': 'GitHub:' in readme and '[Your GitHub URL]' not in readme,
        }
        
        if checks['video_sources']:
            print("✅ Video sources documented")
        else:
            print("❌ Video sources not documented in README")
            print("   Add your 5 video URLs to the 'Video Sources & Languages' section")
        
        if checks['demo_video']:
            print("✅ Demo video link added")
        else:
            print("❌ Demo video link not added to README")
            print("   Add your demo video URL to the 'Author' section")
        
        if checks['github_url']:
            print("✅ GitHub URL customized")
        else:
            print("⚠️  GitHub URL placeholder still present")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Error reading README: {str(e)}")
        return False


def check_git_repository():
    """Check if Git is initialized"""
    print("\n" + "="*60)
    print("Checking Git Repository")
    print("="*60)
    
    git_dir = Path('.git')
    
    if git_dir.exists():
        print("✅ Git repository initialized")
        
        gitignore = Path('.gitignore')
        if gitignore.exists():
            print("✅ .gitignore exists")
        else:
            print("⚠️  .gitignore not found")
        
        return True
    else:
        print("❌ Git not initialized")
        print("   Run: git init")
        return False


def check_requirements():
    """Check if all requirements are installed"""
    print("\n" + "="*60)
    print("Checking Python Dependencies")
    print("="*60)
    
    try:
        import pkg_resources
        
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip().split('>=')[0] for line in f if line.strip() and not line.startswith('#')]
        
        missing = []
        for package in requirements:
            try:
                pkg_resources.get_distribution(package)
            except pkg_resources.DistributionNotFound:
                missing.append(package)
        
        if not missing:
            print(f"✅ All {len(requirements)} dependencies installed")
            return True
        else:
            print(f"❌ Missing {len(missing)} dependencies:")
            for pkg in missing:
                print(f"   - {pkg}")
            print("\nRun: pip install -r requirements.txt")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not verify dependencies: {str(e)}")
        return True  # Don't block on this


def generate_submission_checklist():
    """Generate final submission checklist"""
    print("\n" + "="*60)
    print("FINAL SUBMISSION CHECKLIST")
    print("="*60)
    
    checklist = [
        ("GitHub repository created and public", False),
        ("All code committed and pushed", False),
        ("README.md includes 5 video sources with links", False),
        ("README.md includes demo video link", False),
        ("Demo video recorded and uploaded", False),
        ("Demo video is publicly accessible", False),
        ("requirements.txt is complete", True),
        ("Pipeline successfully processed all 5 videos", False),
        ("Output visualizations look meaningful", False),
        (".env file NOT committed (API keys)", True),
    ]
    
    print("\nBefore submitting, manually verify:\n")
    for item, auto_check in checklist:
        checkbox = "[ ]"
        print(f"{checkbox} {item}")
    
    print("\n" + "="*60)
    print("\nSubmission Requirements:")
    print("1. Public GitHub repository link")
    print("2. Working demo video link (YouTube/Google Drive)")
    print("=" * 60)


def main():
    """Run all validation checks"""
    print("="*60)
    print("iREL SUBMISSION VALIDATION")
    print("="*60)
    
    checks = []
    
    # File existence checks
    print("\n" + "="*60)
    print("Checking Required Files")
    print("="*60)
    
    required_files = [
        ('README.md', 'README'),
        ('requirements.txt', 'Requirements file'),
        ('main.py', 'Main entry point'),
        ('config/config.yaml', 'Configuration file'),
        ('.gitignore', 'Git ignore file'),
    ]
    
    files_ok = all(check_file_exists(f, d) for f, d in required_files)
    checks.append(('Required files', files_ok))
    
    # Video configuration
    videos_ok = check_config_videos()
    checks.append(('Video configuration', videos_ok))
    
    # API key
    api_ok = check_api_key()
    checks.append(('API key', api_ok))
    
    # Dependencies
    deps_ok = check_requirements()
    checks.append(('Dependencies', deps_ok))
    
    # Outputs
    outputs_ok = check_outputs()
    checks.append(('Generated outputs', outputs_ok))
    
    # README
    readme_ok = check_readme_completeness()
    checks.append(('README customization', readme_ok))
    
    # Git
    git_ok = check_git_repository()
    checks.append(('Git repository', git_ok))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for check_name, status in checks:
        status_str = "✅ PASS" if status else "❌ FAIL"
        print(f"{check_name:.<35} {status_str}")
    
    all_passed = all(status for _, status in checks)
    
    # Generate checklist
    generate_submission_checklist()
    
    # Final message
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("="*60)
        print("\nYour project is ready for submission!")
        print("\nNext steps:")
        print("1. Record and upload demo video")
        print("2. Update README with demo video link")
        print("3. Push to GitHub")
        print("4. Verify repository is public")
        print("5. Submit repository and demo links")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before submitting.")
        print("\nSee PROJECT_SUMMARY.md for detailed instructions.")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
