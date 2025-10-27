import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import chromadb
import os
import io
from pypdf import PdfReader
class RAG():
    def __init__(self):
        self.embedding_function = OpenAIEmbeddings(
            openai_api_key=os.environ["API_KEY"],
            openai_api_base="https://api.ai.it.cornell.edu",
            model="openai.text-embedding-3-small"
        )
        self.chroma_client = chromadb.Client()
        
        self.db = Chroma(
            client=self.chroma_client,
            collection_name="rag_collection",
            embedding_function=self.embedding_function
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
        )
        
        self.file_to_ids = {}

    def handle_files(self, current_file_names, previous_file_names, current_files_in_widget):
        added_file_names = current_file_names - previous_file_names
        deleted_file_names = previous_file_names - current_file_names

        if added_file_names:
            self._add_files(added_file_names, current_files_in_widget)
            return True
        
        if deleted_file_names:
            self._delete_files(deleted_file_names.pop())
            return True
        
        return False

    
    def _add_files(self, added_file_names, current_files_in_widget):
        for file_name in added_file_names:
            file_obj = next((f for f in current_files_in_widget if f.name == file_name), None)
            
            if file_obj:
                content = "" 
                file_obj.seek(0)
                if file_obj.name.endswith(".pdf"):
                    try:
                        pdf_bytes = file_obj.read()
                        pdf_stream = io.BytesIO(pdf_bytes)
                        reader = PdfReader(pdf_stream)
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                content += page_text + "\n"
                    except Exception as e:
                        print("PDF read error")
                        continue 
                
                elif file_obj.name.endswith((".txt", ".md")):
                    try:
                        content = file_obj.read().decode("utf-8")
                    except Exception as e:
                        print("TXT, MD read error")
                        continue 

                chunks = self.text_splitter.split_text(content)
                metadatas = [{"filename": file_name, "source": file_name} for _ in chunks]
                ids = [str(uuid.uuid4()) for _ in chunks]
                
                self.db.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
                self.file_to_ids[file_name] = ids

    def _delete_files(self, deleted_file_name):
        if deleted_file_name in self.file_to_ids:
            ids_to_delete = self.file_to_ids.pop(deleted_file_name, None)
            if ids_to_delete:
                try:
                    self.db.delete(ids=ids_to_delete)
                    return True
                except Exception as e:
                    print(f"Error deleting chunks for {deleted_file_name}: {e}")
        return False
    
    def retrieve_chunks(self, query, search_type="mmr", k=5):
        if search_type == "mmr":
            # fetch_k: get 10 chunks and use MMR to get 5
            retriever = self.db.as_retriever(
                search_type="mmr",
                search_kwargs={'k': k, 'fetch_k': 10}
            )
        else:
            retriever = self.db.as_retriever(
                search_type="similarity",
                search_kwargs={'k': k}
            )
        
        return retriever.invoke(query)