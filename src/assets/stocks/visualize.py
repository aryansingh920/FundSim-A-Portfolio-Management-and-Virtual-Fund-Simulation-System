import plotly.graph_objects as go
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from assets.stocks.model import HistoricalData, Base


def generate_candlestick_chart(ticker: str):
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

    # Extract all columns dynamically
    dates = [r.date for r in records]
    open_prices = [float(r.open_price) for r in records]
    high_prices = [float(r.day_high) for r in records]
    low_prices = [float(r.day_low) for r in records]
    close_prices = [float(r.close_price) for r in records]

    # Get all attributes dynamically
    extra_fields = [col for col in HistoricalData.__table__.columns.keys(
    ) if col not in ['date', 'open_price', 'day_high', 'day_low', 'close_price', 'ticker']]

    # Prepare custom hover text dynamically for all fields
    hover_text = []
    for record in records:
        hover_items = [
            f"Date: {record.date}",
            f"Open: {record.open_price}",
            f"High: {record.day_high}",
            f"Low: {record.day_low}",
            f"Close: {record.close_price}"
        ]
        # Add all extra fields dynamically
        # for field in extra_fields:
        #     # Fetch attribute or fallback to "N/A"
        #     if field == "id" or field == "ticker" or field == "historical_data_start_date" or field == "historical_data_end_date":
        #         continue
        #     value = getattr(record, field, "N/A")
        #     hover_items.append(f"{field.replace('_', ' ').title()}: {value}")

        hover_text.append("<br>".join(hover_items))

    # Create the candlestick figure
    fig = go.Figure(data=[go.Candlestick(
        x=dates,
        open=open_prices,
        high=high_prices,
        low=low_prices,
        close=close_prices,
        name=ticker,
        hoverinfo='text',     # Enable text-based hover
        hovertext=hover_text  # Supply the dynamic hover text
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
    generate_candlestick_chart("BGINTF")
