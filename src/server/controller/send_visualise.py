from flask import jsonify
from assets.stocks.visualize import generate_candlestick_chart
import plotly.io as pio

# Route Handler Function


def get_candlestick_chart(ticker: str):
    if not ticker:
        return jsonify({"error": "Missing ticker parameter"}), 400

    # Generate the chart
    fig = generate_candlestick_chart(ticker)
    if not fig:
        return jsonify({"error": f"No data found for ticker {ticker}"}), 404

    # Convert the figure to HTML
    chart_html = pio.to_html(fig, full_html=False)
    return chart_html
