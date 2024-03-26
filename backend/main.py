from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import OpenAI
from typing import Any

import pandas as pd
from PyPDF2 import PdfReader
import os
import motor.motor_asyncio

# Load environment variables from .env file (if any)
load_dotenv()

class Response(BaseModel):
    result: str | None

# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:3000",
#     "http://localhost:5173",
# ]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
import os

# os.environ["OPENAI_API_KEY"] = "openai Api key"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB Configuration
# MONGO_DETAILS = "mongodb://localhost:27017"
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.fastapi_db
file_collection = database.get_collection("Files")
result_collection = database.get_collection("results")

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}

# Function to process uploaded PDF file
async def process_pdf(file: UploadFile) -> str:
    raw_text = ''
    reader = PdfReader(file.file)
    for page in reader.pages:
        text = page.extract_text()
        if text:
            raw_text += text
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    return docsearch

# Function to process uploaded text file
async def process_txt(file: UploadFile) -> str:
    raw_text = file.file.read().decode("utf-8")
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=500,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    return docsearch

# Load the QA chain
chain = load_qa_chain(OpenAI(), chain_type="stuff")

# Endpoint to upload PDF file and perform question answering
@app.post("/predict_pdf", response_model=Response)
async def predict_pdf(
    file: UploadFile = File(...),
    query: str = Form(...)
) -> Any:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported")
    docsearch = await process_pdf(file)
    docs = docsearch.similarity_search(query)
    inputs = {'input_documents': docs, 'question': query}
    result = chain.invoke(inputs)
    output_text = result.get('output_text')
    
    # Save file details and results in MongoDB
    file_id = await file_collection.insert_one({"filename": file.filename, "content_type": file.content_type})
    result_id = await result_collection.insert_one({"file_id": file_id.inserted_id, "result": output_text})
    
    return {"result": output_text}

# Endpoint to upload text file and perform question answering
@app.post("/predict_txt", response_model=Response)
async def predict_txt(
    file: UploadFile = File(...),
    query: str = Form(...)
) -> Any:
    if file.content_type != "text/plain":
        raise HTTPException(status_code=415, detail="Only text files (.txt) are supported")
    docsearch = await process_txt(file)
    docs = docsearch.similarity_search(query)
    inputs = {'input_documents': docs, 'question': query}
    result = chain.invoke(inputs)
    output_text = result.get('output_text')
    
    # Save file details and results in MongoDB
    file_id = await file_collection.insert_one({"filename": file.filename, "content_type": file.content_type})
    result_id = await result_collection.insert_one({"file_id": file_id.inserted_id, "result": output_text})
    
    return {"result": output_text}

# Endpoint to upload CSV file and perform analysis
@app.post("/analyze_csv", response_model=Response)
async def analyze_csv(
    file: UploadFile = File(...),
    query: str = Form(...)
) -> Any:
    if file.content_type != "text/csv":
        raise HTTPException(status_code=415, detail="Only CSV files are supported")
    df = pd.read_csv(file.file)
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True)
    output = agent.run(query)
    
    # Save file details and results in MongoDB
    file_id = await file_collection.insert_one({"filename": file.filename, "content_type": file.content_type})
    result_id = await result_collection.insert_one({"file_id": file_id.inserted_id, "result": output})
    
    return {"result": output}
