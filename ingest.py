"""Load html from files, clean up, split, ingest into Weaviate."""
import os
import dill as pickle
import weaviate
import dotenv
# from langchain.document_loaders import ReadTheDocsLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Weaviate
# from langchain.vectorstores.faiss import FAISS
# from langchain.document_loaders import UnstructuredURLLoader
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import TextLoader

dotenv.load_dotenv()

weaviate_url = os.getenv("WEAVIATE_URL")  # Replace w/ your endpoint
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")  # Replace w/ your Weaviate API Key
openai_api_key = os.getenv("OPENAI_API_KEY")  # Replace w/ your OpenAI API Key

auth = weaviate.auth.AuthApiKey(
    api_key=weaviate_api_key
)

# Instantiate the client with the auth config
client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=auth
)

weaviate = Weaviate(client, "Python", "text")


def ingest_docs():
    """Get documents from web pages."""
    # loader = UnstructuredURLLoader(urls=["https://python.langchain.com/en/latest/"])
    loader = DirectoryLoader('./devguide.python.org', loader_cls=TextLoader)
    # loader = ReadTheDocsLoader("python.langchain.com/en/latest/")
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = weaviate.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()
