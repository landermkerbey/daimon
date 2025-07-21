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
    """Test that KnowledgeBaseScanner can be created - this should fail for now."""
    from scanner import KnowledgeBaseScanner
    scanner = KnowledgeBaseScanner("./knowledge_base")
    assert scanner is not None, "Should be able to create KnowledgeBaseScanner instance"
