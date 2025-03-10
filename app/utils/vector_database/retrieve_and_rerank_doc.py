from sentence_transformers import CrossEncoder
from typing import List
from langchain.schema import Document

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Retrieval and reranking function (aligned with Milvus/Qdrant approach)
def retrieve_and_rerank_single_query(query: str, cross_encoder,m, retriever,) -> List[Document]:
    """Retrieve and rerank documents for a single query."""
    retrieved_docs = retriever.invoke(query)
    inputs = [(query, doc.page_content) for doc in retrieved_docs]
    scores = cross_encoder.predict(inputs)
    scored_docs = list(zip(retrieved_docs, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in scored_docs[:m]]

def retrieve_top_chunks(query: str, alt_queries: List[str], retriever, k: int = 5, m: int = 2, final_n: int = 5) -> List[Document]:
    """Retrieve and rerank documents across multiple queries, returning the top N unique results."""
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    all_top_chunks = []
    
    # Retrieve and rerank for the main query and alternative queries
    for q in [query] + alt_queries:
        top_m = retrieve_and_rerank_single_query(q,cross_encoder, m=m, retriever=retriever)
        all_top_chunks.extend(top_m)
    
    # Remove duplicates based on document content
    seen_texts = set()
    unique_top_chunks = []
    for doc in all_top_chunks:  
        text = doc.page_content.strip()
        if text not in seen_texts:
            seen_texts.add(text)
            unique_top_chunks.append(doc)
    
    # Final reranking if more than final_n documents
    if len(unique_top_chunks) > final_n:
        inputs = [(query, doc.page_content) for doc in unique_top_chunks]
        scores = cross_encoder.predict(inputs)
        scored_unique = list(zip(unique_top_chunks, scores))
        scored_unique.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_unique[:final_n]]
    
    return unique_top_chunks