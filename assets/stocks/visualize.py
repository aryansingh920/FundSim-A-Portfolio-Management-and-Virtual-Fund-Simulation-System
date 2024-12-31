import plotly.graph_objects as go
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from assets.stocks.model import HistoricalData, IntradayData


def generate_candlestick_chart(ticker: str):
    # 1) Connect to DB
    engine = create_engine('sqlite:///data/stocks.db', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 2) Fetch daily data
    daily_records = (
        session.query(HistoricalData)
        .filter_by(ticker=ticker)
        .order_by(HistoricalData.date.asc())
        .all()
    )
    if not daily_records:
        print(f"No historical data found for ticker {ticker}.")
        session.close()
        return

    daily_dates = [rec.date for rec in daily_records]
    daily_open = [float(rec.open_price) for rec in daily_records]
    daily_high = [float(rec.day_high) for rec in daily_records]
    daily_low = [float(rec.day_low) for rec in daily_records]
    daily_close = [float(rec.close_price) for rec in daily_records]

    # 3) Fetch *all distinct* dates for intraday data for this ticker
    distinct_intraday_dates = (
        session.query(IntradayData.date)
        .filter_by(ticker=ticker)
        .distinct()
        .order_by(IntradayData.date.asc())
        .all()
    )
    # Convert list of tuples to a flat list of dates
    distinct_intraday_dates = [row[0] for row in distinct_intraday_dates]

    # We'll store intraday traces in lists:
    intraday_traces = []

    # 4) Start building the figure
    fig = go.Figure()

    # ---- [0] Daily Candlestick ----
    fig.add_trace(
        go.Candlestick(
            x=daily_dates,
            open=daily_open,
            high=daily_high,
            low=daily_low,
            close=daily_close,
            name="Daily Candlestick",
            visible=True  # default: daily is shown
        )
    )

    # ---- [1] Daily Line ----
    fig.add_trace(
        go.Scatter(
            x=daily_dates,
            y=daily_close,
            mode='lines',
            name="Daily Line",
            visible=False  # hidden initially (we start with candlestick)
        )
    )

    # 5) For each distinct intraday date, build 2 new traces: candle & line
    for date in distinct_intraday_dates:
        # Query all intraday data for that date
        records = (
            session.query(IntradayData)
            .filter_by(ticker=ticker, date=date)
            .order_by(IntradayData.timestamp.asc())
            .all()
        )
        if not records:
            continue

        x_vals = [r.timestamp for r in records]
        y_vals = [float(r.price) for r in records]

        # (a) Intraday candlestick (same open/high/low/close values per point)
        fig.add_trace(
            go.Candlestick(
                x=x_vals,
                open=y_vals,
                high=y_vals,
                low=y_vals,
                close=y_vals,
                name=f"Intraday {date}",
                visible=False,
                hoverinfo="skip"  # Removes unnecessary labels
            )
        )
        candle_idx = len(fig.data) - 1

        # (b) Intraday line
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name=f"Intraday Line {date}",
                visible=False,
                hoverinfo="skip"  # Removes unnecessary labels
            )
        )
        line_idx = len(fig.data) - 1

        intraday_traces.append((date, candle_idx, line_idx))

    session.close()

    # 6) Dropdown Logic
    n_traces = len(fig.data)

    # Default visibility for "Show Daily"
    show_daily = [False] * n_traces
    show_daily[0] = True  # Daily Candlestick ON
    show_daily[1] = True  # Daily Line OFF (initial toggle)

    # Dropdown options
    dropdown_buttons = [
        dict(
            label="Show Daily",
            method="update",
            args=[
                {"visible": show_daily},
                {"yaxis.autorange": True}
            ]
        )
    ]

    for date, candle_idx, line_idx in intraday_traces:
        visibility = [False] * n_traces
        # Show intraday candlestick for this date
        visibility[candle_idx] = True
        visibility[line_idx] = True  # Show intraday line for this date

        dropdown_buttons.append(
            dict(
                label=f"Intraday {date}",
                method="update",
                args=[
                    {"visible": visibility},
                    {"yaxis.autorange": True}
                ]
            )
        )

    # 7) Chart Type Toggle
    candlestick_visibility = [False] * n_traces
    line_visibility = [False] * n_traces

    # Set visibility for daily and intraday candlesticks
    candlestick_visibility[0] = True
    for _, candle_idx, _ in intraday_traces:
        candlestick_visibility[candle_idx] = True

    # Set visibility for daily and intraday lines
    line_visibility[1] = True
    for _, _, line_idx in intraday_traces:
        line_visibility[line_idx] = True

    chart_type_buttons = [
        dict(
            label="Candlestick",
            method="update",
            args=[
                {"visible": candlestick_visibility},
                {"yaxis.autorange": True}
            ]
        ),
        dict(
            label="Line",
            method="update",
            args=[
                {"visible": line_visibility},
                {"yaxis.autorange": True}
            ]
        ),
    ]

    # 8) Update layout with updatemenus
    fig.update_layout(
        updatemenus=[
            # Dropdown for Daily/Intraday
            dict(
                type="dropdown",
                buttons=dropdown_buttons,
                x=0.0,
                y=1.15,
                xanchor="right",
                yanchor="top",
            ),
            # Buttons for Chart Type
            dict(
                type="buttons",
                buttons=chart_type_buttons,
                x=0.0,
                y=1.08,
                xanchor="right",
                yanchor="top",
                direction="left"
            )
        ],
        title=f"{ticker} - Daily & Intraday",
        xaxis=dict(
            title='Date/Time',
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(label="All", step="all")
                ])
            ),
        ),
        yaxis=dict(title="Price (USD)", autorange=True),
        hovermode="x unified"
    )

    # Show the figure
    fig.show()
