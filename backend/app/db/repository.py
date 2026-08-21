from sqlalchemy import text

from app.db.database import engine


def create_document(filename: str):
    query = text("""
        INSERT INTO documents (filename)
        VALUES (:filename)
        RETURNING id
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {"filename": filename}
        )

        return result.scalar()


def create_chunks(document_id, chunks):
    query = text("""
        INSERT INTO chunks (
            document_id,
            text,
            page_start,
            page_end,
            embedding
        )
        VALUES (
            :document_id,
            :text,
            :page_start,
            :page_end,
            CAST(:embedding AS vector)
        )
    """)

    rows = []

    for chunk in chunks:
        rows.append({
            "document_id": document_id,
            "text": chunk["text"],
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "embedding": str(chunk["embedding"])
        })

    with engine.begin() as connection:
        connection.execute(query, rows)