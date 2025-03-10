from pathlib import Path
from typing import Any, Optional

from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings
from app.utils.vector_database.expand_query import expand_query
from app.utils.vector_database.retrieve_and_rerank_doc import retrieve_top_chunks

class VectorDatabase:
    """A class to manage vector database operations using Chroma."""
    
    DEFAULT_PERSIST_DIR = Path("./storage")
    
    def __init__(
        self, 
        collection_name: str,
        document: Any,
        embeddings: Any,
        persist_directory: Optional[Path] = None,
        client_settings: Optional[dict] = None
    ):
        """Initialize the vector database.
        
        Args:
            collection_name: Name of the collection to create/manage
            persist_directory: Directory to store the database (default: ./storage)
            client_settings: Additional settings for ChromaDB client
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or self.DEFAULT_PERSIST_DIR
        self.client_settings = client_settings or {}
        
        # Initialize client and setup storage
        self._initialize_storage()
        self.vector_db = self._create_vector_database(document=document,embeddings=embeddings)
        
    def _initialize_storage(self) -> None:
        """Initialize storage and client configuration."""
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                **self.client_settings
            )
        )
        
        self._reset_collection()
        
    def _reset_collection(self) -> None:
        """Reset the collection if it exists and create a new one."""
        existing_collections = [col.name for col in self.client.list_collections()]
        
        if self.collection_name in existing_collections:
            self.client.delete_collection(name=self.collection_name)
        
        self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "l2"}
        )
            
    def _create_vector_database(
        self,
        document: Any,
        embeddings: Any,
        distance_metric: str = "l2",
        max_connections: int = 16
    ) -> Chroma:
        """Create a vector database from documents.
        
        Args:
            document: Preprocessed document containing splited_document
            embeddings: Embedding model to use
            distance_metric: Distance metric for HNSW algorithm
            max_connections: Maximum connections per layer in HNSW
            
        Returns:
            Chroma: Initialized vector database
        """
        if not hasattr(document, 'splited_document'):
            raise ValueError("Document must have 'splited_document' attribute")
            
        vector_db = Chroma.from_documents(
            documents=document.splited_document,  # Assuming 'document' is defined elsewhere
            embedding=embeddings,
            client=self.client,
            collection_name=self.collection_name,
            collection_metadata={
                "hnsw:space": distance_metric,           # Distance metric (L2, like Milvus/Qdrant defaults)
                "hnsw:M": max_connections,                 # Max connections per layer
            },
            ids=[f"{doc.metadata['source']}_page_{doc.metadata['page']}" for doc in document.splited_document]
        )
        
        return vector_db

    def search(self, query: str, k: int = 5):
        """Search for similar vectors in the database.

        Args:
            query: Query text to search
            embeddings: Embedding model to generate query vector
            k: Number of nearest neighbors to return

        Returns:
            List of search results
        """
        
        expanded_query = expand_query(query)
        
        retriever = self.vector_db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "lambda_mult": 0.5})
        
        top_chunks = retrieve_top_chunks(query=query, alt_queries=expanded_query, retriever=retriever)
        
        joined_chunk = "\n\n".join([doc.page_content for doc in top_chunks[0:5]])
        
        return joined_chunk