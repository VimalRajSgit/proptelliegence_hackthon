"""
Setup script for the Simple Environmental Law RAG System (No OpenAI Required)
Run this script to initialize the RAG system with your PDF documents
"""

import os
import sys
from pathlib import Path

# Add the rag directory to Python path
sys.path.append(str(Path(__file__).parent))

from rag_simple import SimpleEnvironmentalLawRAG

def setup_rag_system():
    """Setup the RAG system with all PDF documents"""
    print("🌍 Simple Environmental Law RAG System Setup")
    print("=" * 60)
    print("✅ No API keys required!")
    print("✅ Runs entirely on your local machine!")
    print("✅ Free and open-source!")
    print("")
    
    # Initialize RAG system
    rag = SimpleEnvironmentalLawRAG()
    
    # Check if vector store already exists
    if rag.load_existing_vectorstore():
        print("✅ Existing vector store found!")
        stats = rag.get_document_statistics()
        print(f"📊 Current statistics:")
        print(f"   - Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   - Unique documents: {stats.get('unique_documents', 0)}")
        print(f"   - Sources: {', '.join(stats.get('sources', []))}")
        
        response = input("\nDo you want to rebuild the vector store? (y/N): ").strip().lower()
        if response != 'y':
            print("Using existing vector store.")
            return rag
    
    print("\n📚 Loading PDF documents...")
    documents = rag.load_pdf_documents()
    
    if not documents:
        print("❌ No PDF documents found in the 'rag' directory.")
        print("Please ensure your PDF files are in the 'rag' folder.")
        return None
    
    print(f"✅ Loaded {len(documents)} documents")
    
    print("\n🔪 Chunking documents...")
    chunks = rag.chunk_documents(chunk_size=1000, chunk_overlap=200)
    print(f"✅ Created {len(chunks)} chunks")
    
    print("\n🗄️ Creating vector store...")
    print("   This may take a few minutes for large documents...")
    rag.create_vectorstore(chunks)
    print("✅ Vector store created successfully!")
    
    # Get final statistics
    stats = rag.get_document_statistics()
    print(f"\n📊 Final statistics:")
    print(f"   - Total chunks: {stats.get('total_chunks', 0)}")
    print(f"   - Unique documents: {stats.get('unique_documents', 0)}")
    print(f"   - Sources: {', '.join(stats.get('sources', []))}")
    
    print("\n🎉 RAG system setup completed!")
    print("\n🚀 Next steps:")
    print("   1. Run 'python rag/rag_simple.py' for command-line interface")
    print("   2. Run 'python rag/web_interface_simple.py' for web interface")
    print("   3. Or use the SimpleEnvironmentalLawRAG class in your code")
    
    return rag

def test_queries(rag):
    """Test the RAG system with sample queries"""
    if not rag:
        print("❌ RAG system not initialized")
        return
    
    print("\n🧪 Testing with sample queries...")
    
    test_questions = [
        "What are the penalties for air pollution violations?",
        "What is the Water Prevention and Control of Pollution Act about?",
        "What are the requirements for e-waste management?",
        "What is the Forest Conservation Act?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        result = rag.query(question)
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Answer: {result['answer'][:150]}...")
            sources = [doc['source'] for doc in result['source_documents']]
            print(f"   📄 Sources: {', '.join(set(sources))}")

if __name__ == "__main__":
    # Setup the RAG system
    rag_system = setup_rag_system()
    
    if rag_system:
        # Test with sample queries
        test_response = input("\nDo you want to test with sample queries? (Y/n): ").strip().lower()
        if test_response != 'n':
            test_queries(rag_system)
        
        print(f"\n🎉 Setup complete! Your free RAG system is ready to use.")
        print(f"   - No API keys needed!")
        print(f"   - Runs entirely on your local machine!")
        print(f"   - Completely free and open-source!")

