import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


class KnowledgeBase:
    def __init__(self, persist_directory: str = "./chroma"):
        self.persist_directory = persist_directory
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vector_store = None

    def load_document(self, file_path: str) -> List[Document]:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        return loader.load()

    def load_documents_from_directory(self, directory: str) -> List[Document]:
        documents = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    docs = self.load_document(file_path)
                    documents.extend(docs)
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        return documents

    def split_documents(self, documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        return text_splitter.split_documents(documents)

    def build_vector_store(self, documents: List[Document]):
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.vector_store.persist()

    def load_vector_store(self):
        if os.path.exists(self.persist_directory):
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return True
        return False

    def add_documents(self, documents: List[Document]):
        if self.vector_store is None:
            self.build_vector_store(documents)
        else:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()

    def search(self, query: str, k: int = 3) -> List[Document]:
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call build_vector_store or load_vector_store first.")
        
        docs = self.vector_store.similarity_search(query, k=k)
        return docs

    def get_document_count(self) -> int:
        if self.vector_store is None:
            return 0
        return self.vector_store._collection.count()

    def clear(self):
        import shutil
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
        self.vector_store = None


def main():
    kb = KnowledgeBase()
    
    docs = kb.load_documents_from_directory("./documents")
    print(f"Loaded {len(docs)} documents")
    
    split_docs = kb.split_documents(docs)
    print(f"Split into {len(split_docs)} chunks")
    
    kb.build_vector_store(split_docs)
    print("Vector store built successfully")
    
    results = kb.search("自然语言处理")
    print(f"Found {len(results)} relevant chunks")
    for i, doc in enumerate(results):
        print(f"\nResult {i+1}:")
        print(doc.page_content[:200] + "...")


if __name__ == "__main__":
    main()
