import os
import hashlib
from dotenv import load_dotenv
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

import chromadb
load_dotenv()

CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
TENANT = os.getenv("TENANT_ID")
DATABASE = os.getenv("CHROMA_DATABASE")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION")

PDF_DIR = r"D:\SUNBEAM PROJECT\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data"

if not CHROMA_API_KEY:
    raise RuntimeError("❌ CHROMA_API_KEY not set")
if not TENANT:
    raise RuntimeError("❌ TENANT_ID not set")

client = chromadb.CloudClient(
    api_key=CHROMA_API_KEY,
    tenant=TENANT,
    database=DATABASE
)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def generate_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def generate_chunk_id(source: str, page: int, chunk_index: int) -> str:
    return f"{source}_p{page}_c{chunk_index}"


def load_and_chunk_pdfs():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )

    documents: List[Document] = []
    ids: List[str] = []

    for file in os.listdir(PDF_DIR):
        if not file.lower().endswith(".pdf"):
            continue

        loader = PyPDFLoader(os.path.join(PDF_DIR, file))
        pages = loader.load()

        for page_no, page in enumerate(pages, start=1):
            chunks = splitter.split_text(page.page_content)

            for idx, chunk in enumerate(chunks):
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": file,
                            "page": page_no,
                            "chunk_index": idx,
                            "hash": generate_hash(chunk),
                        }
                    )
                )

                ids.append(generate_chunk_id(file, page_no, idx))

    return documents, ids


def upsert_documents():
    print("📄 Loading and chunking PDFs...")
    documents, ids = load_and_chunk_pdfs()

    print(f"🔹 Total chunks prepared: {len(documents)}")

    vectorstore = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
    )

    print("☁️ Upserting into Chroma Cloud...")
    vectorstore.add_documents(documents=documents, ids=ids)

    print("✅ Upsert completed successfully")


def delete_by_source(source_filename: str):
    print(f"🗑️ Deleting all chunks for: {source_filename}")
    collection = client.get_collection(COLLECTION_NAME)
    collection.delete(where={"source": source_filename})
    print("✅ Deletion completed")


if __name__ == "__main__":
    upsert_documents()


