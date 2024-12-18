# main.py
from datetime import datetime, timedelta
from assets.stocks.model import Base, Stock, PriceTradingInfo, FundamentalMetrics, VolatilityRisk, MarketIndicators, HistoricalData
from assets.stocks.historical_data import generate_historical_data


def create_and_insert_historical_data(session, ticker: str, start_price: float, shares_outstanding: int,
                                      start_date: datetime, days: int,
                                      initial_eps: float = 10.0, annual_dividend: float = 5.0, base_volume: int = 1_000_000):

    # Generate historical data
    historical_data = generate_historical_data(
        ticker=ticker,
        start_price=start_price,
        shares_outstanding=shares_outstanding,
        start_date=start_date,
        days=days,
        initial_eps=initial_eps,
        annual_dividend=annual_dividend,
        base_volume=base_volume
    )

    historical_start = start_date.date()
    historical_end = (start_date + timedelta(days=days-1)).date()

    # Insert HistoricalData
    for day_record in historical_data:
        hd = HistoricalData(
            ticker=day_record['ticker'],
            date=datetime.strptime(day_record['date'], "%Y-%m-%d").date(),
            open_price=day_record['open_price'],
            close_price=day_record['close_price'],
            day_high=day_record['day_high'],
            day_low=day_record['day_low'],
            week_52_high=day_record['week_52_high'],
            week_52_low=day_record['week_52_low'],
            trading_volume=day_record['trading_volume'],
            average_volume=day_record['average_volume'],
            eps=day_record['eps'],
            p_e_ratio=day_record['p_e_ratio'],
            dividend_yield=day_record['dividend_yield'],
            roe=day_record['roe'],
            debt_to_equity=day_record['debt_to_equity'],
            revenue_growth=day_record['revenue_growth'],
            net_income=day_record['net_income'],
            beta=day_record['beta'],
            standard_deviation=day_record['standard_deviation'],
            sharpe_ratio=day_record['sharpe_ratio'],
            RSI=day_record['RSI'],
            moving_avg_50=day_record['moving_avg_50'],
            moving_avg_200=day_record['moving_avg_200'],
            MACD=day_record['MACD'],
            analyst_rating=day_record['analyst_rating'],
            historical_data_start_date=historical_start,
            historical_data_end_date=historical_end
        )
        session.add(hd)

    # Commit HistoricalData first
    session.commit()

    # Fetch the stock and update with the final day's metrics
    stock = session.query(Stock).filter_by(ticker=ticker).first()
    last_day = historical_data[-1]

    # Update Stock
    stock.market_cap = last_day['market_cap']
    stock.cap_category = last_day['cap_category']
    stock.historical_data_start_date = historical_start
    stock.historical_data_end_date = historical_end

    # Update PriceTradingInfo
    price_info = session.query(
        PriceTradingInfo).filter_by(ticker=ticker).first()
    if not price_info:
        price_info = PriceTradingInfo(ticker=ticker)
        session.add(price_info)

    price_info.current_price = last_day['close_price']
    price_info.open_price = last_day['open_price']
    price_info.close_price = last_day['close_price']
    price_info.day_high = last_day['day_high']
    price_info.day_low = last_day['day_low']
    price_info.week_52_high = last_day['week_52_high']
    price_info.week_52_low = last_day['week_52_low']
    price_info.trading_volume = last_day['trading_volume']
    price_info.average_volume = last_day['average_volume']
    price_info.historical_data_start_date = historical_start
    price_info.historical_data_end_date = historical_end

    # Update MarketIndicators
    market_indicators = session.query(
        MarketIndicators).filter_by(ticker=ticker).first()
    if not market_indicators:
        market_indicators = MarketIndicators(ticker=ticker)
        session.add(market_indicators)

    market_indicators.RSI = last_day['RSI']
    market_indicators.moving_avg_50 = last_day['moving_avg_50']
    market_indicators.moving_avg_200 = last_day['moving_avg_200']
    market_indicators.MACD = last_day['MACD']
    market_indicators.analyst_rating = last_day['analyst_rating']
    market_indicators.historical_data_start_date = historical_start
    market_indicators.historical_data_end_date = historical_end

    # Update VolatilityRisk
    volatility_risk = session.query(
        VolatilityRisk).filter_by(ticker=ticker).first()
    if not volatility_risk:
        volatility_risk = VolatilityRisk(ticker=ticker)
        session.add(volatility_risk)

    volatility_risk.beta = last_day['beta']
    volatility_risk.standard_deviation = last_day['standard_deviation']
    volatility_risk.sharpe_ratio = last_day['sharpe_ratio']
    volatility_risk.historical_data_start_date = historical_start
    volatility_risk.historical_data_end_date = historical_end

    # Update FundamentalMetrics
    fundamentals = session.query(
        FundamentalMetrics).filter_by(ticker=ticker).first()
    if not fundamentals:
        fundamentals = FundamentalMetrics(ticker=ticker)
        session.add(fundamentals)

    fundamentals.earnings_per_share = last_day['eps']
    fundamentals.price_to_earnings = last_day['p_e_ratio'] if last_day['p_e_ratio'] else None
    fundamentals.dividend_yield = last_day['dividend_yield']
    fundamentals.return_on_equity = last_day['roe']
    fundamentals.debt_to_equity = last_day['debt_to_equity']
    fundamentals.revenue_growth = last_day['revenue_growth']
    fundamentals.net_income = last_day['net_income']
    fundamentals.historical_data_start_date = historical_start
    fundamentals.historical_data_end_date = historical_end

    session.commit()
    print(
        f"Historical data generated and all related tables updated successfully for {ticker}!")
