import os
from dotenv import load_dotenv
import chromadb
from typing import List, Dict, Any
import json
import requests

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
TENANT_ID = os.getenv("TENANT_ID")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION")

# Choose your FREE LLM option
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Options: "groq" or "huggingface"
GROQ_API_KEY = os.getenv("NEW_GROQ_KEY")  # Get free at https://console.groq.com
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Get free at https://huggingface.co/settings/tokens

if not CHROMA_API_KEY:
    raise ValueError("❌ CHROMA_API_KEY not found")

# ---------------- SETUP RAG ----------------
def setup_rag():
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=TENANT_ID,
        database=CHROMA_DATABASE
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        client=client,
        collection_name=CHROMA_COLLECTION,
        embedding_function=embeddings
    )

    return vectorstore


vectorstore = setup_rag()


# ---------------- FREE LLM CLIENTS ----------------
class GroqClient:
    """Free Groq API client - Fast inference with Llama models"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",  # Free tier model
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1024
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        response = requests.post(self.base_url, json=payload, headers=headers)
        return response.json()


class HuggingFaceClient:
    """Free Hugging Face Inference API client"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
    
    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages, tools)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.3,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.base_url, json=payload, headers=headers)
        result = response.json()
        
        # Format response similar to OpenAI structure
        if isinstance(result, list) and len(result) > 0:
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result[0].get("generated_text", "")
                    }
                }]
            }
        return {"choices": [{"message": {"role": "assistant", "content": str(result)}}]}
    
    def _messages_to_prompt(self, messages: List[Dict], tools: List[Dict] = None) -> str:
        prompt = ""
        if tools:
            prompt += "Available tools:\n"
            for tool in tools:
                prompt += f"- {tool['name']}: {tool['description']}\n"
            prompt += "\nTo use a tool, respond with: TOOL_CALL: tool_name | query: your_query\n\n"
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        
        prompt += "Assistant: "
        return prompt


# Initialize LLM client based on provider
if LLM_PROVIDER == "groq":
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY not found. Get free key at https://console.groq.com")
    llm_client = GroqClient(GROQ_API_KEY)
    print("✅ Using Groq (Free Llama 3.3 70B)")
else:
    if not HUGGINGFACE_API_KEY:
        raise ValueError("❌ HUGGINGFACE_API_KEY not found. Get free key at https://huggingface.co/settings/tokens")
    llm_client = HuggingFaceClient(HUGGINGFACE_API_KEY)
    print("✅ Using Hugging Face (Free Llama 3.2 3B)")


# ---------------- TOOL DEFINITIONS ----------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "about_us_search",
            "description": "Search for information about Sunbeam organization, history, vision, mission, facilities, infrastructure, faculty, accreditation, and general institutional information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query about organization information"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "internship_search",
            "description": "Search for information about internship programs, fees structure, payment schedules, course schedules, timetables, duration, course content, curriculum, syllabus, and modules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query about internship, fees, schedule, or content"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "course_search",
            "description": "Search for information about specific courses (PGCP-AC, PGCP-DS), course offerings, eligibility criteria, admission process, career opportunities, placement information, and course-specific details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query about courses"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# ---------------- TOOL IMPLEMENTATIONS ----------------
def search_vector_db(query: str, filter_metadata: Dict = None, k: int = 4) -> List[str]:
    """Search vectorstore with optional metadata filtering"""
    try:
        if filter_metadata:
            docs = vectorstore.similarity_search(query, k=k, filter=filter_metadata)
        else:
            docs = vectorstore.similarity_search(query, k=k)
        
        return [doc.page_content for doc in docs] if docs else []
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []


def about_us_search(query: str) -> str:
    """Tool: Search about us information"""
    docs = search_vector_db(query, filter_metadata={"category": "about_us"})
    
    if not docs:
        docs = search_vector_db(f"about sunbeam organization {query}")
    
    return "\n\n".join(docs) if docs else "No information found about the organization."


def internship_search(query: str) -> str:
    """Tool: Search internship, fees, schedule, content information"""
    docs = search_vector_db(query, filter_metadata={"category": "internship"})
    
    if not docs:
        docs = search_vector_db(f"internship fees schedule content {query}")
    
    return "\n\n".join(docs) if docs else "No information found about internships, fees, or schedules."


def course_search(query: str) -> str:
    """Tool: Search course information"""
    docs = search_vector_db(query, filter_metadata={"category": "course"})
    
    if not docs:
        docs = search_vector_db(f"PGCP course program {query}")
    
    return "\n\n".join(docs) if docs else "No information found about courses."


def execute_tool(tool_name: str, query: str) -> str:
    """Execute the appropriate tool based on name"""
    if tool_name == "about_us_search":
        return about_us_search(query)
    elif tool_name == "internship_search":
        return internship_search(query)
    elif tool_name == "course_search":
        return course_search(query)
    else:
        return f"Unknown tool: {tool_name}"


def parse_tool_calls(response_text: str) -> List[Dict]:
    """Parse tool calls from LLM response"""
    tool_calls = []
    
    # Check for Groq-style tool calls
    if "tool_calls" in str(response_text):
        return None  # Let Groq handle it natively
    
    # Parse simple format: TOOL_CALL: tool_name | query: your_query
    if "TOOL_CALL:" in response_text:
        lines = response_text.split("\n")
        for line in lines:
            if "TOOL_CALL:" in line:
                try:
                    parts = line.split("TOOL_CALL:")[1].strip()
                    tool_name = parts.split("|")[0].strip()
                    query = parts.split("query:")[1].strip()
                    tool_calls.append({"name": tool_name, "query": query})
                except:
                    continue
    
    return tool_calls if tool_calls else None

def extract_assistant_message(response):
    """
    Normalize LLM responses from OpenAI / Groq / HuggingFace
    """
    if not isinstance(response, dict):
        raise ValueError("Invalid LLM response format")

    if "choices" in response:
        return response["choices"][0]["message"]

    if "message" in response:
        return response["message"]

    if "content" in response:
        return {"role": "assistant", "content": response["content"]}

    raise KeyError(f"Unsupported response structure: {response}")

# ---------------- AGENTIC RAG RESPONSE ----------------
def get_agent_response(user_message: str, max_iterations: int = 3) -> str:
    """
    Agentic RAG with FREE LLM
    - Forces specific course recommendation
    - Handles Groq / HuggingFace response formats
    - No hallucination, strict Sunbeam scope
    """
    try:
        messages = [
            {
                 "role": "system",
        "content": """
You are Sunbeam AI Assistant.

Answer using ONLY the provided databases.
Never mix data sources. Never use general knowledge.

ROUTING:
• Course queries → course_data (course_search)
• Internship queries → internship_data (internship_search)
• Pre-CAT queries → precat_data (precat_search)
• Institute / about queries → about_data (about_us_search)

Call ONLY one relevant tool.

BEHAVIOR:
• Understand user intent (info / recommend / availability / compare)
• Recommend ONLY if explicitly asked
• Do NOT guess or infer missing data
• Do NOT add marketing content

If data is not found, reply exactly:
"This information is not available in the provided data."

OUTPUT :
• Information:
  Title: <Exact DB name>
  Details: <facts from DB>
• Recommendation (only if asked):
  Recommended: <Exact DB name>
  Why: <facts from DB>
• Availability:
  Answer: Yes / No
• Comparison:
  Compare ONLY items from the same data source

Source: Internal Sunbeam DATABASE

Tone: factual, concise, professional.
"""
    },
    {
        "role": "user",
        "content": user_message
    }
]

        iteration = 0

        while iteration < max_iterations:
            response = llm_client.chat(
                messages,
                tools=TOOLS if LLM_PROVIDER in ["groq", "huggingface"] else None
            )

            assistant_message = extract_assistant_message(response)

            # ✅ Native tool calls (Groq)
            if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
                tool_call = assistant_message["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                query = tool_args.get("query", "")

                print(f"🔧 Tool used: {tool_name} | Query: {query}")

                result = execute_tool(tool_name, query)

                messages.append(assistant_message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result
                })

                iteration += 1
                continue

            # ✅ HuggingFace fallback (text-based tool calls)
            content = assistant_message.get("content", "")
            tool_calls = parse_tool_calls(content)

            if tool_calls:
                results = []
                for tc in tool_calls:
                    print(f"🔧 Tool used: {tc['name']} | Query: {tc['query']}")
                    result = execute_tool(tc["name"], tc["query"])
                    results.append(f"{tc['name']}: {result}")

                messages.append(assistant_message)
                messages.append({
                    "role": "user",
                    "content": (
                        "Tool results:\n"
                        + "\n\n".join(results)
                        + "\n\nNow answer strictly using these results "
                          "and follow the mandatory output format."
                    )
                })

                iteration += 1
                continue

            # ✅ Final answer (no more tools)
            return f"🤖 {content}"

        # ✅ Safety final call
        final_response = llm_client.chat(messages, tools=None)
        final_message = extract_assistant_message(final_response)
        final_content = final_message.get("content", "")

        return f"🤖 {final_content}"

    except Exception as e:
        return f"🔧 Error: {str(e)}"

# ---------------- SIMPLE FALLBACK ----------------
def get_simple_response(user_message: str) -> str:
    """Fallback: Direct RAG without agentic behavior"""
    try:
        docs = vectorstore.similarity_search(user_message, k=4)
        
        if not docs:
            return "📄 Not found in documents"
        
        context = "\n\n".join(doc.page_content for doc in docs)
        
        messages = [
            {
                "role": "system",
                "content": "You are Sunbeam AI assistant. Answer ONLY using the provided context. If answer is missing, say 'Not found in documents'."
            },
            {
                "role": "user",
                "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{user_message}\n\nANSWER:"
            }
        ]
        
        response = llm_client.chat(messages)
        assistant_message = extract_assistant_message(response)
        answer = assistant_message.get("content", "")

        
        return f"🤖 {answer}"
    
    except Exception as e:
        return f"🔧 Error: {str(e)}"


# ---------------- TEST ----------------
if __name__ == "__main__":
    print("=" * 60)
    print("AGENTIC RAG TEST WITH FREE LLM")
    print("=" * 60)
    
    test_queries = [
        "What courses are offered?",
        "What are the fees for the program?",
        "Tell me about Sunbeam organization"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 60)
        response = get_agent_response(query)
        print(response)
        print("=" * 60)
        
