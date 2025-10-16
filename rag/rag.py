"""
Environmental Law RAG System
A comprehensive Retrieval-Augmented Generation system for environmental law PDFs
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Core libraries
import chromadb
from chromadb.config import Settings
import numpy as np
import pandas as pd

# LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# PDF processing
import PyPDF2
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvironmentalLawRAG:
    """
    A RAG system specifically designed for environmental law documents.
    Uses ChromaDB for vector storage and retrieval.
    """
    
    def __init__(self, 
                 pdf_directory: str = "rag",
                 persist_directory: str = "rag/chroma_db",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG system.
        
        Args:
            pdf_directory: Directory containing PDF files
            persist_directory: Directory to persist ChromaDB
            embedding_model: HuggingFace embedding model name
        """
        self.pdf_directory = Path(pdf_directory)
        self.persist_directory = Path(persist_directory)
        self.embedding_model = embedding_model
        
        # Initialize components
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.documents = []
        
        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("Environmental Law RAG System initialized")
    
    def setup_embeddings(self):
        """Setup embedding model"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                model_kwargs={'device': 'cpu'}
            )
            logger.info(f"Embeddings model '{self.embedding_model}' loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embeddings model: {e}")
            raise
    
    def load_pdf_documents(self) -> List[Dict[str, Any]]:
        """
        Load and process all PDF documents from the directory.
        
        Returns:
            List of processed documents with metadata
        """
        documents = []
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.pdf_directory}")
            return documents
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing {pdf_file.name}")
                
                # Load PDF using PyPDF2 for better control
                with open(pdf_file, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
                if text.strip():
                    # Create document metadata
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
        """
        Split documents into chunks for better retrieval.
        
        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of document chunks
        """
        if not self.documents:
            logger.warning("No documents loaded. Call load_pdf_documents() first.")
            return []
        
        # Use RecursiveCharacterTextSplitter for better chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        all_chunks = []
        
        for doc in self.documents:
            # Split the document content
            chunks = text_splitter.split_text(doc['content'])
            
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
        """
        Create and populate the ChromaDB vector store.
        
        Args:
            chunks: List of document chunks to store
        """
        if not chunks:
            logger.warning("No chunks provided for vector store creation")
            return
        
        if not self.embeddings:
            self.setup_embeddings()
        
        try:
            # Prepare documents and metadatas for ChromaDB
            documents = [chunk['content'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [chunk['metadata']['chunk_id'] for chunk in chunks]
            
            # Create ChromaDB collection
            self.vectorstore = Chroma.from_texts(
                texts=documents,
                embedding=self.embeddings,
                metadatas=metadatas,
                ids=ids,
                persist_directory=str(self.persist_directory)
            )
            
            # Persist the vector store
            self.vectorstore.persist()
            
            logger.info(f"Vector store created with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def load_existing_vectorstore(self):
        """Load existing vector store if it exists"""
        try:
            if not self.embeddings:
                self.setup_embeddings()
            
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            
            # Check if collection exists and has documents
            collection = self.vectorstore._collection
            count = collection.count()
            
            if count > 0:
                logger.info(f"Loaded existing vector store with {count} documents")
                return True
            else:
                logger.info("No existing vector store found")
                return False
                
        except Exception as e:
            logger.error(f"Error loading existing vector store: {e}")
            return False
    
    def setup_qa_chain(self, llm_model: str = "microsoft/DialoGPT-medium"):
        """
        Setup the question-answering chain using local Hugging Face models.
        
        Args:
            llm_model: Hugging Face model to use for generation
        """
        if not self.vectorstore:
            logger.error("Vector store not initialized. Create vector store first.")
            return
        
        try:
            # Create retriever
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  # Retrieve top 5 most similar chunks
            )
            
            # Create prompt template for environmental law queries
            prompt_template = """
            You are an expert in environmental law and regulations. Use the following context to answer questions about environmental laws, regulations, and policies.

            Context:
            {context}

            Question: {question}

            Instructions:
            1. Provide accurate, detailed answers based on the provided context
            2. Cite specific laws, sections, or regulations when relevant
            3. If the context doesn't contain enough information, say so clearly
            4. Focus on practical implications and compliance requirements
            5. Use clear, professional language suitable for legal and environmental professionals

            Answer:
            """
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Initialize local LLM using Hugging Face
            logger.info(f"Loading local model: {llm_model}")
            
            # Use a smaller, faster model for better performance
            model_name = "microsoft/DialoGPT-small"  # Smaller model for faster loading
            
            try:
                # Create pipeline for text generation
                pipe = pipeline(
                    "text-generation",
                    model=model_name,
                    tokenizer=model_name,
                    max_length=512,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=50256
                )
                
                # Create HuggingFacePipeline for LangChain
                llm = HuggingFacePipeline(pipeline=pipe)
                logger.info("Local LLM loaded successfully")
                
            except Exception as e:
                logger.warning(f"Error loading {model_name}: {e}")
                logger.info("Falling back to a simple text-based approach...")
                
                # Fallback: Create a simple text-based LLM
                class SimpleLocalLLM:
                    def __call__(self, prompt):
                        # Simple text-based response
                        return "Based on the provided context, I can help you find relevant information. Please check the source documents for detailed answers."
                
                llm = SimpleLocalLLM()
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            logger.info("QA chain setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up QA chain: {e}")
            raise
    
    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: The question to ask
            k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary containing answer and source documents
        """
        if not self.qa_chain:
            logger.error("QA chain not initialized. Call setup_qa_chain() first.")
            return {"error": "QA chain not initialized"}
        
        try:
            # Query the system
            result = self.qa_chain({"query": question})
            
            return {
                "question": question,
                "answer": result["result"],
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("source", "Unknown")
                    }
                    for doc in result["source_documents"]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return {"error": str(e)}
    
    def search_similar_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents without generating an answer.
        
        Args:
            query: Search query
            k: Number of documents to return
            
        Returns:
            List of similar documents
        """
        if not self.vectorstore:
            logger.error("Vector store not initialized")
            return []
        
        try:
            docs = self.vectorstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score,
                    "source": doc.metadata.get("source", "Unknown")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded documents"""
        if not self.vectorstore:
            return {"error": "Vector store not initialized"}
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            # Get unique sources
            results = collection.get()
            sources = set(metadata.get("source", "Unknown") for metadata in results["metadatas"])
            
            return {
                "total_chunks": count,
                "unique_documents": len(sources),
                "sources": list(sources)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}


def main():
    """Main function to demonstrate the RAG system"""
    # Initialize RAG system
    rag = EnvironmentalLawRAG()
    
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
    
    # Setup QA chain (requires OpenAI API key)
    try:
        rag.setup_qa_chain()
        
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
    
    except Exception as e:
        print(f"Error setting up QA chain: {e}")
        print("Make sure you have set your OPENAI_API_KEY environment variable.")


if __name__ == "__main__":
    main()
