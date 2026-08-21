from sqlalchemy import text

from app.db.database import engine
from app.rag.embedder import create_embedding


def search_chunks(query: str, limit: int = 5):
    query_embedding = create_embedding(query)

    sql = text("""
        SELECT
            c.id,
            c.document_id,
            d.filename,
            c.text,
            c.page_start,
            c.page_end,
            1 - (c.embedding <=> CAST(:embedding AS vector)) AS similarity
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE c.embedding IS NOT NULL
        ORDER BY c.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "limit": limit
            }
        )

        return [
            {
                "id": str(row.id),
                "document_id": str(row.document_id),
                "filename": row.filename,
                "text": row.text,
                "page_start": row.page_start,
                "page_end": row.page_end,
                "similarity": float(row.similarity)
            }
            for row in result
        ]