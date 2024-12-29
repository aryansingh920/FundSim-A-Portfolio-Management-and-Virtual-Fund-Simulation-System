import plotly.graph_objects as go
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
from assets.stocks.model import HistoricalData, IntradayData


def generate_candlestick_chart(ticker: str):
    # Connect to the database
    engine = create_engine('sqlite:///data/stocks.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1) Query all daily data
    daily_records = session.query(HistoricalData).filter_by(
        ticker=ticker).order_by(HistoricalData.date.asc()).all()

    if not daily_records:
        print(f"No historical data found for ticker {ticker}.")
        return

    # Extract daily data
    daily_dates = [rec.date for rec in daily_records]
    daily_open = [float(rec.open_price) for rec in daily_records]
    daily_high = [float(rec.day_high) for rec in daily_records]
    daily_low = [float(rec.day_low) for rec in daily_records]
    daily_close = [float(rec.close_price) for rec in daily_records]

    # 2) Identify the last day and query intraday data
    last_date = max(daily_dates)
    intraday_records = session.query(IntradayData).filter_by(
        ticker=ticker, date=last_date).order_by(IntradayData.timestamp.asc()).all()

    # Extract intraday data
    intraday_timestamps = []
    intraday_prices = []

    if intraday_records:
        intraday_timestamps = [row.timestamp for row in intraday_records]
        intraday_prices = [float(row.price) for row in intraday_records]

    # 3) Calculate global min and max for scaling
    daily_min = min(daily_low)
    daily_max = max(daily_high)
    intraday_min = min(intraday_prices) if intraday_prices else daily_min
    intraday_max = max(intraday_prices) if intraday_prices else daily_max

    # Combine to get overall min and max
    overall_min = min(daily_min, intraday_min)
    overall_max = max(daily_max, intraday_max)

    # 4) Create the figure
    fig = go.Figure()

    # Add daily candlestick trace
    fig.add_trace(go.Candlestick(
        x=daily_dates,
        open=daily_open,
        high=daily_high,
        low=daily_low,
        close=daily_close,
        name=f"{ticker} (Daily)"
    ))

    # Add intraday line trace (or candlestick if pre-aggregated)
    if intraday_records:
        fig.add_trace(go.Scatter(
            x=intraday_timestamps,
            y=intraday_prices,
            mode='lines',
            name=f"{ticker} (Intraday)"
        ))

    # 5) Update layout with range selector and dynamic scaling
    fig.update_layout(
        title=f"{ticker} - Daily & Intraday",
        yaxis=dict(
            title='Price (USD)',
            range=[overall_min * 0.95, overall_max * 1.05]  # Add a 5% padding
        ),
        xaxis=dict(
            title='Date/Time',
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(label="All", step="all")
                ])
            ),
            type="date"
        ),
        hovermode='x unified'
    )

    # 6) Show the figure
    fig.show()
