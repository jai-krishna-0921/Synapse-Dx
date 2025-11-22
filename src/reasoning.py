import os
import google.generativeai as genai
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import time

load_dotenv()

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class HybridReasoner:
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        self.qdrant_client = QdrantClient(url=QDRANT_URL)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp') # Using 2.0 Flash as requested (2.5 in prompt, mapping to available)

    def get_graph_context(self, entities: list[str]) -> str:
        """Retrieves 1-hop neighbors for given entities from Neo4j."""
        context = []
        query = """
        MATCH (n:Entity)-[r]-(m:Entity)
        WHERE n.name IN $entities
        RETURN n.name, type(r), m.name, m.type
        LIMIT 20
        """
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(query, entities=entities)
                for record in result:
                    context.append(f"{record['n.name']} {record['type(r)']} {record['m.name']} ({record['m.type']})")
        except Exception as e:
            print(f"Graph query error: {e}")
        
        return "\n".join(context)

    def get_vector_context(self, query_text: str, limit: int = 3) -> str:
        """Retrieves similar text chunks from Qdrant."""
        try:
            query_vector = self.embedder.encode(query_text).tolist()
            hits = self.qdrant_client.search(
                collection_name="med_guidelines",
                query_vector=query_vector,
                limit=limit
            )
            return "\n\n".join([hit.payload['text'] for hit in hits])
        except Exception as e:
            print(f"Vector search error: {e}")
            return ""

    def extract_entities(self, text: str) -> list[str]:
        """
        Simple heuristic entity extraction. 
        In a real app, use a NER model or Gemini to extract.
        For now, we'll just split by common delimiters or use Gemini to extract.
        """
        # Let's use Gemini for fast entity extraction to be more robust
        prompt = f"Extract medical entities (symptoms, diseases, anatomy) from this text as a comma-separated list: {text}"
        try:
            response = self.model.generate_content(prompt)
            return [e.strip() for e in response.text.split(',')]
        except:
            return text.split() # Fallback

    def triage(self, symptoms: str, history: str) -> dict:
        start_time = time.time()
        
        # 1. Extract Entities
        entities = self.extract_entities(symptoms + " " + history)
        
        # 2. Retrieve Context (Parallelizable)
        graph_context = self.get_graph_context(entities)
        vector_context = self.get_vector_context(symptoms)
        
        # 3. Construct Prompt
        prompt = f"""
        You are a high-speed medical triage assistant.
        
        Patient Symptoms: {symptoms}
        Patient History: {history}
        
        Knowledge Graph Context:
        {graph_context}
        
        Medical Guidelines Context:
        {vector_context}
        
        Task:
        1. Provide a likely diagnosis.
        2. Assign a triage level (Emergency, Urgent, Non-Urgent).
        3. Explain reasoning briefly.
        
        Output JSON format:
        {{
            "diagnosis": "...",
            "triage_level": "...",
            "reasoning": "..."
        }}
        """
        
        # 4. Generate Response
        response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        return {
            "result": response.text,
            "latency_ms": latency_ms
        }

    def close(self):
        self.neo4j_driver.close()
