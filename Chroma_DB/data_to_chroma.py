import os
import hashlib
from dotenv import load_dotenv
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

import chromadb
load_dotenv()

CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
TENANT = os.getenv("TENANT_ID")
DATABASE = os.getenv("CHROMA_DATABASE")

# Two collections
SCRAPPED_DATA_COLLECTION = "Scrapped_Data"  # For text chunks
EMBEDDINGS_COLLECTION = "Embeddings"        # For embeddings only

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PDF_DIR = os.path.join(PROJECT_ROOT, "Data")

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


def clear_collection(collection_name: str):
    """Delete all existing data from a specific collection"""
    try:
        print(f"🗑️  Clearing existing data from collection: {collection_name}")
        
        try:
            collection = client.get_collection(collection_name)
            all_data = collection.get()
            
            if all_data and all_data['ids']:
                print(f"📊 Found {len(all_data['ids'])} existing documents in {collection_name}")
                collection.delete(ids=all_data['ids'])
                print(f"✅ All previous data deleted from {collection_name}")
            else:
                print(f"ℹ️  Collection {collection_name} is already empty")
                
        except Exception as e:
            print(f"ℹ️  Collection {collection_name} doesn't exist or is empty: {e}")
            
    except Exception as e:
        print(f"⚠️  Error during collection clearing: {e}")


def get_category_from_filename(filename: str) -> str:
    """Determine category based on PDF filename"""
    filename_lower = filename.lower()
    if "about" in filename_lower:
        return "about_us"
    elif "internship" in filename_lower:
        return "internship"
    elif "course" in filename_lower or "precat" in filename_lower:
        return "course"
    else:
        return "general"


def load_and_chunk_pdfs():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )

    documents: List[Document] = []
    ids: List[str] = []

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print("⚠️  No PDF files found in directory")
        return documents, ids
    
    print(f"📁 Found {len(pdf_files)} PDF file(s)")

    for file in pdf_files:
        print(f"📄 Processing: {file}")
        
        category = get_category_from_filename(file)
        print(f"   Category: {category}")
        
        try:
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
                                "category": category,
                            }
                        )
                    )

                    ids.append(generate_chunk_id(file, page_no, idx))
            
            print(f"   ✓ Extracted {len([d for d in documents if d.metadata['source'] == file])} chunks from {file}")
        
        except Exception as e:
            print(f"   ❌ Error processing {file}: {str(e)}")
            print(f"   ⚠️  Skipping {file} and continuing with next file...")
            continue

    return documents, ids


def upsert_documents():
    print("=" * 60)
    print("🚀 Starting Fresh Data Upload to Chroma")
    print("=" * 60)
    
    # Step 1: Clear existing data from BOTH collections
    print("\n📦 Clearing both collections...")
    clear_collection(SCRAPPED_DATA_COLLECTION)
    clear_collection(EMBEDDINGS_COLLECTION)
    
    print("\n" + "=" * 60)
    print("📄 Loading and Chunking PDFs")
    print("=" * 60)
    
    # Step 2: Load and chunk PDFs
    documents, ids = load_and_chunk_pdfs()

    if not documents:
        print("❌ No documents to upload")
        return

    print(f"\n📊 Total chunks prepared: {len(documents)}")
    
    # Step 3: Upload to Scrapped_Data collection (text chunks with metadata)
    print("\n" + "=" * 60)
    print(f"☁️  Uploading TEXT CHUNKS to '{SCRAPPED_DATA_COLLECTION}' Collection")
    print("=" * 60)

    vectorstore_scrapped = Chroma(
        client=client,
        collection_name=SCRAPPED_DATA_COLLECTION,
        embedding_function=embedding_model,
    )

    print(f"🔄 Upserting {len(documents)} text chunks...")
    vectorstore_scrapped.add_documents(documents=documents, ids=ids)
    print(f"✅ Text chunks uploaded to '{SCRAPPED_DATA_COLLECTION}'")

    # Step 4: Generate and upload ONLY embeddings to Embeddings collection
    print("\n" + "=" * 60)
    print(f"☁️  Uploading EMBEDDINGS to '{EMBEDDINGS_COLLECTION}' Collection")
    print("=" * 60)

    # Create documents with minimal metadata for embeddings collection
    embedding_documents = []
    for doc, doc_id in zip(documents, ids):
        embedding_documents.append(
            Document(
                page_content=doc.page_content,
                metadata={
                    "source": doc.metadata["source"],
                    "page": doc.metadata["page"],
                    "chunk_id": doc_id,  # Reference to original chunk
                    "category": doc.metadata["category"],
                }
            )
        )

    vectorstore_embeddings = Chroma(
        client=client,
        collection_name=EMBEDDINGS_COLLECTION,
        embedding_function=embedding_model,
    )

    print(f"🔄 Generating and upserting {len(embedding_documents)} embeddings...")
    vectorstore_embeddings.add_documents(documents=embedding_documents, ids=ids)
    print(f"✅ Embeddings uploaded to '{EMBEDDINGS_COLLECTION}'")

    print("\n" + "=" * 60)
    print("✅ Upload Completed Successfully!")
    print("=" * 60)
    print(f"📦 Collection 1: {SCRAPPED_DATA_COLLECTION} - {len(documents)} text chunks")
    print(f"📦 Collection 2: {EMBEDDINGS_COLLECTION} - {len(documents)} embeddings")


def view_collection_stats(collection_name: str):
    """View statistics about a specific collection"""
    try:
        collection = client.get_collection(collection_name)
        all_data = collection.get()
        
        print("\n" + "=" * 60)
        print(f"📊 Collection Statistics: {collection_name}")
        print("=" * 60)
        print(f"Total Documents: {len(all_data['ids']) if all_data['ids'] else 0}")
        
        if all_data['metadatas']:
            sources = set(m.get('source', 'Unknown') for m in all_data['metadatas'])
            print(f"Unique Sources: {len(sources)}")
            print("Source Files:")
            for source in sorted(sources):
                count = sum(1 for m in all_data['metadatas'] if m.get('source') == source)
                print(f"  - {source}: {count} chunks")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error viewing stats for {collection_name}: {e}")


def delete_by_source(source_filename: str, collection_name: str):
    """Delete all chunks for a specific source file from a collection"""
    print(f"🗑️  Deleting all chunks for '{source_filename}' from '{collection_name}'")
    try:
        collection = client.get_collection(collection_name)
        collection.delete(where={"source": source_filename})
        print("✅ Deletion completed")
    except Exception as e:
        print(f"❌ Error during deletion: {e}")


if __name__ == "__main__":
    # Main execution: Clear old data and upload new data to both collections
    upsert_documents()
    
    # View stats for both collections
    view_collection_stats(SCRAPPED_DATA_COLLECTION)
    view_collection_stats(EMBEDDINGS_COLLECTION)