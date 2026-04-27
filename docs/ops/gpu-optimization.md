
# GPU-Accelerated PDF Parsing Configuration

This setup optimizes Onyx for local GPU-accelerated PDF parsing and embedding generation using your RTX 3090/3070.

## Key Optimizations:

1. **Local Embedding Models**: Uses lightweight but effective embedding models that can run efficiently on GPU
2. **Privacy Preservation**: All processing happens locally on your hardware
3. **Performance Optimization**: Leverages GPU acceleration for faster processing
4. **Memory Efficiency**: Configured for optimal memory usage on RTX cards

## Models Used:

- `all-MiniLM-L6-v2`: Fast, lightweight embedding model
- `nomic-embed-text`: Effective for optical character recognition in documents

## Benefits:

- Significantly faster PDF parsing compared to CPU-only processing
- Enhanced privacy - no external API calls for document processing
- Better resource utilization of your RTX GPU
- Reduced latency for document indexing operations

## Usage:

Once deployed, Onyx will automatically use the GPU-accelerated models for:
- PDF text extraction
- Document embedding generation
- Optical character recognition (OCR) for scanned documents
    