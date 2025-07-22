import argparse
import sys
from pathlib import Path

from .config import Config
from .config_loader import find_config_file
from .scanner import KnowledgeBaseScanner
from .parser import OrgParser
from .chunking import ChunkingEngine
from .chroma_manager import ChromaManager


def get_config_path(args_config):
    """
    Determine which config file to use based on CLI args and discovery.
    
    Priority order:
    1. CLI --config argument (if provided)
    2. Automatic discovery via find_config_file()
    3. Error if none found
    """
    if args_config:
        # User explicitly specified config file
        config_path = Path(args_config)
        if not config_path.exists():
            print(f"Error: Specified config file not found: {config_path}")
            sys.exit(1)
        print(f"Using config file: {config_path} (specified via --config)")
        return str(config_path)
    
    # Try automatic discovery
    discovered_config = find_config_file()
    if discovered_config:
        print(f"Using config file: {discovered_config} (auto-discovered)")
        return str(discovered_config)
    
    # No config found anywhere
    print("Error: No configuration file found.")
    print("Searched for:")
    print("  - ./config/default.json")
    print("  - ~/.config/daimonkms/config.json")
    print("Please create a config file or specify one with --config")
    sys.exit(1)


def config_command(args_config, db_path_override=None):
    """Display current configuration settings."""
    output = []
    output.append("Knowledge Management System Configuration")
    output.append("=" * 50)
    
    try:
        config_path = get_config_path(args_config)
        config = Config(config_path)
        
        output.append(f"Config file: {config_path}")
        output.append("")
        output.append("Settings:")
        output.append(f"  Knowledge Base Root: {config.knowledge_base_root}")
        
        # Use override if provided, otherwise use config
        db_path = db_path_override if db_path_override else config.chroma_db_path
        output.append(f"  ChromaDB Path: {db_path}")
        if db_path_override:
            output.append(f"    (overridden from command line)")
        
        output.append(f"  Chunk Size: {config.chunk_size}")
        output.append(f"  Chunk Overlap: {config.chunk_overlap}")
        
        # Check if paths exist
        kb_path = Path(config.knowledge_base_root)
        db_path_obj = Path(db_path)
        
        output.append("")
        output.append("Path Status:")
        output.append(f"  Knowledge Base: {'✓ exists' if kb_path.exists() else '✗ not found'} ({kb_path.absolute()})")
        output.append(f"  ChromaDB: {'✓ exists' if db_path_obj.exists() else '✗ not found'} ({db_path_obj.absolute()})")
        
    except Exception as e:
        output.append(f"Error loading config: {e}")
    
    result = "\n".join(output)
    print(result)
    return result


def status_command(args_config, db_path_override=None):
    """Show knowledge base status and statistics."""
    output = []
    output.append("Knowledge Base Status")
    output.append("=" * 30)
    
    try:
        config_path = get_config_path(args_config)
        config = Config(config_path)
        output.append(f"Using config: {config_path}")
        output.append("")
        
        # Check knowledge base files
        scanner = KnowledgeBaseScanner(config.knowledge_base_root)
        org_files = scanner.scan_org_files()
        output.append(f"Source Files:")
        output.append(f"  Org files found: {len(org_files)}")
        if org_files:
            output.append(f"  Files:")
            for org_file in sorted(org_files):
                output.append(f"    - {org_file.name}")
        output.append("")
        
        # Check ChromaDB status
        db_path = db_path_override if db_path_override else config.chroma_db_path
        chroma = ChromaManager(db_path)
        output.append("ChromaDB Status:")
        
        try:
            # Try to get collections
            collections = chroma.client.list_collections()
            output.append(f"  Collections: {len(collections)}")
            
            if collections:
                for collection in collections:
                    count = collection.count()
                    output.append(f"    - {collection.name}: {count} documents")
            else:
                output.append("    No collections found")
                output.append("    Tip: Run 'daimon index' to create and populate collections")
                
        except Exception as e:
            output.append(f"  Database not accessible: {e}")
            output.append("  Tip: Run 'daimon index' to initialize the database")
            
    except Exception as e:
        output.append(f"Error checking status: {e}")
    
    result = "\n".join(output)
    print(result)
    return result


def search_command(query, args_config, results=5, collection="knowledge_base", db_path_override=None):
    """Search the knowledge base for relevant content."""
    output = []
    
    try:
        # Load configuration
        config_path = get_config_path(args_config)
        config = Config(config_path)
        
        # Initialize ChromaManager
        db_path = db_path_override if db_path_override else config.chroma_db_path
        chroma = ChromaManager(db_path)
    except Exception as e:
        output.append(f"Error loading configuration: {e}")
        result = "\n".join(output)
        print(result)
        return result
    
    output.append(f"Searching for: '{query}'")
    output.append(f"Collection: {collection}")
    output.append(f"Max results: {results}")
    output.append("-" * 60)
    
    # Query the collection
    search_results = chroma.query_collection(collection, query, n_results=results)
    
    # Check if we got any results
    if not search_results["documents"] or not search_results["documents"][0]:
        output.append("No results found.")
        output.append("\nTip: Make sure you've indexed your content first with 'daimon index'")
        result = "\n".join(output)
        print(result)
        return result
    
    # Display results
    documents = search_results["documents"][0]
    distances = search_results.get("distances", [None] * len(documents))[0] if search_results.get("distances") else [None] * len(documents)
    ids = search_results.get("ids", [None] * len(documents))[0] if search_results.get("ids") else [None] * len(documents)
    
    for i, (doc, distance, doc_id) in enumerate(zip(documents, distances, ids), 1):
        output.append(f"Result {i}:")
        if distance is not None:
            output.append(f"  Relevance: {1 - distance:.3f}" if distance <= 1 else f"  Distance: {distance:.3f}")
        if doc_id:
            output.append(f"  ID: {doc_id}")
        
        # Truncate very long content for readability
        content = doc.strip()
        if len(content) > 300:
            content = content[:300] + "..."
        
        output.append(f"  Content:")
        # Indent the content for better readability
        for line in content.split('\n'):
            output.append(f"    {line}")
        
        output.append("-" * 40)
    
    result = "\n".join(output)
    print(result)
    return result


def index_command(args_config, db_path_override=None):
    """Index org files into ChromaDB."""
    output = []
    
    try:
        # Load configuration
        config_path = get_config_path(args_config)
        config = Config(config_path)
        output.append(f"Loading config from {config_path}")
        
        # Initialize components
        scanner = KnowledgeBaseScanner(config.knowledge_base_root)
        chunker = ChunkingEngine(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
        
        # Use override if provided, otherwise use config
        db_path = db_path_override if db_path_override else config.chroma_db_path
        chroma = ChromaManager(db_path)
    except Exception as e:
        output.append(f"Error loading configuration: {e}")
        result = "\n".join(output)
        print(result)
        return result
    
    # Find all org files
    org_files = scanner.scan_org_files()
    output.append(f"Found {len(org_files)} org files to process")
    
    if not org_files:
        output.append("No org files found. Check your knowledge_base_root path in config.")
        result = "\n".join(output)
        print(result)
        return result
    
    # Create collection for this indexing run (this will clear existing data)
    collection_name = "knowledge_base"
    output.append(f"Creating/clearing collection: {collection_name}")
    chroma.clear_and_create_collection(collection_name)
    
    total_chunks = 0
    
    # Process each file
    for i, org_file in enumerate(org_files, 1):
        output.append(f"Processing {i}/{len(org_files)}: {org_file.name}")
        
        try:
            # Parse the org file
            parser = OrgParser(org_file)
            headers = parser.parse_headers()
            content = parser.parse_content()
            
            # Skip files with no content
            if not content.strip():
                output.append(f"  Skipping {org_file.name} - no content")
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
            
            output.append(f"  Stored {stored_count} chunks from {org_file.name}")
            
        except Exception as e:
            output.append(f"  Error processing {org_file.name}: {e}")
            continue
    
    output.append(f"\nIndexing complete! Stored {total_chunks} total chunks in collection '{collection_name}'")
    
    result = "\n".join(output)
    print(result)
    return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Daimon Knowledge Management System CLI")
    parser.add_argument('--config', help='Path to config file (overrides auto-discovery)')
    parser.add_argument('--db-path', help='Override ChromaDB path from config')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add config subcommand
    config_parser = subparsers.add_parser('config', help='Show configuration settings')
    
    # Add status subcommand
    status_parser = subparsers.add_parser('status', help='Show knowledge base status')
    
    # Add index subcommand
    index_parser = subparsers.add_parser('index', help='Index org files into ChromaDB')
    
    # Add search subcommand
    search_parser = subparsers.add_parser('search', help='Search the knowledge base')
    search_parser.add_argument('query', help='Search query text')
    search_parser.add_argument('--results', type=int, default=5,
                              help='Number of results to return (default: 5)')
    search_parser.add_argument('--collection', default='knowledge_base',
                              help='Collection to search (default: knowledge_base)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Dispatch to appropriate handler
    if args.command == 'config':
        config_command(args.config, args.db_path)
    elif args.command == 'status':
        status_command(args.config, args.db_path)
    elif args.command == 'index':
        index_command(args.config, args.db_path)
    elif args.command == 'search':
        search_command(args.query, args.config, args.results, args.collection, args.db_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
