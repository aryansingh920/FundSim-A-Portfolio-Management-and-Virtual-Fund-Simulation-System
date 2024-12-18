import plotly.graph_objects as go
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.model import HistoricalData, Base


def plot_candlestick_chart(ticker: str):
    # Connect to the database
    engine = create_engine('sqlite:///data/stocks.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query historical data for the specified ticker, sorted by date
    records = session.query(HistoricalData).filter_by(
        ticker=ticker).order_by(HistoricalData.date.asc()).all()

    if not records:
        print(f"No historical data found for ticker {ticker}.")
        return

    # Extract the price data into lists for Plotly
    dates = [r.date for r in records]
    open_prices = [float(r.open_price) for r in records]
    high_prices = [float(r.day_high) for r in records]
    low_prices = [float(r.day_low) for r in records]
    close_prices = [float(r.close_price) for r in records]

    # Create a custom hovertext for each data point
    hover_text = [
        f"Date: {d}<br>Open: {o}<br>High: {h}<br>Low: {l}<br>Close: {c}"
        for d, o, h, l, c in zip(dates, open_prices, high_prices, low_prices, close_prices)
    ]

    # Create the candlestick figure
    fig = go.Figure(data=[go.Candlestick(
        x=dates,
        open=open_prices,
        high=high_prices,
        low=low_prices,
        close=close_prices,
        name=ticker,
        hoverinfo='text',     # Enable text-based hover
        hovertext=hover_text  # Supply the custom hover text
    )])

    # Update layout to add title and better formatting
    fig.update_layout(
        title=f"Candlestick Chart for {ticker}",
        yaxis_title='Price (USD)',
        xaxis_title='Date',
        hovermode='x unified'
    )

    # Add range buttons for 1D, 1W, 1M, 6M, 1Y, All
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1D", step="day", stepmode="backward"),
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=2, label="2Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(count=10, label="10Y", step="year", stepmode="backward"),
                dict(label="All", step="all")
            ])
        ),
        type="date"
    )

    # Show the figure
    fig.show()


if __name__ == "__main__":
    # Example usage: plot candlestick for a given ticker
    plot_candlestick_chart("XTK")
