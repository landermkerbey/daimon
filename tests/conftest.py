import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_org_content():
    """Sample org-mode content for testing."""
    return """* Sample Heading
#mathematics #reference #set-theory

This is sample org content for testing.

** Subheading
Some more content here.
"""


@pytest.fixture
def sample_org_file():
    """Path to sample org file for testing."""
    return Path(__file__).parent / "fixtures" / "sample.org"
