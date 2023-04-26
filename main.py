"""Main entrypoint for the app."""
import os
import dotenv
import weaviate
import logging
import pickle
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain.vectorstores import VectorStore
from langchain.vectorstores.weaviate import Weaviate

from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from query_data import get_chain
from schemas import ChatResponse

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

app = FastAPI()
templates = Jinja2Templates(directory="templates")
vectorstore: Optional[VectorStore] = None


@app.on_event("startup")
async def startup_event():
    logging.info("loading vectorstore")
    # if not Path("vectorstore.pkl").exists():
    #     raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
    # with open("vectorstore.pkl", "rb") as f:
    global vectorstore
    vectorstore = Weaviate(client, "Python", "text")  # pickle.load(f)


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)
    chat_history = []
    qa_chain = get_chain(vectorstore, question_handler, stream_handler)
    # Use the below line instead of the above line to enable tracing
    # Ensure `langchain-server` is running
    # qa_chain = get_chain(vectorstore, question_handler, stream_handler, tracing=True)

    while True:
        try:
            # Receive and send back the client message
            question = await websocket.receive_text()
            resp = ChatResponse(sender="you", message=question, type="stream")
            await websocket.send_json(resp.dict())

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            result = await qa_chain.acall(
                {"question": question, "chat_history": chat_history}
            )
            chat_history.append((question, result["answer"]))

            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())
        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender="bot",
                message="Sorry, something went wrong. Try again.",
                type="error",
            )
            await websocket.send_json(resp.dict())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("ENV_HOST"), port=9000)
