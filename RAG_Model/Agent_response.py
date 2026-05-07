import os
import logging
import chromadb
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration from Environment
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
TENANT_ID = os.getenv("TENANT_ID")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
GROQ_API_KEY = os.getenv("NEW_GROQ_KEY")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class SunbeamRAGAgent:
    def __init__(self):
        self._init_vector_stores()
        self._init_llm_client()
        
    def _init_vector_stores(self):
        """Initializes connection to Chroma collections."""
        try:
            if not CHROMA_API_KEY or CHROMA_API_KEY == "your_chroma_api_key_here":
                db_path = os.path.join(PROJECT_ROOT, "chroma_db_local")
                logger.info(f"RAG Agent using local ChromaDB at {db_path}")
                self.client = chromadb.PersistentClient(path=db_path)
            else:
                logger.info("RAG Agent connecting to Chroma Cloud...")
                self.client = chromadb.CloudClient(
                    api_key=CHROMA_API_KEY,
                    tenant=TENANT_ID,
                    database=CHROMA_DATABASE or "default"
                )
            
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            # Map collections
            self.scrapped_store = Chroma(
                client=self.client,
                collection_name="Scrapped_Data",
                embedding_function=self.embeddings
            )
            logger.info("Vector stores initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Vector Stores: {str(e)}")
            raise

    def _init_llm_client(self):
        """Initializes the Groq client."""
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            logger.warning("No valid GROQ_API_KEY found. LLM features will be disabled.")
            self.llm = None
        else:
            try:
                self.llm = Groq(api_key=GROQ_API_KEY)
                logger.info("Groq LLM client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {str(e)}")
                self.llm = None

    def detect_intent(self, query: str) -> str:
        """Heuristic intent detection based on keywords."""
        q = query.lower()
        if any(k in q for k in ["sunbeam", "about", "vision", "mission", "founder", "infrastructure", "location"]):
            return "about_us"
        if any(k in q for k in ["internship", "stipend", "batch", "training"]):
            return "internship"
        if any(k in q for k in ["course", "precat", "pre-cat", "pgcp", "modular", "syllabus", "fees"]):
            return "course"
        return "general"

    def search_context(self, query: str, category: str, k: int = 4) -> List[Dict[str, Any]]:
        """Searches Chroma for relevant chunks in a specific category."""
        logger.info(f"Searching context for category: {category} | Query: {query}")
        try:
            results = self.scrapped_store.similarity_search_with_score(
                query, 
                k=k, 
                filter={"category": category}
            )
            # Flatten to a list of dicts with content and metadata
            return [{"content": doc.page_content, "metadata": doc.metadata} for doc, score in results]
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []

    def generate_response(self, query: str) -> str:
        """Main entry point for generating an agentic RAG response."""
        intent = self.detect_intent(query)
        logger.info(f"Detected Intent: {intent}")
        
        # 1. Retrieve Context
        context_items = self.search_context(query, intent)
        
        # If no specific intent matched or no results found, try a general search
        if not context_items and intent != "general":
            logger.info("Falling back to general search...")
            context_items = self.search_context(query, "general")
        
        if not context_items:
            return "I couldn't find specific information about that in the Sunbeam records. Could you please clarify your question?"

        context_text = "\n\n---\n\n".join([item["content"] for item in context_items])
        sources = list(set([item["metadata"].get("source", "Unknown") for item in context_items]))

        # 2. Call LLM
        if not self.llm:
            return f"📄 **Retrieved Context (LLM Offline):**\n\n{context_text[:500]}...\n\n⚠️ *Please add a valid GROQ_API_KEY to see AI-generated answers.*"

        system_prompt = self._get_system_prompt(intent)
        
        try:
            completion = self.llm.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CONTEXT:\n{context_text}\n\nQUESTION:\n{query}"}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            
            response = completion.choices[0].message.content
            
            # Append sources if useful
            if sources:
                response += f"\n\n**Sources:** {', '.join(sources)}"
            
            return response
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return "I encountered an error while processing your request with the AI model."

    def _get_system_prompt(self, intent: str) -> str:
        """Returns specialized system prompts based on intent."""
        base = "You are the Sunbeam Institute AI assistant. Answer using ONLY the provided context."
        
        prompts = {
            "about_us": f"{base} Focus on organizational history, vision, mission, and infrastructure.",
            "internship": f"{base} Focus on internship batches, durations, fees, and schedules. Use tables if appropriate.",
            "course": f"{base} Focus on modular courses, Pre-CAT, curriculum, eligibility, and fees.",
            "general": f"{base} Provide a concise and helpful summary based on the available Sunbeam information."
        }
        return prompts.get(intent, base)

# Singleton instance for the UI to import
rag_agent = SunbeamRAGAgent()

def agent_response(query: str) -> str:
    """Wrapper for backward compatibility with the UI."""
    return rag_agent.generate_response(query)

if __name__ == "__main__":
    # Test block
    print(agent_response("Tell me about Sunbeam founder and mission"))