# IIT-GENAI-PROJECT-SUNBEAM_CHATBOT

🧠 SUNBEAM RAG Chatbot :
A Production-Ready Retrieval-Augmented Generation System

📌 Project Overview
SUNBEAM RAG Chatbot is an end-to-end Retrieval-Augmented Generation (RAG) system designed
to answer user queries strictly from organizational data scraped from the Sunbeam website.
The system:
Scrapes dynamic website content
Converts data into structured PDFs
Generates embeddings and stores them in Chroma Cloud
Retrieves relevant context using semantic search
Produces grounded answers using a Cloud LLM
Exposes APIs via FastAPI
Provides an interactive Streamlit chatbot UI
Automatically updates data when the website changes

🎯 Key Objectives
✅ Zero hallucination (answers strictly from retrieved data)
✅ Automated website update detection
✅ Cloud-based scalable vector storage
✅ Modular, production-ready architecture
✅ Easy deployment using Docker

🧩 Core Features
🔹 Web Scraping
Dynamic page handling (Selenium)
Retry & error handling
Metadata capture (URL, timestamp, hash)
🔹 PDF Processing
Structured PDFs with headings
Version control on updates
Section-wise organization
🔹 Vector Database
Chroma Cloud integration
Embedding upserts & deletions
Metadata-based filtering
Similarity search (Top-K)
🔹 RAG Pipeline
Context-aware retrieval
Prompt engineering for grounding
Hallucination prevention
Source-based answers
🔹 Automation
Website change detection (hashing / diff)
Trigger-based re-ingestion
Scheduled jobs (cron / cloud schedulers)
🔹 Frontend
Streamlit chatbot UI
Chat history & session state
Loading & error states
Backend API integration


🏗️ System Architecture :
Website
   ↓
Selenium Scraper
   ↓
Text Cleaning & Chunking
   ↓
PDF Generation (Versioned)
   ↓
Chroma Cloud (Embeddings + Metadata)
   ↓
Retriever (Top-K + Filters)
   ↓
Cloud LLM
   ↓
FastAPI Backend
   ↓
Streamlit Chat UI
