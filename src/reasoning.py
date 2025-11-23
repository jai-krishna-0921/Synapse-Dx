import os
from typing import Iterator, List, Optional
from agno.agent import Agent
from agno.models.google import Gemini
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.db.postgres import PostgresDb
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_AUTH = (NEO4J_USER, NEO4J_PASSWORD)
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_URL = os.getenv("DB_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai")

class HybridReasoner:
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        
        # Initialize Embedder
        self.embedder = SentenceTransformerEmbedder(id="all-MiniLM-L6-v2")

        # Initialize Qdrant Vector DB
        self.vector_db = Qdrant(
            collection="med_guidelines",
            url=QDRANT_URL,
            embedder=self.embedder,
        )
        
        # Initialize Knowledge Base
        self.knowledge_base = Knowledge(
            vector_db=self.vector_db,
        )

        # Initialize Postgres DB for Memory
        self.db = PostgresDb(
            db_url=DB_URL,
        )

        # Initialize Agno Agent
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash-exp", api_key=GEMINI_API_KEY),
            markdown=True,
            knowledge=self.knowledge_base,
            # Traditional RAG: Always add knowledge to context
            add_knowledge_to_context=True,
            # Disable agentic search (we want consistent RAG retrieval)
            search_knowledge=False,
            tools=[self.search_medical_graph], # Add Graph Tool
            # Memory Configuration
            db=self.db,
            enable_user_memories=True,
            enable_session_summaries=True,
            debug_mode=True, # Enable debug logging
            instructions=[
                "You are MediGraph, an empathetic and thorough AI medical consultant.",
                "",
                "**YOUR GOAL:**",
                "To help the user by providing accurate, **ELABORATE**, and detailed medical information. Do not be brief. Explain the 'WHY' and 'HOW' behind every conclusion.",
                "",
                "**KNOWLEDGE SOURCES:**",
                "- Use retrieved medical textbooks and knowledge graph to inform your answers.",
                "- Cite specific protocols and dosages when providing treatment plans.",
                "",
                "**INTERACTION MODES:**",
                "1. **General Information:** If the user asks general questions (e.g., 'What are the meds for Diabetes?'), **ANSWER DIRECTLY**. Do NOT ask triage questions.",
                "2. **Symptom Triage:** If the user presents specific symptoms, **INVESTIGATE EFFICIENTLY**.",
                "   - **Active Reasoning:** Constantly check for contradictions. If a user says 'Rash' but you suspected Malaria, **FLAG IT** (e.g., 'Wait, Malaria rarely causes a rash. This might be Dengue.').",
                "   - **Efficiency Protocol:** Ask **MAXIMUM 2** high-value questions per turn. Combine them (e.g., 'Do you have X AND Y?'). Aim to diagnose in **2 turns**.",
                "   - **Disagreement Scoring:** If new info contradicts your previous hypothesis, explicitly state: 'This new information changes the probability...'",
                "",
                "**CRITICAL LOGIC TRAPS (WATCH OUT FOR THESE):**",
                "- **Malaria vs. Dengue:** If a user has fever + travel, suspect Malaria. BUT if they mention **RASH** or **CONSTANT FEVER** (not cyclical), you MUST switch hypothesis to **DENGUE** or **CHIKUNGUNYA**. Malaria rarely causes a rash.",
                "- **Viral vs. Bacterial:** Watch for duration and severity.",
                "",
                "**CRITICAL RULES:**",
                "- **NO ROBOTIC STRUCTURES:** Do NOT use headers like 'Primary Hypothesis', 'Confidence', or 'Reasoning'. Do NOT use bulleted lists for the diagnosis.",
                "- **BE HUMAN:** Explain your thinking naturally. Use phrases like: 'Since you mentioned X, it makes me think of Y...', 'However, the fact that you have Z rules out...', 'This narrows it down to...'.",
                "- **Emergency:** If it's an emergency (like Meningitis), say it clearly but naturally: 'This combination of symptoms is very concerning for Meningitis and requires immediate ER attention.'",
                "- **Context Awareness:** If the user answers your questions, proceed to the diagnosis. Don't keep asking.",
                "",
                "**Response Style (Narrative & Explanatory):**",
                "Instead of a report, have a conversation:",
                "1. **Synthesize:** 'Okay, let's look at what's going on. You have a stiff neck and a severe headache...'",
                "2. **Reason:** 'Because you can't touch your chin to your chest, that's a strong sign of nuchal rigidity. Combined with the fever, it points strongly towards...'",
                "3. **Conclude:** 'Given this, I believe the most likely cause is...'",
                "4. **Advise:** 'You need to go to the ER right now for a lumbar puncture. In the meantime...'",
                "",
                "**Disclaimer:** I am an AI assistant. Always consult a qualified healthcare provider.",
            ]
        )

    def search_medical_graph(self, entities: List[str]) -> str:
        """
        Searches the Neo4j medical knowledge graph for relationships involving the given entities.
        Use this to find connected diseases, symptoms, or drugs.
        
        Args:
            entities: A list of entity names to search for (e.g., ["Headache", "Ibuprofen"]).
            
        Returns:
            A string description of the relationships found.
        """
        context = []
        
        # Enhanced query that prioritizes disease-symptom relationships
        query = """
        MATCH (n:Entity)-[r]-(m:Entity)
        WHERE n.name IN $entities
        WITH n, r, m,
             CASE 
                 WHEN m.type = 'disease' THEN 3
                 WHEN type(r) IN ['HAS_SYMPTOM', 'TREATS', 'CAUSES'] THEN 2
                 ELSE 1
             END AS priority
        RETURN n.name, type(r), m.name, m.type, priority
        ORDER BY priority DESC
        LIMIT 50
        """
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(query, entities=entities)
                for record in result:
                    rel_type = record['type(r)']
                    context.append(f"{record['n.name']} --[{rel_type}]--> {record['m.name']} ({record['m.type']})")
        except Exception as e:
            return f"Graph query error: {str(e)}"
        
        if not context:
            return "No direct relationships found in the knowledge graph."
            
        return "\n".join(context)

    def triage_stream(self, symptoms: str, history: str, session_id: str = None, user_id: str = None) -> Iterator[str]:
        """
        Stream triage assessment from Agno Agent.
        """
        prompt = f"""
        Patient Symptoms: {symptoms}
        Patient History: {history}
        
        Please analyze these symptoms, search for relevant medical guidelines and graph relationships, and provide a triage assessment and advice.
        """
        
        try:
            # Run agent and yield chunks
            run_response = self.agent.run(
                prompt, 
                stream=True,
                session_id=session_id,
                user_id=user_id
            )
            for chunk in run_response:
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            yield f"Error generating response: {str(e)}"

    def close(self):
        self.neo4j_driver.close()
