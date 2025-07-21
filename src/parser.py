from pathlib import Path


class OrgParser:
    """Parser for org-mode files."""
    
    def __init__(self, file_path):
        """Initialize parser with path to org file."""
        self.file_path = Path(file_path)
    
    def parse_headers(self):
        """Parse org file headers and return as dictionary."""
        # For now, return empty dict - we're building the interface
        return {}
