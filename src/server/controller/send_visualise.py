from flask import jsonify
from assets.stocks.visualize import generate_candlestick_chart
from assets.stocks.plot_subplot import plot_subplots
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


def get_subplot_chart(ticker: str, start_date: str, end_date: str):
    if not ticker:
        return jsonify({"error": "Missing ticker parameter"}), 400

    # Generate the chart
    fig = plot_subplots(ticker, start_date, end_date)
    if not fig:
        return jsonify({"error": f"No data found for ticker {ticker}"}), 404

    # Convert the figure to HTML
    chart_html = pio.to_html(fig, full_html=False)
    return chart_html
