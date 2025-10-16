# Environmental Law RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system for environmental law documents using ChromaDB and LangChain.

## 🌟 Features

- **PDF Processing**: Automatically processes multiple PDF documents
- **Intelligent Chunking**: Smart text splitting optimized for legal documents
- **Vector Storage**: Uses ChromaDB for efficient vector storage and retrieval
- **Semantic Search**: Find relevant information using natural language queries
- **Question Answering**: Get detailed answers with source citations
- **Web Interface**: User-friendly web interface for easy interaction
- **Multiple Embedding Models**: Support for various embedding models

## 📁 Project Structure

```
rag/
├── rag.py                 # Main RAG system implementation
├── setup_rag.py          # Setup script for initializing the system
├── web_interface.py      # Flask web interface
├── README.md             # This file
├── templates/
│   └── index.html        # Web interface template
├── chroma_db/            # ChromaDB storage (created automatically)
└── *.pdf                 # Your environmental law PDF documents
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup the RAG System

```bash
python rag/setup_rag.py
```

This will:
- Load all PDF documents from the `rag` directory
- Process and chunk the documents
- Create the vector database
- Set up the embedding model

### 3. Use the System

#### Command Line Interface
```bash
python rag/rag.py
```

#### Web Interface
```bash
python rag/web_interface.py
```
Then open your browser to `http://localhost:5000`

## 📚 Supported Documents

The system is designed to work with environmental law PDFs including:
- Air (Prevention and Control of Pollution) Act, 1981
- Water (Prevention and Control of Pollution) Act, 1974
- Environment (Protection) Act, 1986
- Forest (Conservation) Act, 1980
- E-Waste Management Rules, 2022
- And other environmental regulations

## 🔧 Configuration

### Environment Variables

Set your OpenAI API key for the best results:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Customization Options

You can customize the RAG system by modifying the parameters in `rag.py`:

```python
# Initialize with custom settings
rag = EnvironmentalLawRAG(
    pdf_directory="rag",           # Directory containing PDFs
    persist_directory="rag/chroma_db",  # Vector database location
    embedding_model="all-MiniLM-L6-v2"  # Embedding model
)

# Custom chunking parameters
chunks = rag.chunk_documents(
    chunk_size=1000,      # Size of each chunk
    chunk_overlap=200     # Overlap between chunks
)
```

## 💡 Usage Examples

### Basic Query
```python
from rag import EnvironmentalLawRAG

# Initialize the system
rag = EnvironmentalLawRAG()
rag.load_existing_vectorstore()

# Ask a question
result = rag.query("What are the penalties for air pollution violations?")
print(result['answer'])
```

### Search Similar Documents
```python
# Find similar documents
results = rag.search_similar_documents("water pollution control", k=5)
for result in results:
    print(f"Source: {result['source']}")
    print(f"Content: {result['content'][:200]}...")
```

### Get System Statistics
```python
stats = rag.get_document_statistics()
print(f"Total chunks: {stats['total_chunks']}")
print(f"Documents: {stats['unique_documents']}")
```

## 🌐 Web Interface Features

The web interface provides:
- **Question Answering**: Ask questions in natural language
- **Document Search**: Find relevant documents by keywords
- **Source Citations**: See which documents were used for answers
- **System Statistics**: View database statistics
- **Responsive Design**: Works on desktop and mobile

## 🔍 Query Examples

Try these example queries:
- "What are the penalties for air pollution violations?"
- "What is the Water Prevention and Control of Pollution Act about?"
- "What are the requirements for e-waste management?"
- "What is the Forest Conservation Act?"
- "What are the environmental impact assessment requirements?"
- "What are the penalties for violating environmental laws?"

## 🛠️ Advanced Features

### Custom Embedding Models
```python
# Use different embedding models
rag = EnvironmentalLawRAG(embedding_model="all-mpnet-base-v2")
```

### Custom Chunking Strategy
```python
# Custom chunking for legal documents
chunks = rag.chunk_documents(
    chunk_size=1500,      # Larger chunks for legal text
    chunk_overlap=300     # More overlap for context
)
```

### Filter by Document Source
```python
# Search only in specific documents
results = rag.vectorstore.similarity_search(
    "air pollution",
    filter={"source": "air_act-1981.pdf"}
)
```

## 📊 Performance Optimization

### For Large Document Collections
- Use larger chunk sizes (1500-2000 characters)
- Increase chunk overlap (300-400 characters)
- Consider using more powerful embedding models

### For Better Accuracy
- Use smaller chunk sizes (800-1000 characters)
- Increase the number of retrieved documents (k=7-10)
- Fine-tune the prompt template

## 🐛 Troubleshooting

### Common Issues

1. **"No PDF files found"**
   - Ensure PDF files are in the `rag` directory
   - Check file permissions

2. **"Error loading embeddings model"**
   - Install required dependencies: `pip install sentence-transformers`
   - Check internet connection for model download

3. **"QA chain not initialized"**
   - Set your OpenAI API key: `export OPENAI_API_KEY="your-key"`
   - Or use a different LLM provider

4. **"Vector store not initialized"**
   - Run `python rag/setup_rag.py` first
   - Check if the `chroma_db` directory exists

### Performance Issues

- **Slow queries**: Reduce chunk size or use GPU for embeddings
- **Memory issues**: Process documents in batches
- **Storage issues**: Clean up old vector stores

## 🔒 Security Considerations

- Keep your OpenAI API key secure
- Don't commit API keys to version control
- Use environment variables for sensitive data
- Consider using local LLMs for sensitive documents

## 📈 Monitoring and Maintenance

### Regular Maintenance
- Monitor vector store size
- Update embedding models periodically
- Clean up old or irrelevant documents
- Backup the vector database

### Performance Monitoring
- Track query response times
- Monitor memory usage
- Check embedding model performance
- Analyze query patterns

## 🤝 Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the code documentation
- Open an issue on GitHub
- Contact the development team

---

**Happy querying! 🌍📚**

