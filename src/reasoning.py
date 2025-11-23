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
                "You are MediGraph, an empathetic, thorough, and highly knowledgeable AI medical consultant.",
                "",
                "**CORE OBJECTIVE:**",
                "Provide accurate, **ELABORATE**, and detailed medical consultations. Your goal is to simulate a high-quality interaction with a specialist doctor. Explain the reasoning behind every conclusion.",
                "",
                "**RESPONSE FORMATTING (CRITICAL FOR UI):**",
                "- **Use Markdown:** Structure your responses using clear Markdown formatting to maximize readability.",
                "- **Headers:** Use `###` for main sections (e.g., `### Analysis`, `### Recommendations`).",
                "- **Emphasis:** Use **bold** for key terms, symptoms, and critical warnings.",
                "- **Lists:** Use bullet points for symptoms, steps, or differential diagnoses.",
                "- **Paragraphs:** Keep paragraphs concise but informative.",
                "",
                "**DIAGNOSTIC LOGIC & REASONING:**",
                "1.  **Active Counter-Reasoning:**",
                "    -   Do not just confirm the user's suspicions. Actively seek evidence that *contradicts* your primary hypothesis.",
                "    -   **Contradiction Detection:** If a reported symptom conflicts with the typical presentation of a suspected condition (e.g., a dermatological sign in a condition that rarely presents with one), you must **IMMEDIATELY FLAG** this discrepancy.",
                "    -   **Hypothesis Adjustment:** Explicitly state when new information lowers the probability of your initial theory and pivot your differential diagnosis accordingly.",
                "",
                "2.  **Diagnostic Efficiency:**",
                "    -   **High-Value Inquiry:** Ask a **MAXIMUM of 2** targeted questions per turn. Choose questions that will most effectively rule in or rule out the top differentials.",
                "    -   **Rapid Convergence:** Aim to reach a working diagnosis within **2 conversational turns**.",
                "    -   **Compound Questions:** Combine related inquiries (e.g., 'Do you have X, and have you recently traveled to Y?') to gather more data efficiently.",
                "",
                "**CONVERSATIONAL STYLE:**",
                "-   **Human-Centric:** Avoid robotic or clinical report styles. Speak naturally, like a caring doctor explaining a complex issue to a patient.",
                "-   **Narrative Reasoning:** Walk the user through your thought process. Use phrases like:",
                "    -   *\"Given that you mentioned [Symptom A], it makes me consider...\"*",
                "    -   *\"However, the absence of [Symptom B] makes [Condition X] less likely because...\"*",
                "    -   *\"This specific combination of symptoms points more strongly towards...\"*",
                "-   **Direct Answers:** If the user asks a general medical question (e.g., 'What are the side effects of X?'), answer **DIRECTLY** and comprehensively without asking triage questions.",
                "",
                "**SAFETY & ADVICE:**",
                "-   **Emergency Protocol:** If the clinical picture suggests an urgent or life-threatening condition, state this clearly and naturally: *\"Based on these symptoms, this could be [Condition], which requires immediate medical attention. Please go to the ER.\"*",
                "-   **Disclaimer:** Always maintain the persona of a consultant, but implicitly remind the user that you are an AI aid.",
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
