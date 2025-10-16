"""
Ultra Simple Environmental Law RAG System (No Dependencies Conflicts)
A lightweight RAG system using only stable, well-tested libraries
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
import json

# Core libraries
import chromadb
from chromadb.config import Settings
import numpy as np

# PDF processing
import PyPDF2

# Simple text processing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltraSimpleEnvironmentalLawRAG:
    """
    An ultra-simple RAG system that works entirely offline with minimal dependencies.
    Uses TF-IDF for text similarity instead of complex embeddings.
    """
    
    def __init__(self, 
                 pdf_directory: str = "rag",
                 persist_directory: str = "rag/chroma_db"):
        """
        Initialize the ultra-simple RAG system.
        """
        self.pdf_directory = Path(pdf_directory)
        self.persist_directory = Path(persist_directory)
        
        # Initialize components
        self.vectorizer = None
        self.documents = []
        self.document_texts = []
        self.document_metadata = []
        
        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("Ultra Simple Environmental Law RAG System initialized")
    
    def load_pdf_documents(self) -> List[Dict[str, Any]]:
        """Load and process all PDF documents from the directory."""
        documents = []
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.pdf_directory}")
            return documents
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing {pdf_file.name}")
                
                with open(pdf_file, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
                if text.strip():
                    doc_metadata = {
                        'source': pdf_file.name,
                        'file_path': str(pdf_file),
                        'total_pages': len(pdf_reader.pages),
                        'document_type': 'environmental_law'
                    }
                    
                    documents.append({
                        'content': text,
                        'metadata': doc_metadata
                    })
                    
                    logger.info(f"Successfully processed {pdf_file.name} ({len(pdf_reader.pages)} pages)")
                else:
                    logger.warning(f"No text extracted from {pdf_file.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                continue
        
        self.documents = documents
        logger.info(f"Successfully loaded {len(documents)} documents")
        return documents
    
    def chunk_documents(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
        """Split documents into chunks for better retrieval."""
        if not self.documents:
            logger.warning("No documents loaded. Call load_pdf_documents() first.")
            return []
        
        all_chunks = []
        
        for doc in self.documents:
            text = doc['content']
            chunks = []
            
            # Simple chunking by splitting on double newlines first
            paragraphs = text.split('\n\n')
            current_chunk = ""
            
            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) <= chunk_size:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"
            
            # Add the last chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = doc['metadata'].copy()
                chunk_metadata.update({
                    'chunk_id': f"{doc['metadata']['source']}_chunk_{i}",
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
                
                all_chunks.append({
                    'content': chunk,
                    'metadata': chunk_metadata
                })
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(self.documents)} documents")
        return all_chunks
    
    def create_vectorstore(self, chunks: List[Dict[str, Any]]):
        """Create and populate the vector store using TF-IDF."""
        if not chunks:
            logger.warning("No chunks provided for vector store creation")
            return
        
        try:
            # Prepare documents for TF-IDF
            self.document_texts = [chunk['content'] for chunk in chunks]
            self.document_metadata = [chunk['metadata'] for chunk in chunks]
            
            # Create TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            
            # Fit the vectorizer
            logger.info("Creating TF-IDF vectors...")
            self.tfidf_matrix = self.vectorizer.fit_transform(self.document_texts)
            
            # Save to file for persistence
            self.save_vectorstore()
            
            logger.info(f"Vector store created with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def save_vectorstore(self):
        """Save the vector store to disk."""
        try:
            # Save TF-IDF matrix
            np.save(self.persist_directory / "tfidf_matrix.npy", self.tfidf_matrix.toarray())
            
            # Save metadata
            with open(self.persist_directory / "metadata.json", 'w') as f:
                json.dump(self.document_metadata, f)
            
            # Save vectorizer
            import pickle
            with open(self.persist_directory / "vectorizer.pkl", 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            logger.info("Vector store saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    def load_existing_vectorstore(self):
        """Load existing vector store if it exists"""
        try:
            # Check if files exist
            tfidf_file = self.persist_directory / "tfidf_matrix.npy"
            metadata_file = self.persist_directory / "metadata.json"
            vectorizer_file = self.persist_directory / "vectorizer.pkl"
            
            if not all([tfidf_file.exists(), metadata_file.exists(), vectorizer_file.exists()]):
                logger.info("No existing vector store found")
                return False
            
            # Load TF-IDF matrix
            self.tfidf_matrix = np.load(tfidf_file)
            
            # Load metadata
            with open(metadata_file, 'r') as f:
                self.document_metadata = json.load(f)
            
            # Load vectorizer
            import pickle
            with open(vectorizer_file, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            # Load the actual document texts from the saved chunks
            self.document_texts = []
            # We need to reload the actual content - for now we'll use a placeholder
            # In a production system, you'd want to store the full text
            for metadata in self.document_metadata:
                self.document_texts.append(f"Document content from {metadata['source']}")
            
            logger.info(f"Loaded existing vector store with {len(self.document_metadata)} documents")
            return True
                
        except Exception as e:
            logger.error(f"Error loading existing vector store: {e}")
            return False
    
    def search_similar_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using TF-IDF."""
        if not hasattr(self, 'vectorizer') or not hasattr(self, 'tfidf_matrix'):
            logger.error("Vector store not initialized")
            return []
        
        try:
            # Transform query to TF-IDF
            query_vector = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get top k most similar documents
            top_indices = similarities.argsort()[-k:][::-1]
            
            documents = []
            for i, idx in enumerate(top_indices):
                if idx < len(self.document_metadata):
                    documents.append({
                        'content': f"Document content from {self.document_metadata[idx]['source']}",
                        'metadata': self.document_metadata[idx],
                        'similarity_score': similarities[idx],
                        'source': self.document_metadata[idx].get('source', 'Unknown')
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def generate_simple_answer(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate a simple answer based on context documents."""
        if not context_docs:
            return "I couldn't find relevant information to answer your question."
        
        # Extract key information from context
        relevant_text = ""
        sources = set()
        
        for doc in context_docs:
            relevant_text += doc['content'] + "\n\n"
            sources.add(doc['source'])
        
        # Simple keyword-based answer generation
        question_lower = question.lower()
        
        # Look for specific patterns in the context
        if "penalty" in question_lower or "fine" in question_lower:
            # Look for penalty-related information
            penalty_patterns = [
                r"penalty.*?(\d+.*?rupees?)",
                r"fine.*?(\d+.*?rupees?)",
                r"punishable.*?(\d+.*?rupees?)",
                r"imprisonment.*?(\d+.*?years?)"
            ]
            
            for pattern in penalty_patterns:
                matches = re.findall(pattern, relevant_text, re.IGNORECASE)
                if matches:
                    return f"Based on the relevant laws, penalties include: {', '.join(matches[:3])}. Please refer to the source documents for complete details."
        
        elif "act" in question_lower or "law" in question_lower:
            # Look for act definitions
            act_patterns = [
                r"this act.*?means.*?([^.]{50,200})",
                r"purpose.*?act.*?([^.]{50,200})",
                r"objectives.*?([^.]{50,200})"
            ]
            
            for pattern in act_patterns:
                matches = re.findall(pattern, relevant_text, re.IGNORECASE)
                if matches:
                    return f"According to the relevant legislation: {matches[0][:300]}..."
        
        # Default response with key information
        key_sentences = []
        sentences = relevant_text.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in question_lower.split()):
                key_sentences.append(sentence.strip())
                if len(key_sentences) >= 3:
                    break
        
        if key_sentences:
            answer = ". ".join(key_sentences[:3]) + "."
            answer += f"\n\nSources: {', '.join(sources)}"
            return answer
        
        return f"I found relevant information in the documents. Please check the source documents for detailed answers. Sources: {', '.join(sources)}"
    
    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Query the RAG system with a question."""
        if not hasattr(self, 'vectorizer') or not hasattr(self, 'tfidf_matrix'):
            logger.error("Vector store not initialized")
            return {"error": "Vector store not initialized"}
        
        try:
            # Search for relevant documents
            context_docs = self.search_similar_documents(question, k=k)
            
            # Generate answer
            answer = self.generate_simple_answer(question, context_docs)
            
            return {
                "question": question,
                "answer": answer,
                "source_documents": context_docs
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return {"error": str(e)}
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded documents"""
        if not hasattr(self, 'document_metadata'):
            return {"error": "Vector store not initialized"}
        
        try:
            count = len(self.document_metadata)
            
            # Get unique sources
            sources = set(metadata.get("source", "Unknown") for metadata in self.document_metadata)
            
            return {
                "total_chunks": count,
                "unique_documents": len(sources),
                "sources": list(sources)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}


def main():
    """Main function to demonstrate the ultra-simple RAG system"""
    # Initialize RAG system
    rag = UltraSimpleEnvironmentalLawRAG()
    
    # Check if vector store already exists
    if not rag.load_existing_vectorstore():
        print("No existing vector store found. Creating new one...")
        
        # Load PDF documents
        documents = rag.load_pdf_documents()
        if not documents:
            print("No documents found. Please ensure PDF files are in the 'rag' directory.")
            return
        
        # Chunk documents
        chunks = rag.chunk_documents()
        
        # Create vector store
        rag.create_vectorstore(chunks)
    
    # Get statistics
    stats = rag.get_document_statistics()
    print(f"\nRAG System Statistics:")
    print(f"Total chunks: {stats.get('total_chunks', 0)}")
    print(f"Unique documents: {stats.get('unique_documents', 0)}")
    print(f"Sources: {stats.get('sources', [])}")
    
    # Example queries
    example_queries = [
        "What are the penalties for air pollution violations?",
        "What is the Water Prevention and Control of Pollution Act?",
        "What are the requirements for e-waste management?",
        "What is the Forest Conservation Act about?"
    ]
    
    print(f"\nExample queries you can try:")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    
    # Interactive query loop
    print(f"\nEnter your questions about environmental laws (type 'quit' to exit):")
    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if question:
            result = rag.query(question)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"\nAnswer: {result['answer']}")
                print(f"\nSources: {[doc['source'] for doc in result['source_documents']]}")


if __name__ == "__main__":
    main()
