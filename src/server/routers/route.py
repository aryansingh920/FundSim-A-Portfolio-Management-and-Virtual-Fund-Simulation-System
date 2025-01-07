from datetime import datetime
from fastapi import APIRouter, Path, Query, HTTPException
from typing import Any, Dict, Optional
from server.controller.send_visualise import get_candlestick_chart, get_subplot_chart
from server.controller.generate_stock import stock_data_controller
from server.controller.generate_bond import bond_data_controller
# Create a FastAPI router
router = APIRouter()


@router.get('/generate_stocks', summary="Generate Stock Data", response_model=Dict[str, Any])
def generate_stocks(
    number_of_stocks: int = Query(
        default=3, ge=1, le=20, description="Number of stocks to generate (1-20)"),
    start_date: Optional[str] = Query(
        default='2020-01-01', description="Start date in YYYY-MM-DD format"),
    days: int = Query(default=365, ge=1, le=1825,
                      description="Number of days of historical data (1-1825)")
):
    """
    Generate stock data with configurable parameters.

    Args:
        number_of_stocks (int): Number of stocks to generate.
        start_date (str): Start date for historical data.
        days (int): Number of days of historical data.

    Returns:
        Generated stock data.
    """
    # Validate and parse start date
    try:
        parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid date format. Use YYYY-MM-DD",
                "example": "2020-01-01"
            }
        )

    # Call the stock data controller with parameters
    return stock_data_controller(
        number_of_stocks=number_of_stocks,
        start_date=parsed_start_date,
        days=days
    )


@router.get('/generate_bonds', summary="Generate Bond Data", response_model=Dict[str, Any])
def generate_bonds(
    number_of_bonds: int = Query(
        default=3, ge=1, le=20, description="Number of bonds to generate (1-20)"),
    days: int = Query(default=365, ge=1, le=1825,
                      description="Number of days of historical data (1-1825)")
):
    """
    Generate bond data with configurable parameters.

    Args:
        number_of_bonds (int): Number of bonds to generate.
        start_date (str): Start date for historical data.
        days (int): Number of days of historical data.

    Returns:
        Generated bond data.
    """
    # Validate and parse start date
    # try:
    #     parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d')
    # except ValueError:
    # raise HTTPException(
    #     status_code=400,
    #     detail={
    #         "error": "Invalid date format. Use YYYY-MM-DD",
    #         "example": "2020-01-01"
    #     }
    # )

    # Call the bond data controller with parameters
    return bond_data_controller(
        number_of_bonds=number_of_bonds,
        # start_date=parsed_start_date,
        days=days
    )


@router.get("/candlestick/{ticker}", summary="Get Candlestick Chart")
def candlestick_chart(
    ticker: str = Path(..., description="The stock ticker symbol")
):
    """
    Fetch the candlestick chart for the given ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        HTML of the candlestick chart or an error message.
    """
    return get_candlestick_chart(ticker)


@router.get("/subplot/{ticker}/{start_date}/{end_date}", summary="Get Subplot Chart")
def subplot_chart(
    ticker: str = Path(..., description="The stock ticker symbol"),
    start_date: str = Path(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Path(..., description="End date in YYYY-MM-DD format")
):
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
