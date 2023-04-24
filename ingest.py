"""Load html from files, clean up, split, ingest into Weaviate."""
import pickle
import os
import weaviate
from langchain.document_loaders import ReadTheDocsLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.weaviate import Weaviate
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import UnstructuredURLLoader
import dotenv

dotenv.load_dotenv()

client = weaviate.Client(
    url=os.getenv("WEAVIATE_URL"),
    auth_client_secret=weaviate.auth.AuthClientPassword(
        username = os.getenv("WEAVIATE_USERNAME"),
        password = os.getenv("WEAVIATE_PASSWORD"),
    ))  # Replace w/ your API Key for the Weaviate instance

# Instantiate the client with the auth config
# client = weaviate.Client(
#     url=os.getenv("WEAVIATE_URL"),
#     auth_client_secret=auth_config
# )

weaviate = Weaviate(client, "python", "text")

def ingest_docs():
    """Get documents from web pages."""
    # loader = UnstructuredURLLoader(urls=["https://python.langchain.com/en/latest/"])
    loader = ReadTheDocsLoader("python.langchain.com/en/latest/")
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()
