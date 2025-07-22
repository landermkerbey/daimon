import pytest
from pathlib import Path
import sys
sys.path.append('src')

from config import Config
from parser import OrgParser


def test_placeholder_should_fail():
    """Placeholder test that fails - will be replaced with real functionality."""
    # This test intentionally fails to show pytest is working
    assert False, "This is a placeholder test that should fail"


def test_basic_imports():
    """Test that basic Python functionality works."""
    assert True


def test_sample_org_file_exists(sample_org_file):
    """Test that our sample org file fixture works."""
    assert sample_org_file.exists(), f"Sample org file should exist at {sample_org_file}"
    assert sample_org_file.suffix == ".org", "File should have .org extension"


def test_config_loads():
    """Test that configuration loads successfully."""
    config = Config()
    assert config.knowledge_base_root == "./knowledge_base"
    assert config.chunk_size == 1000


def test_org_parser_creation(sample_org_file):
    """Test that OrgParser can be created and returns a dictionary."""
    parser = OrgParser(sample_org_file)
    headers = parser.parse_headers()
    assert isinstance(headers, dict), "parse_headers should return a dictionary"


def test_org_parser_extracts_title(sample_org_file):
    """Test that OrgParser extracts title - this should fail for now."""
    parser = OrgParser(sample_org_file)
    headers = parser.parse_headers()
    assert headers['title'] == "Sample Test Note", "Should extract title from #+TITLE line"


def test_org_parser_extracts_filetags(sample_org_file):
    """Test that OrgParser extracts filetags."""
    parser = OrgParser(sample_org_file)
    headers = parser.parse_headers()
    assert headers['filetags'] == ["test", "reference", "sample"], "Should extract filetags as list from #+filetags line"


def test_org_parser_extracts_id(sample_org_file):
    """Test that OrgParser extracts ID from PROPERTIES drawer."""
    parser = OrgParser(sample_org_file)
    headers = parser.parse_headers()
    assert headers['id'] == "12345678-1234-5678-9abc-123456789012", "Should extract ID from PROPERTIES drawer"


def test_org_parser_extracts_content(sample_org_file):
    """Test that OrgParser extracts main content."""
    parser = OrgParser(sample_org_file)
    content = parser.parse_content()
    assert "Main Topic" in content, "Should extract main content body"
    assert "This is some sample content" in content, "Should include paragraph text"
    assert "#+TITLE:" not in content, "Should not include title header"
    assert ":PROPERTIES:" not in content, "Should not include properties drawer"


def test_chunking_engine_creation():
    """Test that ChunkingEngine can be created."""
    from chunking import ChunkingEngine
    engine = ChunkingEngine()
    assert engine is not None, "Should be able to create ChunkingEngine instance"


def test_chunking_engine_splits_content():
    """Test that ChunkingEngine splits long content."""
    from chunking import ChunkingEngine
    engine = ChunkingEngine(chunk_size=50)
    long_content = "This is a very long piece of content that should definitely be split into multiple chunks when processed by the chunking engine because it exceeds the specified chunk size limit."
    chunks = engine.chunk_content(long_content)
    assert len(chunks) > 1, "Should split long content into multiple chunks"
    assert all(len(chunk) <= 50 for chunk in chunks), "Each chunk should respect size limit"


def test_scanner_creation():
    """Test that KnowledgeBaseScanner can be created."""
    from scanner import KnowledgeBaseScanner
    scanner = KnowledgeBaseScanner("./knowledge_base")
    assert scanner is not None, "Should be able to create KnowledgeBaseScanner instance"


def test_scanner_finds_org_files():
    """Test that KnowledgeBaseScanner finds org files."""
    from scanner import KnowledgeBaseScanner
    scanner = KnowledgeBaseScanner("tests/fixtures/")
    org_files = scanner.scan_org_files()
    assert len(org_files) > 0, "Should find at least one org file"
    assert any("sample.org" in str(f) for f in org_files), "Should find sample.org file"


def test_chroma_manager_creation():
    """Test that ChromaManager can be created."""
    from chroma_manager import ChromaManager
    manager = ChromaManager("./local_cache/chromadb")
    assert manager is not None, "Should be able to create ChromaManager instance"


def test_end_to_end_pipeline(sample_org_file, temp_dir):
    """Test end-to-end pipeline processing."""
    from config import Config
    from scanner import KnowledgeBaseScanner
    from parser import OrgParser
    from chunking import ChunkingEngine
    from chroma_manager import ChromaManager
    
    # Initialize components with temporary ChromaDB path
    config = Config()
    scanner = KnowledgeBaseScanner("tests/fixtures/")
    parser = OrgParser(sample_org_file)
    chunker = ChunkingEngine(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    chroma = ChromaManager(temp_dir / "test_chromadb")
    
    # Process the pipeline
    content = parser.parse_content()
    chunks = chunker.chunk_content(content)
    collection = chroma.create_collection("test_collection")
    stored_count = chroma.store_chunks("test_collection", chunks)
    
    # Verify the pipeline worked
    assert len(chunks) > 0, "Should have created chunks from content"
    assert stored_count == len(chunks), "Should have stored all chunks"
    assert collection.count() == len(chunks), "Collection should contain all chunks"


def test_chroma_manager_query(temp_dir):
    """Test that ChromaManager can query stored content."""
    from chroma_manager import ChromaManager
    
    # Create manager and store test content
    chroma = ChromaManager(temp_dir / "test_chromadb")
    test_chunks = [
        "This is about machine learning and AI",
        "Python programming is very useful",
        "Organic chemistry involves carbon compounds"
    ]
    
    chroma.create_collection("test_query")
    chroma.store_chunks("test_query", test_chunks)
    
    # Query for content
    results = chroma.query_collection("test_query", "artificial intelligence")
    
    # Verify we get results
    assert len(results["documents"]) > 0, "Should return query results"
    assert len(results["documents"][0]) > 0, "Should have at least one document result"


def test_query_sample_content(sample_org_file, temp_dir):
    """Test querying real org file content through full pipeline."""
    from config import Config
    from parser import OrgParser
    from chunking import ChunkingEngine
    from chroma_manager import ChromaManager
    
    # Process sample org file through pipeline
    config = Config()
    parser = OrgParser(sample_org_file)
    chunker = ChunkingEngine(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    chroma = ChromaManager(temp_dir / "sample_chromadb")
    
    # Store the content
    content = parser.parse_content()
    chunks = chunker.chunk_content(content)
    chroma.create_collection("sample_collection")
    chroma.store_chunks("sample_collection", chunks)
    
    # Query for content that exists in the sample file
    results = chroma.query_collection("sample_collection", "Main Topic")
    
    # Verify we get relevant results
    assert len(results["documents"]) > 0, "Should find matching content"
    assert len(results["documents"][0]) > 0, "Should return at least one document"
    # Check that the returned content contains expected text
    returned_docs = results["documents"][0]
    assert any("Main Topic" in doc for doc in returned_docs), "Should find content containing 'Main Topic'"


def test_cli_index_command():
    """Test that CLI index command works."""
    import sys
    import os
    from unittest.mock import patch
    
    # Add project root to path so we can import cli
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Mock sys.argv to simulate command line arguments
    with patch.object(sys, 'argv', ['cli.py', 'index']):
        # Import and test the CLI
        import cli
        try:
            cli.main()
            # If we get here without exception, the test passes
            assert True, "CLI index command should run without crashing"
        except SystemExit:
            # argparse calls sys.exit, which is normal behavior
            assert True, "CLI completed normally"


def test_cli_index_with_temp_db(tmp_path):
    """Test CLI index command with temporary database."""
    import sys
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    import cli
    
    # Create temporary ChromaDB path
    temp_db = tmp_path / "test_chromadb"
    
    # Run index command with temporary database
    result = cli.index_command("config/default.json", str(temp_db))
    
    # Verify output contains expected information
    assert "Loading config from config/default.json" in result
    assert "org files to process" in result
    assert "Creating/clearing collection: knowledge_base" in result
    assert "Indexing complete!" in result


def test_cli_search_with_temp_db(tmp_path):
    """Test CLI search command with temporary database."""
    import sys
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    import cli
    
    # Create temporary ChromaDB path
    temp_db = tmp_path / "test_chromadb"
    
    # First index some content
    index_result = cli.index_command("config/default.json", str(temp_db))
    assert "Indexing complete!" in index_result
    
    # Then search for content
    search_result = cli.search_command("machine learning", "config/default.json", 3, "knowledge_base", str(temp_db))
    
    # Verify search output
    assert "Searching for: 'machine learning'" in search_result
    assert "Collection: knowledge_base" in search_result
    # Should find results since we indexed content
    assert ("No results found" not in search_result) or ("Result 1:" in search_result)


def test_cli_status_with_temp_db(tmp_path):
    """Test CLI status command with temporary database."""
    import sys
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    import cli
    
    # Create temporary ChromaDB path
    temp_db = tmp_path / "test_chromadb"
    
    # Check status before indexing
    status_result = cli.status_command("config/default.json", str(temp_db))
    assert "Knowledge Base Status" in status_result
    assert "Org files found:" in status_result
    
    # Index some content
    cli.index_command("config/default.json", str(temp_db))
    
    # Check status after indexing
    status_result = cli.status_command("config/default.json", str(temp_db))
    assert "knowledge_base:" in status_result
    assert "documents" in status_result


def test_cli_config_with_db_override(tmp_path):
    """Test CLI config command with database path override."""
    import sys
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    import cli
    
    # Create temporary ChromaDB path
    temp_db = tmp_path / "test_chromadb"
    
    # Run config command with database override
    result = cli.config_command("config/default.json", str(temp_db))
    
    # Verify output shows override
    assert "Knowledge Management System Configuration" in result
    assert str(temp_db) in result
    assert "overridden from command line" in result
