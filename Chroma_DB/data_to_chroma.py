import os
import hashlib
import logging
from dotenv import load_dotenv
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

import chromadb

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
TENANT = os.getenv("TENANT_ID")
DATABASE = os.getenv("CHROMA_DATABASE")

SCRAPPED_DATA_COLLECTION = "Scrapped_Data"
EMBEDDINGS_COLLECTION = "Embeddings"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PDF_DIR = os.path.join(PROJECT_ROOT, "Data")

def get_chroma_client():
    """Initializes and returns the appropriate Chroma client (Cloud or Local)."""
    if not CHROMA_API_KEY or CHROMA_API_KEY == "your_chroma_api_key_here":
        db_path = os.path.join(PROJECT_ROOT, "chroma_db_local")
        logger.info(f"Using local ChromaDB at: {db_path}")
        return chromadb.PersistentClient(path=db_path)
    
    logger.info("Connecting to Chroma Cloud...")
    if not TENANT:
        logger.error("TENANT_ID is missing from environment variables.")
        raise RuntimeError("❌ TENANT_ID not set")
    
    return chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=TENANT,
        database=DATABASE or "default"
    )

client = get_chroma_client()
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def generate_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def generate_chunk_id(source: str, page: int, chunk_index: int) -> str:
    return f"{source}_p{page}_c{chunk_index}"

def clear_collection(collection_name: str):
    """Safely deletes all data from a collection if it exists."""
    try:
        logger.info(f"Clearing collection: {collection_name}")
        try:
            collection = client.get_collection(collection_name)
            all_ids = collection.get()['ids']
            if all_ids:
                logger.info(f"Deleting {len(all_ids)} existing documents from {collection_name}")
                # Delete in batches to avoid overhead
                batch_size = 500
                for i in range(0, len(all_ids), batch_size):
                    collection.delete(ids=all_ids[i:i + batch_size])
                logger.info(f"Successfully cleared {collection_name}")
            else:
                logger.info(f"Collection {collection_name} is already empty.")
        except Exception as e:
            logger.info(f"Collection {collection_name} does not exist or is empty. Proceeding.")
    except Exception as e:
        logger.error(f"Error during collection clearing: {str(e)}")

def get_category_from_filename(filename: str) -> str:
    """Categorizes PDFs based on keywords in their filenames."""
    fn = filename.lower()
    if "about" in fn: return "about_us"
    if "internship" in fn: return "internship"
    if "course" in fn or "precat" in fn: return "course"
    return "general"

def load_and_chunk_pdfs() -> Tuple[List[Document], List[str]]:
    """Loads PDFs from the Data directory and splits them into chunks."""
    logger.info(f"Looking for PDFs in: {PDF_DIR}")
    if not os.path.exists(PDF_DIR):
        logger.error(f"Data directory not found: {PDF_DIR}")
        return [], []

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=150)
    documents = []
    ids = []

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        logger.warning("No PDF files found to process.")
        return [], []

    logger.info(f"Processing {len(pdf_files)} PDF files...")

    for file in pdf_files:
        path = os.path.join(PDF_DIR, file)
        category = get_category_from_filename(file)
        logger.info(f"Processing file: {file} (Category: {category})")

        try:
            loader = PyPDFLoader(path)
            pages = loader.load()
            
            for page_no, page in enumerate(pages, start=1):
                chunks = splitter.split_text(page.page_content)
                for idx, chunk in enumerate(chunks):
                    doc_id = generate_chunk_id(file, page_no, idx)
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            "source": file,
                            "page": page_no,
                            "chunk_index": idx,
                            "hash": generate_hash(chunk),
                            "category": category,
                        }
                    ))
                    ids.append(doc_id)
        except Exception as e:
            logger.error(f"Failed to process {file}: {str(e)}")
            continue

    return documents, ids

def upsert_documents():
    """Main pipeline for clearing and uploading data to Chroma."""
    logger.info("🚀 Starting Chroma Data Ingestion Pipeline")
    
    # 1. Prepare Data
    documents, ids = load_and_chunk_pdfs()
    if not documents:
        logger.error("No documents found to upload. Aborting.")
        return

    # 2. Clear Old Data
    clear_collection(SCRAPPED_DATA_COLLECTION)
    clear_collection(EMBEDDINGS_COLLECTION)

    # 3. Upload Text Chunks
    logger.info(f"Uploading {len(documents)} chunks to {SCRAPPED_DATA_COLLECTION}...")
    try:
        Chroma.from_documents(
            documents=documents,
            ids=ids,
            embedding=embedding_model,
            client=client,
            collection_name=SCRAPPED_DATA_COLLECTION
        )
        logger.info(f"Successfully uploaded to {SCRAPPED_DATA_COLLECTION}")
    except Exception as e:
        logger.error(f"Error uploading to {SCRAPPED_DATA_COLLECTION}: {str(e)}")

    # 4. Upload Embeddings Only (Metadata Optimization)
    logger.info(f"Uploading metadata/embeddings to {EMBEDDINGS_COLLECTION}...")
    try:
        # Create minimal documents for the embeddings-only collection
        meta_docs = [
            Document(
                page_content=doc.page_content,
                metadata={
                    "source": doc.metadata["source"],
                    "category": doc.metadata["category"],
                    "chunk_id": ids[i]
                }
            ) for i, doc in enumerate(documents)
        ]
        
        Chroma.from_documents(
            documents=meta_docs,
            ids=ids,
            embedding=embedding_model,
            client=client,
            collection_name=EMBEDDINGS_COLLECTION
        )
        logger.info(f"Successfully uploaded to {EMBEDDINGS_COLLECTION}")
    except Exception as e:
        logger.error(f"Error uploading to {EMBEDDINGS_COLLECTION}: {str(e)}")

    logger.info("✅ Ingestion Pipeline Completed Successfully")

def view_stats():
    """Logs statistics about the collections."""
    for coll_name in [SCRAPPED_DATA_COLLECTION, EMBEDDINGS_COLLECTION]:
        try:
            coll = client.get_collection(coll_name)
            count = coll.count()
            logger.info(f"📊 Collection: {coll_name} | Count: {count}")
        except Exception as e:
            logger.warning(f"Could not retrieve stats for {coll_name}")

if __name__ == "__main__":
    upsert_documents()
    view_stats()