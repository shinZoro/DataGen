from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from typing import Optional, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import csv, sqlite3
from sentence_transformers import SentenceTransformer


load_dotenv()

#Initializing model 
llm = init_chat_model("google_genai:gemini-2.5-flash-preview-05-20") #init_chat_model("openai: o3mini") Uncomment to use Open ai models instead.

#State
class State(TypedDict):
    intent: Optional[str]
    topic: Optional[str]
    num_rows: Optional[int]
    generated_data: Optional[list]
    embeddings: List[Dict[str, Any]]
    query_text: str
    top_k: int
    query_results: List[Dict[str, Any]]
    collection_name: str
    stored_count: int


#prompts

generator_prompt =PromptTemplate.from_template(
    """Generate {num_rows} synthetic product reviews about {topic} in strict JSON array format.
    Each item should have: "Product Name", "Review", "Sentiment" (Positive/Neutral/Negative).
    Example:
    [
      {{"Product_Name": "XPhone", "Review": "Good battery", "Sentiment": "Positive"}},
      ...
    ]

    Important : The data should Feel real therefore use believable made up names, also do stick to the topic do not go into other categories or products.
    Only return valid JSON. 
    """
)

generator = generator_prompt | llm | JsonOutputParser()

#database

def save_to_memory(state: State):
    conn = sqlite3.connect('service/data/Product_reviews.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Product_Name TEXT,
    Review TEXT,
    Sentiment TEXT
    )
    """
    )

    with open ("service/data/data.csv" , 'r',  newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader: 
            cursor.execute("INSERT INTO reviews (Product_Name, Review, Sentiment) VALUES (?, ?, ?)" , row)

    conn.commit()
    conn.close()


#nodes

def router(state: State):
   if state['intent'] == 'search':
       return 'Search'
   elif state['intent'] == 'generate':
       return 'generate'
   else:
       return 'generate' 


def generator_data(state : State):
    topic = state["topic"]
    num_rows = state["num_rows"]

    generated_data = generator.invoke({"topic" : topic , "num_rows" : num_rows})

    return {"generated_data": generated_data}


def save_to_csv_node(state: State):
    filename = "service/data/data.csv"
    with open(filename, "w", newline="", encoding='utf-8') as csvfile:
        if not state["generated_data"]:
            return state
        generated_data = state["generated_data"]
        writer = csv.DictWriter(csvfile, fieldnames=generated_data[0].keys())
        writer.writeheader()
        writer.writerows(generated_data)
    return state


def fetch_and_generate_embeddings(state : State):
   conn = sqlite3.connect('service/data/Product_reviews.db')
   cursor = conn.cursor()
   cursor.execute(f"SELECT Product_Name, Review, Sentiment FROM reviews ORDER BY id DESC LIMIT {state['num_rows']}")
   rows = cursor.fetchall()
   conn.close()
   
   model = SentenceTransformer('all-MiniLM-L6-v2')
   texts = [f"{row[0]}: {row[1]}" for row in rows]
   embeddings = model.encode(texts)
   
   state['embeddings'] = [
       {
           'product_name': rows[i][0],
           'review': rows[i][1], 
           'sentiment': rows[i][2],
           'embedding': embeddings[i]
       }
       for i in range(len(rows))
   ]
   return state

import chromadb

def store_in_chroma_db(state):
   client = chromadb.PersistentClient(path="./chroma_db")

   collection_name = f"{state['topic']}_product_reviews"
   
   collection = client.get_or_create_collection(
       name=collection_name,
       metadata={"hnsw:space": "cosine"}
   )
   
   ids = []
   embeddings = []
   metadatas = []
   documents = []
   
   for i, item in enumerate(state['embeddings']):
       ids.append(f"review_{i}")
       embeddings.append(item['embedding'].tolist())
       metadatas.append({
           'product_name': item['product_name'],
           'sentiment': item['sentiment']
       })
       documents.append(item['review'])
   
   collection.add(
       ids=ids,
       embeddings=embeddings,
       metadatas=metadatas,
       documents=documents
   )
   


   state['collection_name'] = f"{state['topic']}_product_reviews"
   state['stored_count'] = len(ids)

   return state


def query_chroma_db(state):
   client = chromadb.PersistentClient(path="./chroma_db")

   collection_name = f"{state['topic']}_product_reviews"
   collection = client.get_collection(name=collection_name)
   
   results = collection.query(
       query_texts=[state['query_text']],
       n_results=state.get('top_k', 5),
       include=['documents', 'metadatas', 'distances']
   )
   
   state['query_results'] = [
       {
           'document': results['documents'][0][i],
           'product_name': results['metadatas'][0][i]['product_name'],
           'sentiment': results['metadatas'][0][i]['sentiment'],
           'distance': results['distances'][0][i]
       }
       for i in range(len(results['documents'][0]))
   ]
   return state


    
# Create the state graph
workflow = StateGraph(State)
workflow.add_node("router" , router)
workflow.add_node("generate", generator_data)
workflow.add_node("save", save_to_csv_node)
workflow.add_node("DB", save_to_memory)
workflow.add_node("gen_embeddings",fetch_and_generate_embeddings)
workflow.add_node("VectorDB",store_in_chroma_db )
workflow.add_node("Search", query_chroma_db)

# Add edges
workflow.add_conditional_edges(START, router,

  {
    "generate": "generate",
    "Search": "Search"
}
)

workflow.add_edge("generate", "save")
workflow.add_edge("save", "DB")
workflow.add_edge("DB", "gen_embeddings")
workflow.add_edge("gen_embeddings"  , "VectorDB")
workflow.add_edge("VectorDB", END)
workflow.add_edge("Search", END)

# Compile the graph
app = workflow.compile()


if __name__ == "__main__":
    initial_state = {
        "intent": "generate",
        "topic": "Bicycles", 
        "num_rows": 5, 
        "generated_data": [],
        "embeddings": [],
        "query_text": "Build",
        "top_k": 2,
    }
    
    result = app.invoke(initial_state)
    print("Workflow completed!")