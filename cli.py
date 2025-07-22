import argparse
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append('src')

from config import Config
from scanner import KnowledgeBaseScanner
from parser import OrgParser
from chunking import ChunkingEngine
from chroma_manager import ChromaManager


def index_command(config_path):
    """Index org files into ChromaDB."""
    # Load configuration
    config = Config(config_path)
    print(f"Loading config from {config_path}")
    
    # Initialize components
    scanner = KnowledgeBaseScanner(config.knowledge_base_root)
    chunker = ChunkingEngine(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    chroma = ChromaManager(config.chroma_db_path)
    
    # Find all org files
    org_files = scanner.scan_org_files()
    print(f"Found {len(org_files)} org files to process")
    
    if not org_files:
        print("No org files found. Check your knowledge_base_root path in config.")
        return
    
    # Create collection for this indexing run
    collection_name = "knowledge_base"
    chroma.create_collection(collection_name)
    
    total_chunks = 0
    
    # Process each file
    for i, org_file in enumerate(org_files, 1):
        print(f"Processing {i}/{len(org_files)}: {org_file.name}")
        
        try:
            # Parse the org file
            parser = OrgParser(org_file)
            headers = parser.parse_headers()
            content = parser.parse_content()
            
            # Skip files with no content
            if not content.strip():
                print(f"  Skipping {org_file.name} - no content")
                continue
            
            # Chunk the content
            chunks = chunker.chunk_content(content)
            
            # Store chunks in ChromaDB
            stored_count = chroma.store_chunks(collection_name, chunks)
            total_chunks += stored_count
            
            print(f"  Stored {stored_count} chunks from {org_file.name}")
            
        except Exception as e:
            print(f"  Error processing {org_file.name}: {e}")
            continue
    
    print(f"\nIndexing complete! Stored {total_chunks} total chunks in collection '{collection_name}'")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Knowledge Management System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add index subcommand
    index_parser = subparsers.add_parser('index', help='Index org files into ChromaDB')
    index_parser.add_argument('--config', default='config/default.json', 
                             help='Path to config file (default: config/default.json)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Dispatch to appropriate handler
    if args.command == 'index':
        index_command(args.config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
