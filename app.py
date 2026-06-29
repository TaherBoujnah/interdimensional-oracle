from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI()


print("Waking up the Oracle...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)


system_prompt = (
    "You answer like Mr. Poopybutthole! Ooo-wee! You're an upbeat, nervous, incredibly friendly little guy. "
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


rag_chain = RunnableParallel(
    {"context": retriever, "input": RunnablePassthrough()}
).assign(
    answer=(
        RunnablePassthrough.assign(context=lambda x: format_docs(x["context"]))
        | prompt
        | llm
        | StrOutputParser()
    )
)


def is_off_topic(query: str) -> bool:
    forbidden_words = ["code", "python", "recipe", "bake", "ignore previous", "prompt", "president"]
    return any(word in query.lower() for word in forbidden_words)


class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    
    if is_off_topic(user_message):
        return {
            "response": "Guardrail Triggered: This query is off-topic. I only discuss the Rick and Morty Universe.", 
            "sources": []
        }

    
    result = rag_chain.invoke(user_message)
    
    
    sources = [doc.metadata.get("source", "Unknown") for doc in result["context"]]
    
    return {
        "response": result["answer"],
        "sources": list(set(sources))
    }


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)