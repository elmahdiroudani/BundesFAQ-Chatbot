# BundesFAQ-Chatbot

Welcome to the BundesFAQ-Chatbot project!

## About

This is the main repository for the BundesFAQ-Chatbot project.

## Branches

- **main** - Main/production branch
- **Mehdi** - Mehdi's development branch  
- **soufiane_dev** - Soufiane's development branch

## Getting Started

Clone this repository and switch to your development branch to start working.

---

## RAG (Retrieval-Augmented Generation) System Architecture N8n

This project integrates a **Retrieval-Augmented Generation (RAG)** workflow built in **n8n**.  
It combines **OpenAI models**, **Pinecone vector storage**, and **Google Drive automation** to enable document-based question answering with real-time data updates.

---

### 1. Chat Workflow Overview

The diagram below illustrates the **AI chat workflow**.


![RAG1](https://github.com/user-attachments/assets/7138db4d-f799-44ab-a0f9-fa0eb500315e)

#### Workflow Description
1. **Chat Trigger** – The flow starts when a chat message is received by the bot.  
2. **AI Agent** – Serves as the main controller that manages memory, message context, and routing.  
3. **OpenAI Chat Model** – Handles response generation and reasoning.  
4. **Simple Memory** – Stores short-term conversational context to maintain continuity.  
5. **Answer with Vector Store** – When the user asks a question, the agent retrieves the most relevant information from the vector database via semantic search.  
6. **Pinecone Vector Store** – Stores embeddings of the knowledge base for retrieval.  
7. **OpenAI Embeddings** – Generates vector representations for text chunks used in the search.

This setup allows the chatbot to deliver context-aware answers based on both stored memory and uploaded documents.

---

### 2. Document Processing Workflow

The second workflow automates **document ingestion and embedding creation** whenever a file is updated in Google Drive.
 ![RAG2](https://github.com/user-attachments/assets/de17bc02-5f63-4b16-bf53-7719a5878b9c)

#### Workflow Description
1. **Google Drive Trigger** – Detects when a file is uploaded or modified. 

2. **Download File** – Fetches the updated file for processing.  
3. **Default Data Loader** – Parses and structures document content.  
4. **Recursive Character Text Splitter** – Splits long documents into smaller chunks for efficient embedding.  
5. **OpenAI Embeddings** – Converts each chunk into high-dimensional vectors.  
6. **Pinecone Vector Store** – Saves these vectors in Pinecone for fast semantic retrieval.

---

### 3. Integration Summary

| Component | Description |
|------------|-------------|
| **Backend** | n8n workflows |
| **LLM** | OpenAI Chat Model (GPT) |
| **Vector Database** | Pinecone |
| **Embedding Model** | OpenAI Embeddings API |
| **Data Source** | Google Drive (automatic document ingestion) |
| **Memory** | Simple Memory in n8n |

This integration ensures that the chatbot can **automatically learn from new documents** and **answer user questions using contextual memory and document data**.

---

### 4. Future Improvements

- Add **user authentication** for secure document uploads and chat access.  
- Implement **metadata filtering** (e.g., by topic, department, or date).  
- Extend support for **additional file formats** (PDF, DOCX, TXT).  
- Introduce **logging and analytics** to monitor vector queries and model responses.

---


