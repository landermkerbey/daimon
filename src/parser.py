from pathlib import Path


class OrgParser:
    """Parser for org-mode files."""
    
    def __init__(self, file_path):
        """Initialize parser with path to org file."""
        self.file_path = Path(file_path)
    
    def parse_headers(self):
        """Parse org file headers and return as dictionary."""
        headers = {}
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#+TITLE:'):
                    # Extract title after the colon and strip whitespace
                    title = line[8:].strip()
                    headers['title'] = title
                elif line.startswith('#+filetags:'):
                    # Extract filetags after the colon and parse tags
                    filetags_str = line[11:].strip()
                    # Split on colons and filter out empty strings
                    tags = [tag for tag in filetags_str.split(':') if tag]
                    headers['filetags'] = tags
        
        # Set defaults if not found
        if 'title' not in headers:
            headers['title'] = None
        if 'filetags' not in headers:
            headers['filetags'] = []
            
        return headers
