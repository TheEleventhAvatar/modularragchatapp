from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil

from app.ingestion.parser import extract_pdf
from app.ingestion.chunker import chunk_pages
from app.rag.embedder import create_embeddings
from app.rag.retriever import search_chunks
from app.rag.generator import generate_answer
from app.db.repository import create_document, create_chunks


app = FastAPI(title="Modular RAG PDF Chat")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Modular RAG API is running",
    }


@app.post("/documents/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        return {
            "error": "Only PDF files are supported"
        }

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages = extract_pdf(str(file_path))
    chunks = chunk_pages(pages)

    texts = [chunk["text"] for chunk in chunks]
    embeddings = create_embeddings(texts)

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding

    document_id = create_document(file.filename)

    create_chunks(
        document_id,
        chunks,
    )

    return {
        "filename": file.filename,
        "document_id": str(document_id),
        "pages": len(pages),
        "chunks": len(chunks),
        "status": "stored",
    }


@app.post("/chat")
async def chat(question: str):

    chunks = search_chunks(
        question,
        limit=5,
    )

    if not chunks:
        return {
            "answer": "I couldn't find any relevant information in the provided PDFs.",
            "sources": [],
        }

    answer = generate_answer(
        question,
        chunks,
    )

    unique_sources = {}

    for chunk in chunks:
        key = (
            chunk["filename"],
            chunk["page_start"],
            chunk["page_end"],
        )

        if key not in unique_sources:
            unique_sources[key] = {
                "filename": chunk["filename"],
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
            }

    sources = list(unique_sources.values())

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }