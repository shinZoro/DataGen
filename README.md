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
  "topic": "Jackets",
  "num_rows": 5
}
```

**Response:**
```json
{
  "status": "success",
  "count": 5,
  "Generated data ": [
    {
      "Product_Name": "Everest Puffer Jacket",
      "Review": "This jacket is incredibly warm and lightweight! Perfect for cold winter mornings. The hood is a great addition, and it packs down surprisingly small. Highly recommend for anyone needing serious warmth.",
      "Sentiment": "Positive"
    },
    {
      "Product_Name": "Urban Commuter Raincoat",
      "Review": "Disappointed with this raincoat. It claims to be waterproof, but after walking in moderate rain for 15 minutes, my shirt was damp. The zipper also feels flimsy and gets stuck often. Not worth the price.",
      "Sentiment": "Negative"
    },
    {
      "Product_Name": "Summit Trekker Fleece",
      "Review": "A decent fleece jacket for the price. It's soft and provides good layering warmth for hiking. The pockets are a nice size. It's not the most stylish, but it gets the job done for outdoor activities.",
      "Sentiment": "Neutral"
    },
    {
      "Product_Name": "Classic Denim Jacket",
      "Review": "Absolutely love this classic denim jacket! The fit is perfect, not too tight or too baggy. It's become my go-to for casual outings and adds a cool touch to any outfit. The denim feels durable and soft after a few washes.",
      "Sentiment": "Positive"
    },
    {
      "Product_Name": "Voyager Windbreaker",
      "Review": "This windbreaker is okay, but not amazing. It blocks wind effectively, but the breathability isn't great, so I tend to get sweaty quickly during active use. The sizing also runs a bit small, so consider sizing up.",
      "Sentiment": "Neutral"
    }
  ]
}
```

### Search Reviews
```http
POST /search
```

**Request Body:**
```json
{
  "topic": "Jackets",
  "query_text": "Warm and Cozy",
  "top_k": 2
}
```

**Response:**
```json
{
  "results": [
    {
      "document": "A decent fleece jacket for the price. It's soft and provides good layering warmth for hiking. The pockets are a nice size. It's not the most stylish, but it gets the job done for outdoor activities.",
      "product_name": "Summit Trekker Fleece",
      "sentiment": "Neutral",
      "distance": 0.5914355516433716
    },
    {
      "document": "This jacket is incredibly warm and lightweight! Perfect for cold winter mornings. The hood is a great addition, and it packs down surprisingly small. Highly recommend for anyone needing serious warmth.",
      "product_name": "Everest Puffer Jacket",
      "sentiment": "Positive",
      "distance": 0.5925547480583191
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
service/
├── api.py               # FastAPI application and endpoints
└── main.py              # LangGraph workflow and core logic
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
├── docker               # Docker configuration
├── docker-compose.yml   # Docker deployment configuration
├── Dockerfile           # Container build instructions
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