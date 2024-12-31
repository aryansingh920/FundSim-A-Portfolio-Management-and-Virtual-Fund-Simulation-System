"""
Created on 29/12/2024

@author: Aryan

Filename: generate_stock.py

Relative Path: src/server/controller/generate_stock.py
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException
# Import the main stock data generation function
from assets.stocks.main import main


def stock_data_controller(
    number_of_stocks: int = 3,
    start_date: datetime = datetime(2020, 1, 1),
    days: int = 365
) -> Dict[str, Any]:
    """
    Controller function to generate stock data for FastAPI
    
    :param number_of_stocks: Number of stocks to generate
    :param start_date: Start date for historical data
    :param days: Number of days of historical data to generate
    :return: Dictionary with stock data
    """
    try:
        # Generate stock data
        all_stock_data = main(number_of_stocks, start_date, days)

        # Prepare response dictionary
        response_data = {
            "total_stocks": len(all_stock_data),
            "stocks": {}
        }

        # Process each stock
        for ticker, stock_info in all_stock_data.items():
            # Prepare stock details
            stock_details = {
                "basic_info": stock_info["stock_info"],
                "price_info": stock_info["price_trading_info"],
                "fundamentals": stock_info["fundamental_metrics"],
                "risk_metrics": stock_info["volatility_risk"],
                "market_indicators": stock_info["market_indicators"]
            }

            # Add performance summary
            historical_data = stock_info["historical_data"]
            performance_summary = {
                "total_return_percent": round(
                    (historical_data[-1]["close_price"] /
                     historical_data[0]["close_price"] - 1) * 100, 2
                ),
                "start_price": historical_data[0]["close_price"],
                "end_price": historical_data[-1]["close_price"],
                "highest_price": max(day["close_price"] for day in historical_data),
                "lowest_price": min(day["close_price"] for day in historical_data)
            }
            stock_details["performance_summary"] = performance_summary

            # Add to response
            response_data["stocks"][ticker] = stock_details

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate stock data",
                "details": str(e)
            }
        )
