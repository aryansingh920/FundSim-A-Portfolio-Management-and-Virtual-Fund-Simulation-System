"""
Created on 07/01/2025

@author: Aryan

Filename: generate_bond.py

Relative Path: src/server/controller/generate_bond.py
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException
# Import the main bond data generation function
from assets.bonds.main import main


def bond_data_controller(
    number_of_bonds: int = 3,
    days: int = 365
) -> Dict[str, Any]:
    """
    Controller function to generate bond data for FastAPI

    :param number_of_bonds: Number of bonds to generate
    :param days: Number of days of historical data to generate
    :return: Dictionary with bond data
    """
    try:
        # Generate bond data
        all_bond_data = main(number_of_bonds, days)

        # Prepare response dictionary
        response_data = {
            "total_bonds": len(all_bond_data),
            "bonds": {}
        }

        # Process each bond
        for isin, bond_info in all_bond_data.items():
            # Prepare bond details
            bond_details = {
                "basic_info": bond_info["bond_info"],
                "historical_data": bond_info["historical_data"],
                "coupon_payments": bond_info["coupon_payments"],
                "risk_metrics": bond_info["risk_metrics"],
                "bond_rating": bond_info["bond_rating"]
            }

            # Add performance summary
            historical_data = bond_info["historical_data"]
            performance_summary = {
                "total_return_percent": round(
                    (historical_data[-1]["close_price"] /
                     historical_data[0]["close_price"] - 1) * 100, 2
                ) if len(historical_data) > 1 else 0.0,
                "start_price": historical_data[0]["close_price"] if historical_data else None,
                "end_price": historical_data[-1]["close_price"] if historical_data else None,
                "highest_price": max(day["close_price"] for day in historical_data) if historical_data else None,
                "lowest_price": min(day["close_price"] for day in historical_data) if historical_data else None
            }
            bond_details["performance_summary"] = performance_summary

            # Add to response
            response_data["bonds"][isin] = bond_details

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate bond data",
                "details": str(e)
            }
        )
