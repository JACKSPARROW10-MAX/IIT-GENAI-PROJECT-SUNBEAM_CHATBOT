import os
from dotenv import load_dotenv
import chromadb
from typing import List, Dict
import json
import requests

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
TENANT_ID = os.getenv("TENANT_ID")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
GROQ_API_KEY = os.getenv("NEW_GROQ_KEY")

if not CHROMA_API_KEY:
    print("⚠️  WARNING: CHROMA_API_KEY not found in environment")
    print("   Please add CHROMA_API_KEY to your .env file")
if not GROQ_API_KEY:
    print("⚠️  WARNING: NEW_GROQ_KEY not found in environment")
    print("   Please add NEW_GROQ_KEY to your .env file")
    print("   Get your API key from: https://console.groq.com/")


class ChromaVectorStore:
    def __init__(self, collection_name: str):
        try:
            if not CHROMA_API_KEY or CHROMA_API_KEY == "your_chroma_api_key_here":
                print("⚠️  WARNING: Using local ChromaDB instead of Cloud (no API key provided)")
                self.client = chromadb.PersistentClient(path=os.path.join(os.getcwd(), "chroma_db_local"))
            else:
                self.client = chromadb.CloudClient(
                    api_key=CHROMA_API_KEY,
                    tenant=TENANT_ID,
                    database=CHROMA_DATABASE
                )
        except Exception as e:
            print(f"⚠️  WARNING: Failed to connect to Chroma Cloud, using local: {str(e)}")
            self.client = chromadb.PersistentClient(path=os.path.join(os.getcwd(), "chroma_db_local"))
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.collection_name = collection_name
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
    
    def search(self, query: str, filter_metadata: Dict = None, k: int = 4) -> List[str]:
        try:
            if filter_metadata:
                docs = self.vectorstore.similarity_search(query, k=k, filter=filter_metadata)
            else:
                docs = self.vectorstore.similarity_search(query, k=k)
            return [doc.page_content for doc in docs] if docs else []
        except Exception as e:
            print(f"[ERROR] Vector search failed: {str(e)}")
            return []


class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 1024, temperature: float = 0.3) -> str:
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            return "⚠️ API Key Error: Please add a valid Groq API key to your .env file. Get your key from https://console.groq.com/"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                return "⚠️ API Key Error: Your Groq API key is invalid or expired. Please check your .env file."
            else:
                print(f"[ERROR] Groq API call failed: {str(e)}")
                return f"I encountered an error processing your request (HTTP {response.status_code})."
        except Exception as e:
            print(f"[ERROR] Groq API call failed: {str(e)}")
            return "I encountered an error processing your request."


scrapped_data_store = ChromaVectorStore("Scrapped_Data")
embeddings_store = ChromaVectorStore("Embeddings")

llm_client = GroqClient(GROQ_API_KEY)


def detect_intent(query: str) -> str:
    aboutus_keywords = [
        "sunbeam", "institute", "organization", "about", "vision", "mission",
        "history", "infrastructure", "location", "campus", "facilities",
        "philosophy", "overview", "establishment", "founder", "accreditation"
    ]
    
    internship_keywords = [
        "internship", "intern", "training program", "batch", "schedule",
        "duration", "internship fee", "training duration", "internship batch",
        "training schedule", "internship timing", "payment schedule"
    ]
    
    courses_keywords = [
        "course", "modular", "pre-cat", "precat", "curriculum", "syllabus",
        "module", "program structure", "course content", "pgcp", "pgcp-ac", 
        "pgcp-ds", "eligibility", "admission", "placement", "career"
    ]
    
    query_lower = query.lower()
    
    aboutus_score = sum(1 for kw in aboutus_keywords if kw in query_lower)
    internship_score = sum(1 for kw in internship_keywords if kw in query_lower)
    courses_score = sum(1 for kw in courses_keywords if kw in query_lower)
    
    print(f"[INTENT] Scores - AboutUs: {aboutus_score}, Internship: {internship_score}, Courses: {courses_score}")
    
    if aboutus_score >= internship_score and aboutus_score >= courses_score and aboutus_score > 0:
        return "aboutus"
    elif internship_score > courses_score and internship_score > 0:
        return "internship"
    elif courses_score > 0:
        return "courses"
    else:
        return "unknown"


def aboutus_tool(query: str) -> str:
    print(f"[TOOL] aboutus_tool | Query: {query}")
    
    docs_scrapped = scrapped_data_store.search(query, filter_metadata={"category": "about_us"}, k=3)
    docs_embeddings = embeddings_store.search(query, filter_metadata={"category": "about_us"}, k=3)
    
    if not docs_scrapped and not docs_embeddings:
        docs_scrapped = scrapped_data_store.search(f"sunbeam organization {query}", k=3)
        docs_embeddings = embeddings_store.search(f"sunbeam organization {query}", k=3)
    
    all_docs = docs_scrapped + docs_embeddings
    
    if not all_docs:
        return "The available About Us information does not contain this detail."
    
    context = "\n\n".join(all_docs)
    
    # Check if API key is valid before calling LLM
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Fallback: return raw context
        return f"📄 **Retrieved Information (No LLM - API Key Missing)**\n\n{context[:2000]}...\n\n⚠️ To get AI-generated answers, please add a valid Groq API key to your .env file. Get your key from: https://console.groq.com/"
    
    messages = [
        {
            "role": "system",
            "content": """You are the Sunbeam Institute AI assistant.

Answer questions using ONLY the provided context about Sunbeam organization.

RULES:
- Answer strictly from the context
- Be concise and factual
- If the context doesn't contain the answer, say: "The available About Us information does not contain this detail."
- Do not add information not in the context
- Focus on: organization, vision, mission, history, infrastructure, facilities"""
        },
        {
            "role": "user",
            "content": f"""CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
    return llm_client.chat(messages)


def internship_tool(query: str) -> str:
    print(f"[TOOL] internship_tool | Query: {query}")
    
    docs_scrapped = scrapped_data_store.search(query, filter_metadata={"category": "internship"}, k=3)
    docs_embeddings = embeddings_store.search(query, filter_metadata={"category": "internship"}, k=3)
    
    if not docs_scrapped and not docs_embeddings:
        docs_scrapped = scrapped_data_store.search(f"internship program fees schedule {query}", k=3)
        docs_embeddings = embeddings_store.search(f"internship program fees schedule {query}", k=3)
    
    all_docs = docs_scrapped + docs_embeddings
    
    if not all_docs:
        return "The internship information does not contain details about this query."
    
    context = "\n\n".join(all_docs)
    
    # Check if API key is valid before calling LLM
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        # Fallback: return raw context
        return f"📄 **Retrieved Information (No LLM - API Key Missing)**\n\n{context[:2000]}...\n\n⚠️ To get AI-generated answers, please add a valid Groq API key to your .env file. Get your key from: https://console.groq.com/"
    
    messages = [
        {
            "role": "system",
            "content": """You are the Sunbeam Institute AI assistant.

Answer questions using ONLY the provided internship context.

RULES:
- Answer strictly from the context about internship programs
- Focus on: duration, batches, schedules, fees, payment structure
- Be concise and factual
- If the context doesn't contain the answer, say: "The internship information does not contain details about this query."
- Do not discuss courses or organizational details here"""
        },
        {
            "role": "user",
            "content": f"""CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
        }
    ]
    
    return llm_client.chat(messages)


def agent_response(user_query: str) -> str:
    print(f"[QUERY] {user_query}")
    
    intent = detect_intent(user_query)
    print(f"[INTENT] Detected: {intent}")
    
    if intent == "aboutus":
        return aboutus_tool(user_query)
    elif intent == "internship":
        return internship_tool(user_query)
    elif intent == "courses":
        return courses_tool(user_query)
    else:
        return """I'd be happy to help! Could you please clarify what you'd like to know about?

- Information about Sunbeam Institute (organization, vision, infrastructure)
- Details about internship programs (duration, fees, schedules)
- Information about courses (modular courses, Pre-CAT, PGCP-AC, PGCP-DS)"""


if __name__ == "__main__":
    print("=" * 70)
    print("SUNBEAM INSTITUTE RAG AGENT - PRODUCTION")
    print("=" * 70)
    
    test_queries = [
        "Tell me about Sunbeam Institute",
        "What is the internship duration?",
        "Explain the modular courses offered",
        "What are the internship fees?",
        "Where is Sunbeam located?"
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 70}")
        response = agent_response(query)
        print(f"\n[RESPONSE]\n{response}")
        print(f"{'=' * 70}\n")