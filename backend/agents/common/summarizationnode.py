import logging
from typing import Any

from langmem.short_term import SummarizationNode

from agents.models import OpenAIModel

logger = logging.getLogger(__name__)


class SummarizationNode(SummarizationNode):
    """
    A node that summarizes messages using a model.

    Based on LangMem's SummarizationNode.
    """

    # OpenAI model to use for summarization
    MODEL_NAME = "gpt-4o"

    # constants for token limits
    MAX_TOKENS = 256
    MAX_TOKENS_BEFORE_SUMMARY = 1024
    MAX_SUMMARY_TOKENS = 128

    # message keys
    INPUT_MESSAGES_KEY = "messages"
    OUTPUT_MESSAGES_KEY = "messages_summary"

    def __init__(self):
        logger.info("Initializing SummarizationNode with model gpt-4o")
        model = OpenAIModel(openai_model="gpt-4o").get_model().bind(max_tokens=256)
        super().__init__(
            token_counter=model.get_num_tokens_from_messages,
            model=model,
            max_tokens=self.MAX_TOKENS,
            max_tokens_before_summary=self.MAX_TOKENS_BEFORE_SUMMARY,
            max_summary_tokens=self.MAX_SUMMARY_TOKENS,
            input_messages_key=self.INPUT_MESSAGES_KEY,
            output_messages_key=self.OUTPUT_MESSAGES_KEY,
        )

    def _func(self, *args, **kwargs) -> dict[str, Any]:
        logger.info("SummarizationNode _func called. Parameters: %s, %s", args, kwargs)
        result = super()._func(*args, **kwargs)
        return result

    def _afunc(self, *args, **kwargs) -> dict[str, Any]:
        logger.info("SummarizationNode _afunc called. Parameters: %s, %s", args, kwargs)
        result = super()._afunc(*args, **kwargs)
        return result
