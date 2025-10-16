"""
Test script for the Simple Environmental Law RAG System (No OpenAI Required)
Run this to test the system functionality
"""

import os
import sys
from pathlib import Path

# Add the rag directory to Python path
sys.path.append(str(Path(__file__).parent))

from rag_simple import SimpleEnvironmentalLawRAG

def test_rag_system():
    """Test the RAG system functionality"""
    print("🧪 Testing Simple Environmental Law RAG System")
    print("=" * 60)
    print("✅ No API keys required!")
    print("✅ Runs entirely on your local machine!")
    print("")
    
    # Initialize RAG system
    rag = SimpleEnvironmentalLawRAG()
    
    # Test 1: Check if vector store exists
    print("\n1. Checking vector store...")
    if rag.load_existing_vectorstore():
        print("✅ Vector store loaded successfully")
    else:
        print("❌ No vector store found. Please run setup_rag_simple.py first.")
        return False
    
    # Test 2: Get system statistics
    print("\n2. Getting system statistics...")
    stats = rag.get_document_statistics()
    if "error" in stats:
        print(f"❌ Error getting statistics: {stats['error']}")
        return False
    else:
        print(f"✅ Statistics: {stats['total_chunks']} chunks from {stats['unique_documents']} documents")
        print(f"   Sources: {', '.join(stats['sources'])}")
    
    # Test 3: Test document search
    print("\n3. Testing document search...")
    search_results = rag.search_similar_documents("air pollution", k=3)
    if search_results:
        print(f"✅ Found {len(search_results)} similar documents")
        for i, result in enumerate(search_results[:2], 1):
            print(f"   {i}. {result['source']} (score: {result['similarity_score']:.3f})")
    else:
        print("❌ No search results found")
    
    # Test 4: Test question answering
    print("\n4. Testing question answering...")
    test_question = "What are the penalties for air pollution violations?"
    result = rag.query(test_question)
    
    if "error" in result:
        print(f"❌ Error in QA: {result['error']}")
    else:
        print(f"✅ Question answered successfully")
        print(f"   Question: {result['question']}")
        print(f"   Answer: {result['answer'][:150]}...")
        print(f"   Sources: {[doc['source'] for doc in result['source_documents']]}")
    
    # Test 5: Test different search queries
    print("\n5. Testing various search queries...")
    test_queries = [
        "water pollution",
        "forest conservation",
        "e-waste management",
        "environmental impact"
    ]
    
    for query in test_queries:
        results = rag.search_similar_documents(query, k=2)
        if results:
            print(f"✅ '{query}': Found {len(results)} results")
        else:
            print(f"❌ '{query}': No results found")
    
    print("\n🎉 RAG system testing completed!")
    return True

def test_web_interface():
    """Test if web interface can be started"""
    print("\n🌐 Testing web interface...")
    try:
        # Try to import Flask components
        from flask import Flask
        print("✅ Flask is available")
        
        # Check if templates directory exists
        templates_dir = Path(__file__).parent / 'templates'
        if templates_dir.exists():
            print("✅ Templates directory exists")
        else:
            print("❌ Templates directory not found")
            return False
        
        print("✅ Web interface should work. Run 'python rag/web_interface_simple.py' to start.")
        return True
        
    except ImportError as e:
        print(f"❌ Flask not available: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Environmental Law RAG System Test Suite")
    print("=" * 70)
    print("✅ No API keys required!")
    print("✅ Runs entirely on your local machine!")
    print("✅ Free and open-source!")
    print("")
    
    # Test the RAG system
    rag_success = test_rag_system()
    
    # Test web interface
    web_success = test_web_interface()
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"   RAG System: {'✅ PASS' if rag_success else '❌ FAIL'}")
    print(f"   Web Interface: {'✅ PASS' if web_success else '❌ FAIL'}")
    
    if rag_success and web_success:
        print("\n🎉 All tests passed! Your free RAG system is ready to use.")
        print("\nNext steps:")
        print("   1. Run 'python rag/setup_rag_simple.py' to initialize the system")
        print("   2. Run 'python rag/web_interface_simple.py' for web interface")
        print("   3. Or use the SimpleEnvironmentalLawRAG class programmatically")
        print("\n✅ No API keys needed!")
        print("✅ Runs entirely on your local machine!")
        print("✅ Completely free!")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        if not rag_success:
            print("   - Run 'python rag/setup_rag_simple.py' to initialize the system")
        if not web_success:
            print("   - Install Flask: pip install flask")

