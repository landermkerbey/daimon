class ChunkingEngine:
    """Engine for splitting content into chunks for vector embedding."""
    
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """Initialize chunking engine with size and overlap parameters."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_content(self, content):
        """Split content into chunks and return as list."""
        # For now, just return the content as a single chunk - building interface
        return [content]
