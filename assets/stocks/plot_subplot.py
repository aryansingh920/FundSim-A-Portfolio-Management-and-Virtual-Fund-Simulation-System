import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.model import HistoricalData
import pandas as pd


def fetch_data(ticker: str, start_date: str, end_date: str):
    # Connect to the database
    engine = create_engine('sqlite:///data/stocks.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query the historical data
    records = session.query(HistoricalData).filter(
        HistoricalData.ticker == ticker,
        HistoricalData.date >= start_date,
        HistoricalData.date <= end_date
    ).order_by(HistoricalData.date.asc()).all()

    if not records:
        print(
            f"No data found for ticker '{ticker}' between {start_date} and {end_date}.")
        return None

    # Convert records to a DataFrame
    data = pd.DataFrame([{col: getattr(
        r, col) for col in HistoricalData.__table__.columns.keys()} for r in records])
    return data


def plot_subplots(ticker: str, start_date: str, end_date: str):
    # Fetch data
    data = fetch_data(ticker, start_date, end_date)
    if data is None:
        return

    # Remove non-numeric columns (e.g., id, ticker, date)
    numeric_data = data.drop(columns=['id', 'ticker', 'date'], errors='ignore')

    # Define the number of rows and columns for subplots
    num_metrics = len(numeric_data.columns)
    rows = (num_metrics // 2) + (num_metrics % 2)
    cols = 2  # Arrange subplots in 2 columns

    # Create a subplot figure
    fig = make_subplots(rows=rows, cols=cols,
                        subplot_titles=numeric_data.columns)

    # Add each metric as a separate line plot in the subplots
    for idx, column in enumerate(numeric_data.columns):
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        fig.add_trace(
            go.Scatter(x=data['date'], y=numeric_data[column],
                       mode='lines', name=column),
            row=row, col=col
        )

    # Update layout
    fig.update_layout(
        title_text=f"Metrics for {ticker} ({start_date} to {end_date})",
        height=300 * rows,  # Adjust height based on number of rows
        showlegend=False
    )

    # Show the plot
    fig.show()


if __name__ == "__main__":
    # Specify your ticker and date range here
    ticker = "BGINTF"                # Replace with desired ticker
    start_date = "2020-01-01"      # Replace with desired start date
    end_date = "2020-12-31"        # Replace with desired end date
    plot_subplots(ticker, start_date, end_date)
