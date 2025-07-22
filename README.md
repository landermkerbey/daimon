# Knowledge Management System

A comprehensive knowledge management system with AI integration that processes org-mode files, creates vector embeddings for semantic search, and provides a command-line interface for managing your personal knowledge base.

## Overview

This system follows a local-first architecture that:
- Processes collections of org-mode files containing personal knowledge (notes, journals, creative writing, etc.)
- Creates vector embeddings for semantic search using ChromaDB
- Supports multiple AI agents that can query and synthesize knowledge across domains
- Maintains modular, testable architecture for future AI agent integration

## Features

### Core Functionality
- **Org-mode File Processing**: Parse org files with support for headers, properties, filetags, and content extraction
- **Semantic Search**: Vector-based search using ChromaDB for finding relevant content across your knowledge base
- **Content Chunking**: Intelligent splitting of content into chunks with configurable size and overlap
- **Metadata Extraction**: Automatic extraction of titles, tags, IDs, and other metadata from org files
- **Command-Line Interface**: Full CLI for indexing, searching, and managing your knowledge base

### File Organization
The system supports a hierarchical directory structure with a 3-axis tagging system:
- **[domain]** - Subject area (e.g., mathematics, cooking, philosophy)
- **[form]** - Content type (e.g., reference, journal, creative)
- **[granularity]** - Detail level (e.g., overview, detailed, specific-topic)

Example: `#mathematics #reference #set-theory`

## Installation

### Prerequisites
- Python 3.8+
- ChromaDB (install via pip)

### Setup
1. Clone the repository
2. Install ChromaDB:
   ```bash
   pip install --user chromadb
   ```
3. Verify installation:
   ```bash
   python cli.py config
   ```

## Project Structure

```
knowledge_system/
├── src/                    # Core modules
│   ├── config.py          # Configuration management
│   ├── scanner.py         # File discovery
│   ├── parser.py          # Org-mode parsing
│   ├── chunking.py        # Content chunking
│   └── chroma_manager.py  # Vector database operations
├── tests/                 # Test suite
│   ├── fixtures/          # Test data
│   └── test_*.py         # Test files
├── config/
│   └── default.json      # Default configuration
├── knowledge_base/       # Your org files go here
├── cli.py               # Command-line interface
└── pytest.ini          # Test configuration
```

## Configuration

The system uses `config/default.json` for configuration:

```json
{
  "knowledge_base_root": "./knowledge_base",
  "chroma_db_path": "./local_cache/chromadb",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

- **knowledge_base_root**: Directory containing your org files
- **chroma_db_path**: Where ChromaDB stores vector embeddings
- **chunk_size**: Maximum characters per content chunk
- **chunk_overlap**: Characters of overlap between chunks

## Usage

### Command-Line Interface

The CLI provides four main commands:

#### 1. View Configuration
```bash
python cli.py config
```
Shows current configuration settings and path status.

#### 2. Check System Status
```bash
python cli.py status
```
Displays:
- Number of org files found
- ChromaDB collections and document counts
- System health information

#### 3. Index Your Knowledge Base
```bash
python cli.py index
```
Processes all org files in your knowledge base:
- Scans for `.org` files
- Extracts headers and content
- Chunks content appropriately
- Stores in ChromaDB with metadata

Example output:
```
Loading config from config/default.json
Found 4 org files to process
Creating/clearing collection: knowledge_base
Processing 1/4: machine-learning.org
  Stored 3 chunks from machine-learning.org
Processing 2/4: cooking-recipes.org
  Stored 4 chunks from cooking-recipes.org
...
Indexing complete! Stored 15 total chunks in collection 'knowledge_base'
```

#### 4. Search Your Knowledge
```bash
python cli.py search "your query here"
```

Search options:
- `--results N`: Number of results to return (default: 5)
- `--collection NAME`: Search specific collection (default: knowledge_base)

Example:
```bash
python cli.py search "machine learning algorithms" --results 3
```

### Advanced Options

All commands support:
- `--config PATH`: Use custom configuration file
- `--db-path PATH`: Override ChromaDB path (useful for testing)

Example:
```bash
python cli.py index --config my-config.json --db-path /tmp/test-db
```

## Org-Mode File Format

Your org files should follow this structure:

```org
:PROPERTIES:
:ID:       unique-uuid-here
:END:
#+TITLE: Your Note Title
#+filetags: :domain:form:granularity:

* Main Heading

Your content goes here. The system will extract:
- The title from #+TITLE
- Tags from #+filetags
- The unique ID from PROPERTIES
- All content (excluding headers and properties)

** Subheading

More content with [[file:other-note.org][links to other notes]].
```

## Example Workflow

1. **Setup**: Place your org files in the `knowledge_base/` directory
2. **Index**: Run `python cli.py index` to process all files
3. **Search**: Use `python cli.py search "topic"` to find relevant content
4. **Monitor**: Check `python cli.py status` to see system state

## Development and Testing

### Running Tests
```bash
pytest tests/
```

### Test Coverage
The test suite includes:
- Unit tests for all core components
- Integration tests for the full pipeline
- CLI command testing with temporary databases
- Automated cleanup and isolation

### Architecture

The system follows a modular architecture:

- **Config**: JSON-based configuration management
- **Scanner**: Discovers org files in directory trees
- **Parser**: Extracts headers, metadata, and content from org files
- **ChunkingEngine**: Splits content into overlapping chunks
- **ChromaManager**: Handles vector database operations
- **CLI**: Command-line interface tying everything together

## Troubleshooting

### Common Issues

**No results when searching:**
- Ensure you've run `python cli.py index` first
- Check that your org files are in the configured knowledge_base_root
- Verify ChromaDB path is accessible

**Import errors:**
- Make sure ChromaDB is installed: `pip install --user chromadb`
- Check that all source files are present in the `src/` directory

**Configuration problems:**
- Run `python cli.py config` to verify settings
- Ensure `config/default.json` exists and is valid JSON

### Getting Help

1. Check system status: `python cli.py status`
2. Verify configuration: `python cli.py config`
3. Run tests to ensure system integrity: `pytest tests/`

## Future Development

This system is designed for extensibility:
- AI agent integration for automated knowledge synthesis
- Multi-device synchronization
- Advanced search filters and ranking
- Web interface
- Integration with other knowledge management tools

The modular architecture and comprehensive test suite support rapid iteration and feature development.
