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

    # Query daily data
    daily_records = session.query(HistoricalData).filter_by(
        ticker=ticker
    ).order_by(HistoricalData.date.asc()).all()

    if not daily_records:
        print(f"No historical data found for ticker {ticker}.")
        return

    daily_dates = [rec.date for rec in daily_records]
    daily_open = [float(rec.open_price) for rec in daily_records]
    daily_high = [float(rec.day_high) for rec in daily_records]
    daily_low = [float(rec.day_low) for rec in daily_records]
    daily_close = [float(rec.close_price) for rec in daily_records]

    # Query intraday data (for the last date, e.g.)
    last_date = max(daily_dates)
    intraday_records = (
        session.query(IntradayData)
        .filter_by(ticker=ticker, date=last_date)
        .order_by(IntradayData.timestamp.asc())
        .all()
    )

    intraday_timestamps = []
    intraday_prices = []
    if intraday_records:
        intraday_timestamps = [row.timestamp for row in intraday_records]
        intraday_prices = [float(row.price) for row in intraday_records]

    session.close()

    # Build figure
    fig = go.Figure()

    # 0) Daily Candlestick
    fig.add_trace(
        go.Candlestick(
            x=daily_dates,
            open=daily_open,
            high=daily_high,
            low=daily_low,
            close=daily_close,
            name=f"{ticker} (Daily Candle)",
            visible=True  # We'll let "Daily vs Intraday" toggle handle showing/hiding
        )
    )

    # 1) Daily Line
    fig.add_trace(
        go.Scatter(
            x=daily_dates,
            y=daily_close,
            mode='lines',
            name=f"{ticker} (Daily Line)",
            visible=False
        )
    )

    # 2) Intraday Candlestick
    fig.add_trace(
        go.Candlestick(
            x=intraday_timestamps,
            open=intraday_prices,
            high=intraday_prices,
            low=intraday_prices,
            close=intraday_prices,
            name=f"{ticker} (Intraday Candle)",
            visible=False
        )
    )

    # 3) Intraday Line
    fig.add_trace(
        go.Scatter(
            x=intraday_timestamps,
            y=intraday_prices,
            mode='lines',
            name=f"{ticker} (Intraday Line)",
            visible=False
        )
    )

    # Basic layout
    fig.update_layout(
        title=f"{ticker} - Daily & Intraday",
        xaxis=dict(
            title='Date/Time',
            type='date',
            rangeslider=dict(visible=True),  # The bottom drag range
            rangeselector=dict(
                # THIS range selector only picks date ranges.
                # We CANNOT hide/show traces from these buttons.
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
        ),
        yaxis=dict(title='Price (USD)', autorange=True),
        hovermode='x unified'
    )

    # Updatemenus:
    #
    # Menu 1: Toggle between Candlestick or Line (for both daily & intraday).
    # We have 4 total traces:
    #  [0] daily candle, [1] daily line, [2] intraday candle, [3] intraday line
    #
    # "Candlestick" => daily candle = ON if daily is ON, daily line OFF
    #                  intraday candle = ON if intraday is ON, intraday line OFF
    #
    # "Line" => daily candle = OFF if daily is ON, daily line ON
    #            intraday candle = OFF if intraday is ON, intraday line ON
    #
    # So we won't attempt to show/hide daily vs intraday here, only "how" to draw them.

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                x=0.37,
                y=1.09,
                xanchor="left",
                yanchor="top",
                direction="left",
                buttons=[
                    dict(
                        label="Candlestick",
                        method="update",
                        args=[
                            {
                                # If daily is currently visible,
                                # keep daily candle ON (trace0),
                                # daily line OFF (trace1).
                                # If intraday is visible,
                                # keep intraday candle ON (trace2),
                                # intraday line OFF (trace3).
                                #
                                # However, we can't know from here which is "Daily vs Intraday."
                                # We can simply do:
                                #   "candlestick" => [True, False, True, False]
                                # but that *always* shows both daily & intraday.
                                # So instead we "mirror" the current on/off states:
                                #
                                # Easiest is to forcibly do daily candle = same as daily line was + daily candle was
                                # but in pure static Plotly there's no "state memory."
                                #
                                # => So let's do the simpler approach:
                                #    * Daily candle replaces daily line if daily was used
                                #    * Intraday candle replaces intraday line if intraday was used
                                #
                                # We'll just always assume daily is on by default.
                                # For a real production approach, you'd do a bigger system of 8 buttons or a dynamic callback.

                                "visible": [
                                    True,  # daily candle
                                    False,  # daily line
                                    True,  # intraday candle
                                    False  # intraday line
                                ]
                            },
                            {"yaxis.autorange": True},
                        ],
                    ),
                    dict(
                        label="Line",
                        method="update",
                        args=[
                            {
                                "visible": [
                                    False,  # daily candle
                                    True,  # daily line
                                    False,  # intraday candle
                                    True   # intraday line
                                ]
                            },
                            {"yaxis.autorange": True},
                        ],
                    ),
                ],
            ),

            # Menu 2: Toggle between "Daily" vs. "Intraday"
            # We'll forcibly hide intraday if user picks "Daily"
            # and forcibly hide daily if user picks "Intraday"
            dict(
                type="buttons",
                x=0.20,
                y=1.09,
                xanchor="left",
                yanchor="top",
                direction="left",
                buttons=[
                    dict(
                        label="Show Daily",
                        method="update",
                        args=[
                            {
                                # Keep daily traces on
                                # (but which daily is actually on depends on the first toggle).
                                # Hide intraday traces.
                                # So we set daily candle = True, daily line = True
                                # intraday candle = False, intraday line = False
                                "visible": [True, True, False, False]
                            },
                            {"yaxis.autorange": True},
                        ],
                    ),
                    dict(
                        label="Show Intraday",
                        method="update",
                        args=[
                            {
                                # Hide daily traces, show intraday traces
                                "visible": [False, False, True, True]
                            },
                            {"yaxis.autorange": True},
                        ],
                    ),
                ],
            ),
        ]
    )

    fig.show()
