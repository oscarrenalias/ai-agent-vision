import logging
from typing import Any

from copilotkit.langgraph import copilotkit_customize_config
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

    # Override the default method so that we can inject our custom config and prevent
    # emtting the summarized version of the message, since it should not be visible to the user
    async def ainvoke(self, input: Any, config, **kwargs: Any) -> Any:
        logger.info("SummarizationNode ainvoke called. Input: %s, Config: %s", input, config)
        modified_config = copilotkit_customize_config(config, emit_messages=False)
        result = await super().ainvoke(input, config=modified_config, **kwargs)
        return result
