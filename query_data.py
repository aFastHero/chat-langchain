"""Create a ConversationalRetrievalChain for question/answering."""
import os
import dotenv
from langchain.callbacks.base import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT,
                                                     QA_PROMPT)
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever

from langchain.schema import Document
from typing import List

dotenv.load_dotenv()

async def aget_relevant_documents(self, query: str) -> List[Document]:
    return self.get_relevant_documents(query)

VectorStoreRetriever.aget_relevant_documents = aget_relevant_documents

def get_chain(
    vectorstore: VectorStore, question_handler, stream_handler, tracing: bool = False
) -> ConversationalRetrievalChain:
    """Create a ConversationalRetrievalChain for question/answering."""
    # Construct a ConversationalRetrievalChain with a streaming llm for combine docs
    # and a separate, non-streaming llm for question generation
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])
    if tracing:
        tracer = LangChainTracer()
        tracer.load_default_session()
        manager.add_handler(tracer)
        question_manager.add_handler(tracer)
        stream_manager.add_handler(tracer)

    question_gen_llm = OpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
        verbose=True,
        callback_manager=question_manager,
    )
    streaming_llm = OpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        temperature=0,
    )

    question_generator = LLMChain(
        llm=question_gen_llm, prompt=CONDENSE_QUESTION_PROMPT, callback_manager=manager
    )
    doc_chain = load_qa_chain(
        streaming_llm, chain_type="stuff", prompt=QA_PROMPT, callback_manager=manager
    )

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        callback_manager=manager,
    )
    return qa
