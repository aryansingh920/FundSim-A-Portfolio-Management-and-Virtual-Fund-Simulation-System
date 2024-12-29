import plotly.graph_objects as go
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from assets.stocks.model import HistoricalData, IntradayData, Base


def generate_candlestick_chart(ticker: str):
    # Connect to the database
    engine = create_engine('sqlite:///data/stocks.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1) Query all daily data
    daily_records = (session.query(HistoricalData)
                     .filter_by(ticker=ticker)
                     .order_by(HistoricalData.date.asc())
                     .all())

    if not daily_records:
        print(f"No historical data found for ticker {ticker}.")
        return

    # Extract daily data
    daily_dates = [rec.date for rec in daily_records]
    daily_open = [float(rec.open_price) for rec in daily_records]
    daily_high = [float(rec.day_high) for rec in daily_records]
    daily_low = [float(rec.day_low) for rec in daily_records]
    daily_close = [float(rec.close_price) for rec in daily_records]

    # 2) Identify last day from daily data
    last_date = max(daily_dates)

    # 3) Query intraday data for that last day
    intraday_records = (session.query(IntradayData)
                        .filter_by(ticker=ticker)
                        .filter(IntradayData.date == last_date)
                        .order_by(IntradayData.timestamp.asc())
                        .all())

    # Extract intraday data if available
    intraday_timestamps = []
    intraday_open = []
    intraday_high = []
    intraday_low = []
    intraday_close = []

    if intraday_records:
        # For candlesticks, we typically group intraday data by (time intervals)
        # If you have each minute (or each record individually):
        #   - you either plot them as a single "line" or
        #   - you aggregate them into intervals (e.g. 15-min, 30-min candles)
        # For simplicity, let's pretend each row is already the needed interval:
        intraday_timestamps = [row.timestamp for row in intraday_records]
        # If your table does not store open/high/low/close for intraday,
        #   you can replicate them from `row.price` or some aggregator function.
        # Let's assume we only have `row.price` in IntradayData for simplicity:
        # In that case, a candlestick might not make sense unless you’re
        # computing open/high/low/close per interval.
        # So let's do a *line chart* for intraday to keep it simpler.

        # However, to show you how to do a candlestick, we’ll *pretend*
        # we have O/H/L/C columns. If not, adapt accordingly.
        intraday_open = [float(row.price) for row in intraday_records]
        intraday_high = [float(row.price) for row in intraday_records]
        intraday_low = [float(row.price) for row in intraday_records]
        intraday_close = [float(row.price) for row in intraday_records]

    # 4) Create the figure
    fig = go.Figure()

    # --- Add daily candlestick trace ---
    fig.add_trace(go.Candlestick(
        x=daily_dates,
        open=daily_open,
        high=daily_high,
        low=daily_low,
        close=daily_close,
        name=f"{ticker} (Daily)"
    ))

    # --- Add intraday candlestick or line trace (if intraday data exists) ---
    if intraday_records:
        # Using Candlestick (pretending we have O/H/L/C):
        fig.add_trace(go.Candlestick(
            x=intraday_timestamps,
            open=intraday_open,
            high=intraday_high,
            low=intraday_low,
            close=intraday_close,
            name=f"{ticker} (Intraday)",
            increasing_line_color='blue',
            decreasing_line_color='red',
            showlegend=True
        ))
        # If you only have a single price per record, you can use:
        # fig.add_trace(go.Scatter(
        #     x=intraday_timestamps,
        #     y=[float(r.price) for r in intraday_records],
        #     mode='lines+markers',
        #     name=f"{ticker} (Intraday)"
        # ))

    # 5) Add the range selector with the 1D button (and others)
    fig.update_layout(
        title=f"{ticker} - Daily & Intraday",
        yaxis_title='Price (USD)',
        xaxis_title='Date/Time',
        hovermode='x unified',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=2, label="2Y", step="year", stepmode="backward"),
                    dict(label="All", step="all")
                ])
            ),
            type="date"
        )
    )

    fig.show()
