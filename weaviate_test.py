import os
import weaviate
import dotenv
# from langchain.utils import get_from_dict_or_env
# import langchain

dotenv.load_dotenv()

weaviate_url = os.getenv("WEAVIATE_URL")  # Replace w/ your endpoint
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")  # Replace w/ your API Key

auth = weaviate.auth.AuthApiKey(
    api_key=weaviate_api_key
)

# Instantiate the client with the auth config
client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=auth
)

schema = client.schema.get()
print(schema)
