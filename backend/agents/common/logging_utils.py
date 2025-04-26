# Utility for logging only relevant fields from LLM responses


def llm_response_to_log(response, extra_fields=None):
    """
    Extract only the relevant fields from an LLM response object for logging.
    Returns a dict suitable for logging or further processing.
    """
    if hasattr(response, "content"):
        data = {"content": response.content}
        if hasattr(response, "role"):
            data["role"] = response.role
        if extra_fields:
            for field in extra_fields:
                if hasattr(response, field):
                    data[field] = getattr(response, field)
        return data
    else:
        return response


def log_llm_response(response, logger, extra_fields=None):
    """
    Log only the relevant fields from an LLM response object.
    """
    data = llm_response_to_log(response, extra_fields=extra_fields)
    logger.info(f"LLM response: {data}")
