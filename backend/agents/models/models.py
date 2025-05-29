import logging
import os

from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def Model(id: str):
    if id == "openai":
        return OpenAIModel()
    else:
        raise Exception(f"Model {id} not found")


class OpenAIModel:
    """
    Handles the initialization and interaction with the OpenAI model.
    """

    model: ChatOpenAI

    openai_model = "gpt-4o"

    use_cache: bool = True

    def __init__(self, openai_model: str = "gpt-4o", use_cache: bool = True):
        self.openai_model = openai_model
        self.use_cache = use_cache
        self.initialize_model()

    def initialize_model(self):
        # set temperature to 1 if the model has "mini" in its name since the parameter is not supported
        temperature = 1.0 if "mini" in self.openai_model else 0.0

        self.model = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=self.openai_model,
            temperature=temperature,
            verbose=True,
        )

        logger.info(f"Initializing OpenAI model: {self.openai_model}")

        if self.use_cache:
            logger.info(
                "Using LLM cache to speed things up. Keep this in mind if results do not change when altering prompts!"
            )
            set_llm_cache(SQLiteCache(database_path=".langchain.db"))

    def get_model(self):
        return self.model
