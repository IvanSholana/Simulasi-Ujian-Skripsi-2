from pathlib import Path
from typing import Any, Optional

from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings

class VectorDatabase:
    """A class to manage vector database operations using Chroma."""
    
    DEFAULT_PERSIST_DIR = Path("./storage")
    
    def __init__(
        self, 
        collection_name: str,
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
            
    def create_vector_database(
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
            documents=document.splited_document,
            embedding=embeddings,
                        persist_directory=str(self.persist_directory),
            collection_name=self.collection_name,
            client=self.client,
            distance_metric=distance_metric,
            max_connections=max_connections
        )
        
        return vector_db
    
    def add_documents(self, documents: Any, embeddings: Any) -> None:
        """Add documents to the vector database.

        Args:
            documents: Preprocessed documents containing splited_document
            embeddings: OpenAIEmbeddings instance
        """
        if not hasattr(documents, 'splited_document'):
            raise ValueError("Documents must have 'splited_document' attribute")
        
        # Ekstrak page_content dari setiap Document
        text_list = [doc.page_content for doc in documents.splited_document]
        
        # Dapatkan embeddings dari daftar teks
        embeddings_list = embeddings.embed_documents(text_list)

        # Tambahkan ke koleksi vektor dengan text_list
        collection = self.client.get_collection(name=self.collection_name)
        collection.add(
            ids=[str(i) for i in range(len(documents.splited_document))],
            documents=text_list,  # Gunakan text_list, bukan documents.splited_document
            embeddings=embeddings_list
        )

    def search(self, query: str, embeddings: Any, k: int = 5):
        """Search for similar vectors in the database.

        Args:
            query: Query text to search
            embeddings: Embedding model to generate query vector
            k: Number of nearest neighbors to return

        Returns:
            List of search results
        """
        collection = self.client.get_collection(name=self.collection_name)
        query_vector = embeddings.embed(query)
        return collection.query(query_vector, n_results=k)