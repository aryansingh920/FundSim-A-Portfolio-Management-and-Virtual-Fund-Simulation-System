from fastapi import APIRouter
from server.controller.send_visualise import get_candlestick_chart, get_subplot_chart

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


@router.get("/subplot/{ticker}/{start_date}/{end_date}", summary="Get Subplot Chart, enter date in format YYYY-MM-DD")
def subplot_chart(ticker: str, start_date: str, end_date: str):
    """
    Fetch the subplot chart for the given ticker and date range.
    Args:
    ticker (str): The stock ticker symbol.
    start_date (str): The start date for the data range.
    end_date (str): The end date for the data range.
    Returns:
    HTML of the subplot chart or an error message.
    """
    return get_subplot_chart(ticker, start_date, end_date)
