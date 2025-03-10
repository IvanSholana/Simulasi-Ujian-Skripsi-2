from typing import List, Optional
from dataclasses import dataclass
from langchain.text_splitter import TextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

@dataclass
class DocumentPreparation(TextSplitter):
    """A class to handle document preparation and splitting into paragraphs.
    
    This class extends TextSplitter to provide functionality for loading PDF documents
    and splitting them into meaningful paragraphs.
    """
    
    document_loader: Optional[List[Document]] = None
    splited_document: Optional[List[Document]] = None

    def __init__(self,data_path:str) -> None:
        """Initialize document loader and process document splitting after instance creation."""
        self.document_loader = PyPDFLoader(data_path).load()
        self.splited_document = self.split_documents_by_paragraph(self.document_loader)

    def split_text(self, text: str) -> List[str]:
        """Split text into paragraphs by removing excess whitespace and splitting on double newlines.
        
        Args:
            text (str): The input text to be split.
            
        Returns:
            List[str]: A list of paragraphs.
        """
        cleaned_lines = [line.strip() for line in text.split("\n") if line.strip()]
        normalized_text = "\n".join(cleaned_lines)
        return normalized_text.split("\n\n")

    def split_documents_by_paragraph(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks based on paragraphs.
        
        Args:
            documents (List[Document]): List of documents to be split.
            
        Returns:
            List[Document]: List of split documents where each document represents a paragraph.
        """
        split_documents = []
        
        for document in documents:
            paragraphs = self.split_text(document.page_content)
            split_documents.extend([
                Document(
                    page_content=paragraph,
                    metadata=document.metadata.copy()
                ) for paragraph in paragraphs
            ])
        
        return split_documents