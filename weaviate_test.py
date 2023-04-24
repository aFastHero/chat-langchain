import weaviate
import os
import dotenv

dotenv.load_dotenv()

auth_config = weaviate.auth.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))  # Replace w/ your API Key for the Weaviate instance

# Instantiate the client with the auth config
client = weaviate.Client(
    url=os.getenv("WEAVIATE_URL"),  # Replace w/ your endpoint
    auth_client_secret=auth_config
)

schema = client.schema.get()
print(schema)


