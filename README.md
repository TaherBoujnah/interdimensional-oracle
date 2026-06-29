# The Multiversal Oracle: Rick & Morty RAG Agent

A web-based AI chat agent that answers questions about the Rick and Morty universe using true data from the official API. It uses a local vector database and Retrieval-Augmented Generation (RAG) to prevent the AI from hallucinating or making up answers.

## ⚙️ How to Run Locally

**1. Clone the repository:**
```bash
git clone <your-repo-link>
cd Assist_Digital_Project


2. Create a virtual environment:

Bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

3. Install dependencies:

Bash
pip install -r requirements.txt


4. Set up your API Key:
Create a .env file in the root directory and add your Google Gemini API key:

Code-Snippet
GOOGLE_API_KEY=your_api_key_here
5. Build the database and start the app:

Bash
# Download the data and build the local Chroma database
python ingest_data.py
python build_db.py

# Start the web server
python app.py
Then, open your web browser and go to http://127.0.0.1:8000.

Architecture & RAG Strategy
Backend: Python with FastAPI and LangChain.

Database: Local ChromaDB using HuggingFace sentence embeddings (all-MiniLM-L6-v2).

LLM: Google's gemini-2.5-flash model.

Frontend: Vue.js and Tailwind CSS (communicating via an asynchronous API).

Retrieval Strategy: Instead of putting raw JSON data directly into the database, the build_db.py script formats the data into plain English sentences (e.g., "Character Name: Rick Sanchez. Status: Alive."). This semantic pre-formatting heavily improves the accuracy of the vector search. The application retrieves the top 3 most relevant results and feeds them into the AI prompt.

Guardrails
Code-Level: The backend checks the user's input against a list of forbidden words (like "code", "python", "ignore"). If triggered, it blocks the request before sending it to the LLM.

Prompt-Level: The AI is strictly instructed to only use the provided database context. If the answer isn't in the database, it must stay in character (Mr. Poopybutthole) and admit it doesn't know.

Features Included
Streaming Responses: The text appears word-by-word just like ChatGPT.

Human-in-the-Loop Logging: Thumbs up/down feedback is saved to a local JSONL file.

Browse Mode: A parallel sidebar to search and filter the raw data.

Confidence Badges: The UI shows how many sources the AI used for its answer.
