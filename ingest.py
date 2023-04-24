"""Load html from files, clean up, split, ingest into Weaviate."""
import weaviate
import os
import dotenv
import dill as pickle
from langchain.document_loaders import ReadTheDocsLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Weaviate
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import UnstructuredURLLoader
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import TextLoader

dotenv.load_dotenv(".env")

auth_config = weaviate.auth.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))

# Instantiate the client with the auth config
client = weaviate.Client(
    url=os.getenv("WEAVIATE_URL"),  # Replace w/ your endpoint
    auth_client_secret=auth_config  # Replace w/ your API Key for the Weaviate instance
)

# Instantiate the client with the auth config
# client = weaviate.Client(
#     url=os.getenv("WEAVIATE_URL"),
#     auth_client_secret=auth_config
# )

weaviate = Weaviate(client, "langchain", "text")

def ingest_docs():
    """Get documents from web pages."""
    # loader = UnstructuredURLLoader(urls=["https://python.langchain.com/en/latest/"])
    loader = DirectoryLoader('./devguide.python.org', loader_cls=TextLoader)
    # loader = ReadTheDocsLoader("python.langchain.com/en/latest")
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectorstore = weaviate.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()
