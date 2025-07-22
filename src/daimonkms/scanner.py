from pathlib import Path


class KnowledgeBaseScanner:
    """Scanner for finding and processing org-mode files in a knowledge base."""
    
    def __init__(self, root_directory):
        """Initialize scanner with root directory path."""
        self.root_directory = Path(root_directory)
    
    def scan_org_files(self):
        """Scan for org files in the knowledge base and return list of paths."""
        org_files = []
        
        # Handle case where directory doesn't exist
        if not self.root_directory.exists():
            return org_files
        
        # Walk through directory tree looking for .org files
        for file_path in self.root_directory.rglob("*.org"):
            if file_path.is_file():
                org_files.append(file_path)
        
        return org_files
