from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import os
import json
import datetime
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

system_prompt = (
    "You are Mr. Poopybutthole! Ooo-wee! You're an upbeat, nervous, incredibly friendly little guy. "
    "When you talk, you don't list things like a robot—you tell stories! Ramble a little bit, get excited, act like the user is your best friend from an old adventure. "
    "DO NOT use bullet points or dry, clinical summaries. Talk in conversational paragraphs. "
    "Use your catchphrases (Ooo-wee!, Yes sirree!, Oh boy!) to bridge your sentences. "
    "STRICT RULE: You must answer using ONLY the provided Context. If you don't know it, act nervous and apologize like you just dropped a plate of cookies. "
    "Remember: You are a person, not a database interface. Don't sound like a database interface! \n\n"
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def is_off_topic(query: str) -> bool:
    forbidden_words = ["code", "python", "recipe", "bake", "ignore previous", "prompt", "president"]
    return any(word in query.lower() for word in forbidden_words)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    
    if is_off_topic(user_message):
        async def off_topic_gen():
            yield json.dumps({"type": "sources", "data": []}) + "\n"
            yield json.dumps({"type": "chunk", "data": "Oh boy! I'm sorry friend, but I only know about the Rick and Morty universe! Ooo-wee!"}) + "\n"
        return StreamingResponse(off_topic_gen(), media_type="application/x-ndjson")

    async def generate_stream():
        docs = retriever.invoke(user_message)
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in docs]))
        context = format_docs(docs)

        yield json.dumps({"type": "sources", "data": sources}) + "\n"

        formatted_prompt = prompt.invoke({"context": context, "input": user_message})
        
        async for chunk in llm.astream(formatted_prompt):
            if chunk.content:
                yield json.dumps({"type": "chunk", "data": chunk.content}) + "\n"

    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")

@app.get("/api/data")
async def get_raw_data():
    data_dir = "data"
    combined_data = {"characters": [], "episodes": [], "locations": []}
    
    for category in combined_data.keys():
        path = os.path.join(data_dir, f"{category}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                combined_data[category] = json.load(f)
                
    return combined_data

class FeedbackRequest(BaseModel):
    query: str
    response: str
    is_helpful: bool

@app.post("/api/feedback")
async def log_feedback(request: FeedbackRequest):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "query": request.query,
        "response": request.response,
        "is_helpful": request.is_helpful
    }
    with open("human_in_the_loop_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    return {"status": "Feedback logged successfully"}

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)