from typing import AsyncGenerator
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models import ChatRequest
from logger_config import logger
import faiss
import os
import asyncio

FAISS_PATH = "faiss_vector_store"
FAQ_PATH = "datasets/faq.csv"

class RAGManager:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(temperature=0.2, model="gemini-2.0-flash")
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.vector_store = None
        self.load_vector_store()
        logger.info("Vector store loaded successfully.")
        self.chain = self.get_chain()

    def load_vector_store(self, faiss_path=FAISS_PATH):
        """Loads the vector store from disk if it exists, otherwise creates a new one."""
        if os.path.exists(faiss_path):
            try:
                self.vector_store = FAISS.load_local(faiss_path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                logger.error(f"Error loading FAISS vector store: {e}")
                self.vector_store = None
        else:
            index = faiss.IndexHNSWFlat(768, 10)  # (emb_size, n_neighbors)
            self.vector_store = FAISS(embedding_function=self.embeddings,
                                      index=index,  # where to store the vectors
                                      docstore=InMemoryDocstore(),  # where to store documents metadata
                                      index_to_docstore_id={}  # how to map index to docstore
                                      )
            self.ingest_faq_dataset()
            self.vector_store.save_local(faiss_path)

    def ingest_faq_dataset(self, faq_path=FAQ_PATH):
        """Load the dataset and add the documents to the vector store."""
        loader = CSVLoader(file_path=faq_path, source_column="Question")
        docs = loader.load()
        self.vector_store.add_documents(documents=docs)
        
    def get_chain(self) -> RunnableSerializable:
        """Returns the chain for the RAG process."""
        prompt = hub.pull("rlm/rag-prompt")
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})
        return (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
    async def chat(self, prompt: str) -> AsyncGenerator[str, None]:
        """Handles the chat interaction."""
        try:
            async for chunk in self.chain.astream(prompt):
                yield chunk
                await asyncio.sleep(0.1)  ## Simulate a delay for streaming effect
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            yield "Sorry, I couldn't process your request at the moment."
           
# Initialize the RAG manager
faq_manager = RAGManager()

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/faq")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(faq_manager.chat(request.prompt), media_type="text/plain")
