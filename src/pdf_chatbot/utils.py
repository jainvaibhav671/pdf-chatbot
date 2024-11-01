from fastapi import UploadFile
import nanoid
import os
import logging
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.google_vector_store import ServerSideEmbedding
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from pdf_chatbot.constants import PUBLIC_FOLDER, LOGS, SYSTEM_PROMPT

logging.basicConfig(filename="logs.log", level=logging.INFO)


def generate_session_id() -> str:
    """
    Generate a unique session ID
    """

    return nanoid.generate(size=8)


def save_file(file: UploadFile) -> str:
    """
    Save the file to the public folder with a unique name
    and return the path
    """

    file_name = file.filename

    file_name = f"{nanoid.generate(size=4)}-{file_name}".replace(" ", "-")
    file_path = os.path.join(PUBLIC_FOLDER, file_name)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path


def read_pdf(file_path: str) -> List[Document]:
    loader = PyPDFLoader(file_path)
    return loader.load()


def init_chat_model(file_path):
    docs = read_pdf(file_path)

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vector_store = InMemoryVectorStore.from_documents(
        documents=splits, embedding=ServerSideEmbedding()
    )
    retreiver = vector_store.as_retriever()

    prompt = ChatPromptTemplate(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retreiver, question_answer_chain)

    return rag_chain


def get_logger(name: str):
    """
    Get a logger with the given name
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


def log(logger: logging.Logger, *message: str, level: str = "debug"):
    """
    Log a message with a given level if logs are enabled
    """

    if not LOGS:
        return

    if level == "debug":
        logger.debug(" ".join(message))
    elif level == "info":
        logger.info(" ".join(message))
    elif level == "warning":
        logger.warning(" ".join(message))
    elif level == "error":
        logger.error(" ".join(message))
