# DataGen

A FastAPI-based service that generates synthetic product reviews using AI and provides semantic search capabilities through vector embeddings. Built with LangGraph workflows, ChromaDB for vector storage, and Google's Gemini AI model.

## Features

- **Synthetic Data Generation**: Create realistic product reviews using AI
- **Topic-Based Semantic Search**: Find similar reviews within specific topics using vector embeddings
- **Workflow Management**: LangGraph-powered data processing pipeline
- **Topic-Isolated Vector Storage**: ChromaDB integration with topic-specific collections
- **RESTful API**: Clean FastAPI endpoints for easy integration
- **Docker Support**: Containerized deployment with Docker Compose

## Architecture

The service uses a LangGraph workflow that handles two main intents:

1. **Generate**: Creates synthetic product reviews → Saves to CSV → Stores in SQLite → Generates embeddings → Stores in topic-specific ChromaDB collections
2. **Search**: Performs semantic search against stored embeddings in topic-specific ChromaDB collections

### Topic-Based Data Isolation

Each topic creates its own ChromaDB collection (e.g., `electronics_product_reviews`, `books_product_reviews`), ensuring:
- No data mixing between different topics
- Isolated search results per topic
- Better semantic accuracy within topic domains
- Scalable multi-topic support

## Prerequisites

- Python 3.8+
- Docker and Docker Compose (for containerized deployment)
- Google AI API key (for Gemini model)

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/shinZoro/DataGen.git
   cd datagen
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` file:
   ```env
   GOOGLE_API_KEY=your_google_ai_api_key_here
   ```

4. **Run the application**
   ```bash
   python api.py
   ```

### Docker Deployment

1. **Set up environment variables**
   Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your Google API key:
   ```env
   GOOGLE_API_KEY=your_google_ai_api_key_here
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

The service will be available at `http://localhost:8000`

## API Endpoints

### Generate Synthetic Data
```http
POST /generate
```

**Request Body:**
```json
{
  "topic": "electronics",
  "num_rows": 5
}
```

**Response:**
```json
{
  "status": "success",
  "count": 5
}
```

### Search Reviews
```http
POST /search
```

**Request Body:**
```json
{
  "topic": "electronics",
  "query_text": "great sound quality",
  "top_k": 2
}
```

**Response:**
```json
{
  "results": [
    {
      "document": "These headphones have incredible sound quality with deep bass and crystal clear highs. Perfect for music lovers who want premium audio experience.",
      "product_name": "SoundMaster Pro",
      "sentiment": "Positive",
      "distance": 0.6175824403762817
    },
    {
      "document": "Amazing audio clarity and the bass response is phenomenal. These are by far the best headphones I've ever owned for the price range.",
      "product_name": "AudioElite 500",
      "sentiment": "Positive",
      "distance": 0.6949067115783691
    }
  ]
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

## Usage Examples

### Generate Product Reviews for Electronics
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "electronics",
       "num_rows": 15
     }'
```

### Search for Similar Reviews in Electronics Topic
```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "electronics",
       "query_text": "sound quality excellent",
       "top_k": 3
     }'
```

### Generate Reviews for Different Topics
```bash
# Books
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "books",
       "num_rows": 10
     }'

# Clothing
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "clothing",
       "num_rows": 8
     }'
```

## Data Flow

1. **Data Generation Pipeline**:
   - AI generates synthetic reviews based on topic
   - Data saved to `data.csv`
   - Reviews stored in SQLite database (`Product_reviews.db`)
   - Sentence embeddings generated using `all-MiniLM-L6-v2`
   - Embeddings stored in topic-specific ChromaDB collections (e.g., `electronics_product_reviews`)

2. **Search Pipeline**:
   - Query text converted to embedding
   - ChromaDB performs cosine similarity search within the specified topic collection
   - Returns top-k most similar reviews with metadata from that topic only

## Topic Management

### Supported Topics
The system supports any topic you specify. Common examples:
- `electronics` → Creates `electronics_product_reviews` collection
- `books` → Creates `books_product_reviews` collection  
- `clothing` → Creates `clothing_product_reviews` collection
- `home_appliances` → Creates `home_appliances_product_reviews` collection

### Benefits of Topic Isolation
- **Improved Search Accuracy**: Search within relevant domain context
- **Data Organization**: Clear separation of different product categories
- **Scalability**: Add new topics without affecting existing data
- **Parallel Processing**: Generate and search different topics independently

## Configuration

### AI Model Configuration
The service uses Google's Gemini 2.5 Flash model by default. To switch to OpenAI:

```python
# In main.py, uncomment and modify:
llm = init_chat_model("openai:gpt-3.5-turbo")
```

### Database Storage
- **SQLite**: `Product_reviews.db` - Stores raw review data
- **ChromaDB**: `./chroma_db` - Stores vector embeddings in topic-specific collections
- **Data Directory**: `./data/` - Contains generated CSV files and other data
- **ChromaDB Data**: `./chroma_data` - ChromaDB persistent storage

## File Structure

```
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
├── .python-version      # Python version specification
├── api.py               # FastAPI application and endpoints
├── docker               # Docker configuration
├── docker-compose.yml   # Docker deployment configuration
├── Dockerfile           # Container build instructions
├── main.py              # LangGraph workflow and core logic
├── pyproject.toml       # Python project configuration
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
└── uv.lock              # UV dependency lock file
```

**Note**: The following directories will be created automatically when you run the application:
- `chroma_db/` - ChromaDB database files with topic collections
- `chroma_data/` - ChromaDB persistent storage (if using Docker)

### API Documentation
Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Troubleshooting

### Common Issues

1. **Google API Key Issues**
   - Ensure your API key is valid and has access to Gemini models
   - Check the `.env` file is properly configured

2. **ChromaDB Connection Issues**
   - Ensure ChromaDB service is running (check docker-compose logs)
   - Verify the `./chroma_db` directory has proper permissions

3. **Topic Collection Issues**
   - If search returns empty results, ensure you've generated data for that specific topic first
   - Check ChromaDB logs for collection creation/access errors

4. **Dependency Issues**
   - Make sure all required packages are installed
   - Use a virtual environment to avoid conflicts

### Windows-Specific Notes

When testing on Windows, use proper JSON escaping for curl commands:

```bash
# Windows curl syntax
curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" -d "{\"topic\": \"electronics\", \"num_rows\": 10}"

# Or use PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/generate" -Method POST -ContentType "application/json" -Body '{"topic": "electronics", "num_rows": 10}'
```