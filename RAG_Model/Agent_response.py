import os
from dotenv import load_dotenv
import chromadb

from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_chroma import Chroma

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline




load_dotenv()

CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
TENANT_ID = os.getenv("TENANT_ID")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION")

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

    model_name = "google/flan-t5-base"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        temperature=0
    )

    llm = HuggingFacePipeline(pipeline=pipe)

    return llm, vectorstore


llm, vectorstore = setup_rag()

# ---------------- RAG RESPONSE ----------------
def get_agent_response(user_message: str) -> str:
    try:
        docs = vectorstore.similarity_search(user_message, k=3)

        if not docs:
            return "📄 Not found in documents"

        context = "\n\n".join(doc.page_content for doc in docs)

        prompt = f"""
You are Sunbeam AI assistant for PG programs (PGCP-AC, PGCP-DS).

Answer ONLY using the context below.
If answer is missing, say "Not found in documents".

CONTEXT:
{context}

QUESTION:
{user_message}

ANSWER:
"""

        response = llm.invoke(prompt)

        return f"🤖 {response}\n\n📄 Source: Sunbeam PDFs"

    except Exception as e:
        return f"🔧 Error: {str(e)}"


# ---------------- TEST ----------------
if __name__ == "__main__":
    print(get_agent_response("What are the courses offered?"))
