import os
from dotenv import load_dotenv
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

load_dotenv()


def setup_rag():
    """ONLY your installed packages"""
    # YOUR CHROMA CLOUD (exact setup)
    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        tenant=os.getenv("TENANT_ID"),
        database=os.getenv("CHROMA_DATABASE")
    )
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(
        client=client,
        collection_name=os.getenv("CHROMA_COLLECTION"),
        embedding_function=embeddings
    )
    
    llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("groq_Api"), temperature=0)
    
    return llm, vectorstore

# Initialize (uses your existing installs)
llm, vectorstore = setup_rag()

def get_agent_response(user_message: str) -> str:
    """✅ NO NEW LIBRARIES - Pure RAG"""
    try:
        # 1. Search your PDFs
        docs = vectorstore.similarity_search(user_message, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 2. Smart prompt (your PG programs)
        prompt = f"""
You are Sunbeam AI assistant for PG programs (PGCP-AC, PGCP-DS).

CONTEXT FROM YOUR PDFs:
{context}

QUESTION: {user_message}

Answer using ONLY the PDF context above. Be concise and helpful.
If no relevant info found, say "Not found in documents".
"""
        
        # 3. Groq response (your installed package)
        response = llm.invoke(prompt)
        
        return f"🤖 **{response.content}**\n\n📄 *From Sunbeam PDFs*"
        
    except Exception as e:
        return f"🔧 **Error:** {str(e)[:100]}\nCheck ChromaDB/Groq keys"

# Test
if __name__ == "__main__":
    print(get_agent_response("What are the courses?"))
