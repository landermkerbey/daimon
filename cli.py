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


def search_command(query, config_path, results=5, collection="knowledge_base"):
    """Search the knowledge base for relevant content."""
    # Load configuration
    config = Config(config_path)
    
    # Initialize ChromaManager
    chroma = ChromaManager(config.chroma_db_path)
    
    print(f"Searching for: '{query}'")
    print(f"Collection: {collection}")
    print(f"Max results: {results}")
    print("-" * 60)
    
    # Query the collection
    search_results = chroma.query_collection(collection, query, n_results=results)
    
    # Check if we got any results
    if not search_results["documents"] or not search_results["documents"][0]:
        print("No results found.")
        print("\nTip: Make sure you've indexed your content first with 'python cli.py index'")
        return
    
    # Display results
    documents = search_results["documents"][0]
    distances = search_results.get("distances", [None] * len(documents))[0] if search_results.get("distances") else [None] * len(documents)
    ids = search_results.get("ids", [None] * len(documents))[0] if search_results.get("ids") else [None] * len(documents)
    
    for i, (doc, distance, doc_id) in enumerate(zip(documents, distances, ids), 1):
        print(f"Result {i}:")
        if distance is not None:
            print(f"  Relevance: {1 - distance:.3f}" if distance <= 1 else f"  Distance: {distance:.3f}")
        if doc_id:
            print(f"  ID: {doc_id}")
        
        # Truncate very long content for readability
        content = doc.strip()
        if len(content) > 300:
            content = content[:300] + "..."
        
        print(f"  Content:")
        # Indent the content for better readability
        for line in content.split('\n'):
            print(f"    {line}")
        
        print("-" * 40)


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
    
    # Create collection for this indexing run (this will clear existing data)
    collection_name = "knowledge_base"
    print(f"Creating/clearing collection: {collection_name}")
    chroma.clear_and_create_collection(collection_name)
    
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
            
            # Store chunks in ChromaDB with file-specific metadata
            stored_count = chroma.store_chunks_with_metadata(
                collection_name, 
                chunks, 
                org_file.stem,  # filename without extension
                headers
            )
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
    
    # Add search subcommand
    search_parser = subparsers.add_parser('search', help='Search the knowledge base')
    search_parser.add_argument('query', help='Search query text')
    search_parser.add_argument('--config', default='config/default.json',
                              help='Path to config file (default: config/default.json)')
    search_parser.add_argument('--results', type=int, default=5,
                              help='Number of results to return (default: 5)')
    search_parser.add_argument('--collection', default='knowledge_base',
                              help='Collection to search (default: knowledge_base)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Dispatch to appropriate handler
    if args.command == 'index':
        index_command(args.config)
    elif args.command == 'search':
        search_command(args.query, args.config, args.results, args.collection)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
