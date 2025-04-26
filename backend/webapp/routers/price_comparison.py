import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage
from pydantic import BaseModel

from agents.pricecomparison.agent import PriceComparisonFlow

# Create a module-specific logger
logger = logging.getLogger("webapp.routers.price_comparison")


class PriceComparisonRequest(BaseModel):
    item: str


class PriceComparisonResponse(BaseModel):
    result: str


# Create a router for price comparison endpoints
router = APIRouter(prefix="/api", tags=["price_comparison"])


@router.post("/price-comparison", response_model=PriceComparisonResponse)
async def compare_prices(request: PriceComparisonRequest) -> Dict[str, Any]:
    """
    Compare prices for a given item across different stores
    """
    try:
        logger.info(f"Received price comparison request for item: {request.item}")

        # Initialize the price comparison flow
        price_comparison_manager = PriceComparisonFlow()

        # Run the price comparison
        result = price_comparison_manager.run(request.item)

        # Extract the last assistant message from the result
        messages = result.get("messages", [])
        assistant_messages = [msg for msg in messages if isinstance(msg, AIMessage)]

        if assistant_messages:
            # Get the most recent assistant message
            response_content = assistant_messages[-1].content
        else:
            response_content = "No comparison results available."

        logger.info(f"Price comparison completed for item: {request.item}")

        return {"result": response_content}

    except Exception as e:
        logger.error(f"Error during price comparison: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Error comparing prices: {str(e)}")
