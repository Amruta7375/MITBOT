# 🤖 MITBOT — AI-Powered PDF Question Answering System

MITBOT is an **AI-powered PDF question-answering application** built with Python and Streamlit.

The system allows users to upload or access PDF documents and ask questions in natural language. MITBOT processes the documents, converts their content into vector embeddings, stores them in a FAISS vector database, and uses **Google Gemini** with a Retrieval-Augmented Generation (RAG) pipeline to generate answers based on the document context.

It also provides **user authentication, admin controls, PDF management, chat history, bookmarks, user uploads, and source references**.

---

## 📌 Project Overview

MITBOT is designed to make it easier to interact with large PDF documents.

Instead of manually searching through hundreds of pages, users can ask questions such as:

> "What is the main objective of this document?"

> "Explain the methodology used in this research paper."

> "What are the important findings mentioned in the PDF?"

MITBOT retrieves the most relevant document content and provides an AI-generated answer based on that context.

The application follows a **Retrieval-Augmented Generation (RAG)** architecture.

---

## ✨ Features

### 👤 User Features

* User registration
* Secure login
* Password authentication
* Password reset functionality
* PDF/document upload
* AI-powered document question answering
* Chat interface
* Chat history
* Bookmark important answers
* View uploaded documents
* Source document references
* Page-level source information

### 🛠️ Admin Features

* Admin dashboard
* Upload PDF documents
* Manage PDF documents
* Manage users
* View user history
* Model configuration/settings
* Document management

### 🤖 AI Features

* Retrieval-Augmented Generation (RAG)
* Google Gemini LLM integration
* LangChain-based question answering
* Sentence Transformer embeddings
* FAISS vector similarity search
* Context-based responses
* Source document retrieval
* Page number references
* Prompt-based answer generation
* Reduced hallucination using context-restricted prompting

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │       User           │
                    │                      │
                    │  Ask PDF Question    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Streamlit UI     │
                    │                      │
                    │ Login / Chat / Admin │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Question Handler   │
                    │                      │
                    │   User Question      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FAISS Vector DB   │
                    │                      │
                    │ Similarity Search    │
                    └──────────┬───────────┘
                               │
                         Relevant Chunks
                               │
                               ▼
                    ┌──────────────────────┐
                    │      LangChain       │
                    │    RetrievalQA       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Google Gemini     │
                    │       LLM            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Final Answer    │
                    │                      │
                    │ + Source File        │
                    │ + Page Number        │
                    └──────────────────────┘
```

---

# 🔄 How MITBOT Works

The application follows these major steps:

### 1. PDF Upload

An administrator or authorized user uploads a PDF document.

```text
PDF Document
     ↓
Document Processing
```

### 2. Text Extraction

Text is extracted from the PDF using PDF processing libraries.

```text
PDF
 ↓
Text Extraction
 ↓
Clean Text
```

### 3. Text Chunking

Large documents are divided into smaller chunks so that relevant sections can be retrieved efficiently.

```text
Large Document
      ↓
Text Chunks
      ↓
Chunk 1
Chunk 2
Chunk 3
...
```

### 4. Embedding Generation

The text chunks are converted into numerical vector representations using **Sentence Transformers**.

```text
Text Chunk
    ↓
Sentence Transformer
    ↓
Embedding Vector
```

### 5. FAISS Vector Storage

The generated embeddings are stored in a FAISS vector database.

FAISS allows MITBOT to perform efficient similarity searches over document embeddings.

```text
Embeddings
     ↓
FAISS
     ↓
Vector Index
```

### 6. User Question

The user asks a question in the chat interface.

```text
"What is the main objective of this document?"
```

### 7. Similarity Search

MITBOT converts the question into an embedding and searches FAISS for the most relevant document chunks.

```text
User Question
      ↓
Question Embedding
      ↓
FAISS Similarity Search
      ↓
Relevant Document Chunks
```

### 8. Retrieval-Augmented Generation

The retrieved document context is passed to the LangChain RetrievalQA pipeline.

```text
Question
   +
Relevant Context
   ↓
LangChain RetrievalQA
```

### 9. Gemini Generates the Answer

Google Gemini generates the final answer using the retrieved context.

The application instructs the model to answer using the provided context and respond with "I don't know" when the required information is not available.

### 10. Source Information

MITBOT also returns the source document and page information used for the answer.

```text
Answer

Sources:
File: example.pdf
Page: 12
```

---

# 🧠 RAG Architecture

MITBOT uses **Retrieval-Augmented Generation (RAG)**.

RAG combines two major processes:

```text
Retrieval
    +
Generation
```

### Retrieval

Relevant information is retrieved from the document vector database.

### Generation

Google Gemini generates the answer using the retrieved context.

```text
PDF
 ↓
Text
 ↓
Chunks
 ↓
Embeddings
 ↓
FAISS
 ↓
Retrieve Relevant Chunks
 ↓
Gemini
 ↓
Answer
```

This approach helps the application answer questions based on the uploaded documents instead of relying only on the model's general knowledge.

---

# 🛠️ Tech Stack

| Technology            | Purpose                         |
| --------------------- | ------------------------------- |
| Python                | Core programming language       |
| Streamlit             | Web application interface       |
| LangChain             | RAG and LLM orchestration       |
| Google Gemini         | Large Language Model            |
| FAISS                 | Vector similarity search        |
| Sentence Transformers | Text embeddings                 |
| PyPDF2                | PDF processing                  |
| SQLite                | Application database            |
| bcrypt                | Password hashing                |
| python-dotenv         | Environment variable management |
| pdfkit                | PDF generation                  |
| WeasyPrint            | Document/PDF rendering          |
| Pydantic              | Data validation                 |

The repository's current `requirements.txt` includes Streamlit, LangChain packages, Google Gemini integration, FAISS, Sentence Transformers, PyPDF2, bcrypt, SQLite-related application code, and other supporting libraries.

---

# 📂 Project Structure

```text
MITBOT/
│
├── data/
│   └── PDF documents
│
├── vectorstore/
│   └── db_faiss/
│       └── FAISS vector database
│
├── app.py
│   └── Main Streamlit application
│
├── auth.py
│   └── User authentication
│
├── admin.py
│   └── Admin dashboard and document management
│
├── user_pages.py
│   └── User interface, chat, history and bookmarks
│
├── db.py
│   └── Database connection and operations
│
├── llm.py
│   └── Gemini + LangChain RAG pipeline
│
├── vectorstore.py
│   └── FAISS vector store creation/loading
│
├── settings.py
│   └── Application/model settings
│
├── utils.py
│   └── Utility functions
│
├── requirements.txt
│   └── Python dependencies
│
├── .env
│   └── Environment variables
│
└── mitbot_db.sqlite
    └── SQLite application database
```

---

# 🔐 Authentication

MITBOT includes an authentication system.

Users can:

* Register
* Login
* Reset passwords
* Access their personal features

Passwords are handled using **bcrypt** hashing rather than storing plain-text passwords.

---

# 👨‍💼 Admin Dashboard

The application provides an administrative interface for managing the system.

Admin functionality includes:

* Dashboard
* PDF upload
* PDF management
* User management
* User history
* Model settings

This separates administrative operations from normal user operations.

---

# 💬 User Chat

After authentication, users can interact with the document chatbot.

Example:

```text
User:
Explain the conclusion of this PDF.

MITBOT:
The conclusion states that ...

Sources:
File: research_paper.pdf
Page: 18
```

---

# 📚 Source References

One of the important features of MITBOT is source tracking.

The RAG pipeline returns the documents used to generate the response.

Example:

```text
Sources:

File: research_paper.pdf
Page: 15

File: research_paper.pdf
Page: 17
```

This makes it easier for users to verify the answer against the original document.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/maheshmadane/MITBOT.git
```

Move into the project directory:

```bash
cd MITBOT
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

You should see:

```text
(.venv)
```

in your terminal.

---

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

Replace:

```text
your_google_gemini_api_key
```

with your own API key.

### ⚠️ Security

Never commit your `.env` file to GitHub.

Add the following to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
*.sqlite
```

If an API key has already been pushed to a public repository, revoke/rotate that key and create a new one.

---

# ▶️ Run the Application

Run:

```powershell
streamlit run app.py
```

Or:

```powershell
python -m streamlit run app.py
```

Streamlit's official documentation uses the same `streamlit run app.py` approach for starting a Streamlit application.

After starting the application, Streamlit normally provides a local address such as:

```text
http://localhost:8501
```

Open that address in your browser.

---

# 📋 Requirements

Recommended environment:

```text
Python 3.10+
pip
Virtual Environment
Google Gemini API Key
```

Install all Python dependencies using:

```bash
pip install -r requirements.txt
```

---

# 🧪 Example Workflow

### Step 1

Start the application:

```bash
streamlit run app.py
```

### Step 2

Login/Register.

### Step 3

Upload or select a PDF document.

### Step 4

Allow MITBOT to process the document.

### Step 5

Ask a question.

Example:

```text
What are the key findings of this document?
```

### Step 6

MITBOT retrieves relevant document sections.

### Step 7

Gemini generates the answer.

### Step 8

MITBOT displays the answer and source pages.

---

# 🧩 Main Components

## `app.py`

The main Streamlit application.

It connects the authentication system, admin functionality, user pages, database and other application components.

---

## `auth.py`

Responsible for user authentication functionality such as:

```text
Registration
Login
Password Reset
Authentication
```

---

## `admin.py`

Contains administrative functionality including:

```text
Admin Dashboard
PDF Upload
PDF Management
User History
Model Settings
```

---

## `user_pages.py`

Handles user-facing functionality such as:

```text
Chat
History
Bookmarks
User Uploads
```

---

## `db.py`

Handles database connectivity and database-related operations.

The project uses SQLite for application data.

---

## `vectorstore.py`

Responsible for working with the FAISS vector database.

The vector store contains document embeddings that are used during similarity search.

---

## `llm.py`

This is the main AI/RAG component.

It:

1. Loads the configured Gemini model.
2. Loads the FAISS vector store.
3. Retrieves relevant documents.
4. Uses LangChain RetrievalQA.
5. Sends context and the user's question to Gemini.
6. Returns the generated answer.
7. Returns source document/page information.

The current implementation uses `ChatGoogleGenerativeAI`, LangChain `RetrievalQA`, and FAISS retrieval.

---

# 🧠 Technologies Explained

### Python

Used as the main programming language.

### Streamlit

Used to build the interactive web application.

### LangChain

Used to connect document retrieval and the LLM into a RAG pipeline.

### Google Gemini

Used as the generative AI model.

### FAISS

Used for vector similarity search.

### Sentence Transformers

Used to convert document text into embeddings.

### SQLite

Used for application data storage.

### bcrypt

Used for password hashing.

---

# 🔍 Why FAISS?

FAISS is used to efficiently search through vector embeddings.

For example:

```text
PDF contains:

"Python is a high-level programming language."

User asks:

"What is Python?"
```

The question is converted into an embedding.

FAISS searches for the closest document vectors and returns the relevant text.

---

# 🤖 Why RAG?

A traditional LLM may not know the contents of a user's private PDF.

RAG solves this by providing relevant document information to the LLM.

```text
Without RAG:

Question → LLM → Answer

With RAG:

Question
   ↓
Vector Search
   ↓
Relevant Document
   ↓
Context
   ↓
LLM
   ↓
Answer
```

---

# 🔒 Security Considerations

For production deployment:

* Never commit `.env`
* Never expose API keys
* Use environment variables for secrets
* Do not commit local databases containing private user data
* Use strong passwords
* Keep dependencies updated
* Validate uploaded files
* Restrict administrator access
* Apply proper database access controls

---

# 🚀 Future Enhancements

Possible future improvements include:

* [ ] Deploy application to Streamlit Cloud
* [ ] Add Docker support
* [ ] Add PostgreSQL support
* [ ] Add multi-document conversations
* [ ] Improve document chunking
* [ ] Add OCR support for scanned PDFs
* [ ] Add voice-based questions
* [ ] Add multilingual document support
* [ ] Add conversation export
* [ ] Add document summarization
* [ ] Add citation highlighting
* [ ] Add improved role-based access control
* [ ] Add automated testing
* [ ] Add CI/CD using GitHub Actions
* [ ] Add application monitoring

---

# 📊 Project Highlights

MITBOT demonstrates practical implementation of:

```text
Python
   ↓
Streamlit
   ↓
PDF Processing
   ↓
Text Chunking
   ↓
Embeddings
   ↓
FAISS
   ↓
LangChain
   ↓
Google Gemini
   ↓
RAG
   ↓
AI-Powered Answers
```

It also demonstrates full application functionality including:

```text
Authentication
Admin Dashboard
Database
Document Management
AI Chat
Chat History
Bookmarks
Source Tracking
```

---

# 🎯 Use Cases

MITBOT can be useful for:

* Research papers
* Educational material
* Technical documentation
* Company documents
* Project reports
* Books
* Manuals
* Study material
* Policy documents
* PDF-based knowledge bases

---

# 🧑‍💻 Author

**Mahesh Madane**

Python Developer | AI/ML Enthusiast

GitHub:

https://github.com/maheshmadane

Project:

https://github.com/maheshmadane/MITBOT

---

# 📄 License

This project is intended for educational and development purposes.

Add an appropriate open-source license to the repository if you intend to distribute the project publicly.

---

# ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

**Thank you for checking out MITBOT! 🤖**
