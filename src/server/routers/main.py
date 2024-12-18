from fastapi import APIRouter
from server.controller.send_visualise import get_candlestick_chart

# Create a FastAPI router
router = APIRouter()

# Define the route and bind it to the handler


@router.get("/candlestick/{ticker}", summary="Get Candlestick Chart")
def candlestick_chart(ticker: str):
    """
    Fetch the candlestick chart for the given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        HTML of the candlestick chart or an error message.
    """
    return get_candlestick_chart(ticker)
