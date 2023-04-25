import os
import weaviate
import dotenv
# from langchain.utils import get_from_dict_or_env
# import langchain

dotenv.load_dotenv()

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

# weaviate_url = get_from_dict_or_env(kwargs, "weaviate_url", "WEAVIATE_URL")
# weaviate_api_key = get_from_dict_or_env(
#     kwargs, "weaviate_api_key", "WEAVIATE_API_KEY", None
# )

auth_config = weaviate.auth.AuthApiKey(
    api_key=weaviate_api_key  # os.getenv("WEAVIATE_API_KEY")
)  # Replace w/ your API Key for the Weaviate instance

# Instantiate the client with the auth config
client = weaviate.Client(
    url=weaviate_url, # os.getenv("WEAVIATE_URL"),  # Replace w/ your endpoint
    auth_client_secret=auth_config
)

schema = client.schema.get()
print(schema)
