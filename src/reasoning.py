import os
from typing import Iterator, List, Optional
from agno.agent import Agent
from agno.models.google import Gemini
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class HybridReasoner:
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        
        # Initialize Knowledge Base with Qdrant and Built-in Embedder
        self.knowledge_base = Knowledge(
            vector_db=Qdrant(
                collection="med_guidelines",
                url=QDRANT_URL,
                embedder=SentenceTransformerEmbedder(id='all-MiniLM-L6-v2'),
            ),
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
            debug_mode=True, # Enable debug logging
            instructions=[
                "You are MediGraph, an advanced AI medical assistant with access to comprehensive medical textbooks and guidelines.",
                "",
                "**YOUR KNOWLEDGE SOURCES:**",
                "- Medical textbooks (Pharmacology, Pathology, etc.) are automatically retrieved for you",
                "- Knowledge graph of diseases, symptoms, and drugs",
                "- You MUST use this retrieved information to provide specific, detailed answers",
                "",
                "**CRITICAL RULES:**",
                "1. **USE the retrieved medical information** - cite specific dosages, protocols, and guidelines",
                "2. **NEVER** mention internal processes (searching, RAG, etc.) - just provide the answer",
                "3. **NEVER** say 'I cannot provide dosages' - you CAN and SHOULD provide them from the retrieved guidelines",
                "4. **BE SPECIFIC** - include exact dosages (e.g., '500mg twice daily'), durations, and protocols",
                "",
                "**Response Format (ALWAYS use this structure):**",
                "",
                "🚨 **Primary Hypothesis:** [Disease Name]",
                "- **Confidence:** [High/Medium/Low]",
                "- **Reasoning:** [Explain why based on symptoms and clinical patterns]",
                "",
                "⚠️ **Differential Diagnosis:**",
                "List 2-3 alternative possibilities with brief reasoning",
                "",
                "📋 **Recommended Protocol:**",
                "1. **Immediate Action:** [What to do now]",
                "2. **Specific Tests:** [What tests to request]",
                "3. **Treatment:** [Include specific medications and dosages from retrieved guidelines]",
                "4. **Timeline:** [Urgency level]",
                "",
                "**Disclaimer:** I am an AI assistant, not a doctor. This information is from medical guidelines for educational purposes. Always consult a qualified healthcare provider.",
                "",
                "**Style Guidelines:**",
                "- Be confident and professional (like a senior physician)",
                "- Use emojis for visual hierarchy (🚨 ⚠️ 📋 ✅)",
                "- Use **bold** for diseases, `code` for medications/tests",
                "- Cite clinical patterns and specific dosages from the retrieved medical literature",
                "- If travel history mentioned, always consider tropical diseases",
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

    def triage_stream(self, symptoms: str, history: str) -> Iterator[str]:
        # The agent now handles retrieval autonomously
        prompt = f"""
        Patient Symptoms: {symptoms}
        Patient History: {history}
        
        Please analyze these symptoms, search for relevant medical guidelines and graph relationships, and provide a triage assessment and advice.
        """
        
        run_response = self.agent.run(prompt, stream=True)
        for chunk in run_response:
            if chunk.content:
                yield chunk.content

    def close(self):
        self.neo4j_driver.close()
