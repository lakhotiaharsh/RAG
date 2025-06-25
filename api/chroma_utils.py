from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from typing import List
from langchain_core.documents import Document
import os

# Configure text splitter and persistent Chroma client
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, length_function=len)
client = chromadb.PersistentClient(path="./chroma_db")
vectorstore = client.get_or_create_collection("documents")


def load_and_split_document(file_path: str) -> List[Document]:
    """
    Load a document from disk and split it into chunks.
    Supported formats: PDF, DOCX, HTML.
    """
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    return text_splitter.split_documents(documents)


def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    """
    Index a document by splitting into chunks, assigning unique IDs,
    and storing metadata for each chunk for easy deletion later.
    """
    try:
        splits = load_and_split_document(file_path)
        
        # Prepare data for Chroma
        documents = [split.page_content for split in splits]
        metadatas = []
        ids = []
        for i, split in enumerate(splits):
            # Unique chunk ID: combine file_id with chunk index
            unique_id = f"{file_id}_{i}"
            ids.append(unique_id)
            # Attach file_id and optional source path to metadata
            md = split.metadata.copy()
            md['file_id'] = str(file_id)
            md['source'] = os.path.basename(file_path)
            metadatas.append(md)

        # Upsert chunks into the collection
        vectorstore.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        #vectorstore.persist()
        return True

    except Exception as e:
        print(f"Error indexing document: {e}")
        return False


def delete_doc_from_chroma(file_id: int) -> bool:
    """
    Delete all indexed chunks associated with a given file_id.
    """
    try:
        # Retrieve chunks by metadata filter
        results = vectorstore.get(where={"file_id": str(file_id)})
        total = len(results.get('ids', []))
        print(f"Found {total} document chunks for file_id {file_id}")
        
        # Delete using metadata filter
        vectorstore.delete(where={"file_id": str(file_id)})
        #vectorstore.persist()
        print(f"Deleted all documents with file_id {file_id}")
        return True

    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {e}")
        return False
