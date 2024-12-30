"""
Created on 30/12/2024

@author: Aryan

Filename: visualize.py

Relative Path: src/assets/stocks/visualize.py
"""

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
        ticker=ticker
    ).order_by(HistoricalData.date.asc()).all()

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
        ticker=ticker, date=last_date
    ).order_by(IntradayData.timestamp.asc()).all()

    # Extract intraday data
    intraday_timestamps = []
    intraday_prices = []
    if intraday_records:
        intraday_timestamps = [row.timestamp for row in intraday_records]
        intraday_prices = [float(row.price) for row in intraday_records]

    # 3) Create the figure
    fig = go.Figure()

    # ---- Daily Candlestick Trace ----
    fig.add_trace(
        go.Candlestick(
            x=daily_dates,
            open=daily_open,
            high=daily_high,
            low=daily_low,
            close=daily_close,
            name=f"{ticker} (Daily Candlestick)",
            visible=True  # Default: Candlestick is visible
        )
    )

    # ---- Daily Line Trace (hidden by default) ----
    fig.add_trace(
        go.Scatter(
            x=daily_dates,
            y=daily_close,
            mode='lines',
            name=f"{ticker} (Daily Line)",
            visible=False  # Default: hidden, toggled by updatemenu
        )
    )

    # ---- Intraday Line Trace (always plotted, but effectively only seen in 1D range) ----
    if intraday_records:
        fig.add_trace(
            go.Scatter(
                x=intraday_timestamps,
                y=intraday_prices,
                mode='lines',
                name=f"{ticker} (Intraday)",
                # Intraday is "visible",
                # but only becomes relevant if the user zooms to the last day.
                visible=True
            )
        )

    # 4) Let Plotly handle dynamic scaling (remove fixed y-range)
    #    So that each range uses auto-range for min/max.

    # 5) Configure range selector buttons
    #    - 1D: step="day", stepmode="backward"
    #    - 1W, 1M, 6M, 1Y, 5Y, All: same as your original logic
    #    Intraday data is only meaningful if the user zooms into the last day.
    fig.update_layout(
        title=f"{ticker} - Daily & Intraday",
        yaxis=dict(
            title='Price (USD)',
            autorange=True
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

    # 6) Add a button menu to switch between Candlestick and Line for Daily data
    #    Index of traces:
    #    0 -> Daily Candlestick
    #    1 -> Daily Line
    #    2 -> Intraday (if present; only exists if intraday_records)
    #    If no intraday_records, we only have 2 traces total
    intraday_visible = True if intraday_records else False

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Candlestick",
                        method="update",
                        args=[{
                            "visible": [True, False, True]
                        }]
                    ),
                    dict(
                        label="Line",
                        method="update",
                        args=[{
                            "visible": [False, True, True]
                        }]
                    ),
                ]
            )
        ]
    )

    # fig.update_layout(
    #     updatemenus=[
    #         dict(
    #             type="buttons",
    #             direction="left",
    #             buttons=[
    #                 dict(
    #                     label="Candlestick",
    #                     method="update",
    #                     args=[
    #                         {
    #                             # If intraday data exists: [candlestick=True, line=False, intraday=intraday_visible]
    #                             "visible": [True, False, intraday_visible] if intraday_visible else [True, False],
    #                         }
    #                     ],
    #                 ),
    #                 dict(
    #                     label="Line",
    #                     method="update",
    #                     args=[
    #                         {
    #                             # If intraday data exists: [candlestick=False, line=True, intraday=intraday_visible]
    #                             "visible": [False, True, intraday_visible] if intraday_visible else [False, True],
    #                         }
    #                     ],
    #                 ),
    #             ],
    #             pad={"r": 10, "t": 10},
    #             showactive=True,
    #             x=0.0,
    #             y=1.05,
    #             xanchor="left",
    #             yanchor="top"
    #         )
    #     ]
    # )

    # 7) Show the figure
    fig.show()
