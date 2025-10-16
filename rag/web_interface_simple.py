"""
Simple Web Interface for Environmental Law RAG System (No OpenAI Required)
A Flask-based web interface for the simple RAG system
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
from pathlib import Path

# Add the rag directory to Python path
sys.path.append(str(Path(__file__).parent))

from rag_simple import SimpleEnvironmentalLawRAG

app = Flask(__name__)

# Initialize RAG system
rag_system = None

def initialize_rag():
    """Initialize the RAG system"""
    global rag_system
    if rag_system is None:
        rag_system = SimpleEnvironmentalLawRAG()
        if not rag_system.load_existing_vectorstore():
            return False
    return True

@app.route('/')
def index():
    """Main page"""
    return render_template('index_simple.html')

@app.route('/api/query', methods=['POST'])
def query_rag():
    """API endpoint for querying the RAG system"""
    try:
        if not initialize_rag():
            return jsonify({
                'error': 'RAG system not initialized. Please run setup_rag_simple.py first.'
            }), 500
        
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Query the RAG system
        result = rag_system.query(question)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'question': result['question'],
            'answer': result['answer'],
            'sources': [
                {
                    'source': doc['source'],
                    'content': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                    'metadata': doc['metadata'],
                    'similarity_score': doc.get('similarity_score', 0)
                }
                for doc in result['source_documents']
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_documents():
    """API endpoint for searching similar documents"""
    try:
        if not initialize_rag():
            return jsonify({
                'error': 'RAG system not initialized. Please run setup_rag_simple.py first.'
            }), 500
        
        data = request.get_json()
        query = data.get('query', '').strip()
        k = data.get('k', 5)
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        # Search for similar documents
        results = rag_system.search_similar_documents(query, k=k)
        
        return jsonify({
            'query': query,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint for getting system statistics"""
    try:
        if not initialize_rag():
            return jsonify({
                'error': 'RAG system not initialized. Please run setup_rag_simple.py first.'
            }), 500
        
        stats = rag_system.get_document_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Create the HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Environmental Law RAG System (Free & Local)</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .free-badge {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-left: 10px;
        }
        .search-section {
            margin-bottom: 30px;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            padding: 12px 24px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #2980b9;
        }
        button:disabled {
            background-color: #bdc3c7;
            cursor: not-allowed;
        }
        .results {
            margin-top: 20px;
        }
        .answer {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }
        .sources {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        .source-item {
            margin-bottom: 10px;
            padding: 10px;
            background-color: white;
            border-radius: 3px;
            border-left: 3px solid #27ae60;
        }
        .source-title {
            font-weight: bold;
            color: #27ae60;
        }
        .similarity-score {
            font-size: 12px;
            color: #7f8c8d;
            margin-left: 10px;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
        }
        .error {
            color: #e74c3c;
            background-color: #fadbd8;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .stats {
            background-color: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .info-box {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #2196f3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Environmental Law RAG System <span class="free-badge">FREE & LOCAL</span></h1>
        
        <div class="info-box">
            <strong>ℹ️ No API Keys Required!</strong> This system runs entirely on your local machine using free, open-source models. No internet connection needed after setup.
        </div>
        
        <div class="stats" id="stats">
            <strong>System Statistics:</strong> Loading...
        </div>
        
        <div class="search-section">
            <h2>Ask a Question</h2>
            <div class="input-group">
                <input type="text" id="questionInput" placeholder="Ask about environmental laws, regulations, or policies..." />
                <button onclick="askQuestion()" id="askBtn">Ask</button>
            </div>
            
            <div id="results" class="results"></div>
        </div>
        
        <div class="search-section">
            <h2>Search Documents</h2>
            <div class="input-group">
                <input type="text" id="searchInput" placeholder="Search for specific topics or keywords..." />
                <button onclick="searchDocuments()" id="searchBtn">Search</button>
            </div>
            
            <div id="searchResults" class="results"></div>
        </div>
    </div>

    <script>
        // Load statistics on page load
        loadStats();
        
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('stats').innerHTML = 
                            '<strong>Error:</strong> ' + data.error;
                    } else {
                        document.getElementById('stats').innerHTML = 
                            '<strong>System Statistics:</strong> ' +
                            data.total_chunks + ' chunks from ' + 
                            data.unique_documents + ' documents';
                    }
                })
                .catch(error => {
                    document.getElementById('stats').innerHTML = 
                        '<strong>Error:</strong> Failed to load statistics';
                });
        }
        
        function askQuestion() {
            const question = document.getElementById('questionInput').value.trim();
            if (!question) return;
            
            const btn = document.getElementById('askBtn');
            const results = document.getElementById('results');
            
            btn.disabled = true;
            btn.textContent = 'Asking...';
            results.innerHTML = '<div class="loading">Processing your question...</div>';
            
            fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    results.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                } else {
                    let html = '<div class="answer"><strong>Answer:</strong><br>' + data.answer + '</div>';
                    
                    if (data.sources && data.sources.length > 0) {
                        html += '<div class="sources"><strong>Sources:</strong>';
                        data.sources.forEach(source => {
                            html += '<div class="source-item">' +
                                '<div class="source-title">' + source.source + 
                                '<span class="similarity-score">(Relevance: ' + (source.similarity_score * 100).toFixed(1) + '%)</span></div>' +
                                '<div>' + source.content + '</div>' +
                                '</div>';
                        });
                        html += '</div>';
                    }
                    
                    results.innerHTML = html;
                }
            })
            .catch(error => {
                results.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            })
            .finally(() => {
                btn.disabled = false;
                btn.textContent = 'Ask';
            });
        }
        
        function searchDocuments() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;
            
            const btn = document.getElementById('searchBtn');
            const results = document.getElementById('searchResults');
            
            btn.disabled = true;
            btn.textContent = 'Searching...';
            results.innerHTML = '<div class="loading">Searching documents...</div>';
            
            fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query, k: 5 })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    results.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                } else {
                    let html = '<div class="sources"><strong>Search Results:</strong>';
                    if (data.results.length === 0) {
                        html += '<div>No results found.</div>';
                    } else {
                        data.results.forEach((result, index) => {
                            html += '<div class="source-item">' +
                                '<div class="source-title">' + (index + 1) + '. ' + result.source + 
                                '<span class="similarity-score">(Relevance: ' + (result.similarity_score * 100).toFixed(1) + '%)</span></div>' +
                                '<div>' + result.content + '</div>' +
                                '</div>';
                        });
                    }
                    html += '</div>';
                    results.innerHTML = html;
                }
            })
            .catch(error => {
                results.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            })
            .finally(() => {
                btn.disabled = false;
                btn.textContent = 'Search';
            });
        }
        
        // Allow Enter key to submit
        document.getElementById('questionInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchDocuments();
            }
        });
    </script>
</body>
</html>'''
    
    # Write the HTML template
    with open(templates_dir / 'index_simple.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("🌍 Environmental Law RAG System (Free & Local)")
    print("=" * 60)
    print("✅ No API keys required!")
    print("✅ Runs entirely on your local machine!")
    print("✅ No internet connection needed after setup!")
    print("")
    print("Starting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

