# main.py
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from assets.stocks.model import Base, HistoricalData
from assets.stocks.initialization import generate_random_stock_data
from assets.stocks.create_historical_data import create_and_insert_historical_data


def main(number_of_stocks: int = 1, start_date: datetime = datetime(2020, 1, 1), days: int = 365*1):
    # Dictionary to store all generated stock data
    all_stock_data = {}

    for _ in range(number_of_stocks):
        # Setup the database connection
        engine = create_engine('sqlite:///data/stocks.db', echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Generate a single new random stock and insert it into the database
        stock, price_info, fundamentals, risk_metrics, market_indicators = generate_random_stock_data()

        session.add(stock)
        session.add(price_info)
        session.add(fundamentals)
        session.add(risk_metrics)
        session.add(market_indicators)
        session.commit()

        # Now automatically generate historical data for this new stock
        ticker = stock.ticker
        start_price = float(price_info.close_price)
        shares_outstanding = stock.shares_outstanding
        initial_eps = float(
            fundamentals.earnings_per_share) if fundamentals.earnings_per_share else 10.0
        annual_dividend = float(
            fundamentals.dividend_yield) if fundamentals.dividend_yield else 5.0

        # Generate and insert historical data
        create_and_insert_historical_data(session, ticker, start_price, shares_outstanding,
                                          start_date, days, initial_eps, annual_dividend)

        # Collect all data for the current stock
        stock_data = {
            "stock_info": {
                "ticker": stock.ticker,
                "company_name": stock.company_name,
                "sector": stock.sector,
                # "industry": stock.industry,
                "shares_outstanding": stock.shares_outstanding,
                "market_cap": stock.market_cap,
                "cap_category": stock.cap_category,
                "historical_data_start_date": stock.historical_data_start_date,
                "historical_data_end_date": stock.historical_data_end_date
            },
            "price_trading_info": {
                "current_price": price_info.current_price,
                "open_price": price_info.open_price,
                "close_price": price_info.close_price,
                "day_high": price_info.day_high,
                "day_low": price_info.day_low,
                "week_52_high": price_info.week_52_high,
                "week_52_low": price_info.week_52_low,
                "trading_volume": price_info.trading_volume,
                "average_volume": price_info.average_volume
            },
            "fundamental_metrics": {
                "earnings_per_share": fundamentals.earnings_per_share,
                "price_to_earnings": fundamentals.price_to_earnings,
                "dividend_yield": fundamentals.dividend_yield,
                "return_on_equity": fundamentals.return_on_equity,
                "debt_to_equity": fundamentals.debt_to_equity,
                "revenue_growth": fundamentals.revenue_growth,
                "net_income": fundamentals.net_income
            },
            "volatility_risk": {
                "beta": risk_metrics.beta,
                "standard_deviation": risk_metrics.standard_deviation,
                "sharpe_ratio": risk_metrics.sharpe_ratio
            },
            "market_indicators": {
                "RSI": market_indicators.RSI,
                "moving_avg_50": market_indicators.moving_avg_50,
                "moving_avg_200": market_indicators.moving_avg_200,
                "MACD": market_indicators.MACD,
                "analyst_rating": market_indicators.analyst_rating
            }
        }

        # Fetch historical data
        historical_records = session.query(
            HistoricalData).filter_by(ticker=ticker).all()
        stock_data["historical_data"] = [
            {
                "date": record.date,
                "open_price": record.open_price,
                "close_price": record.close_price,
                "day_high": record.day_high,
                "day_low": record.day_low,
                "trading_volume": record.trading_volume,
                "eps": record.eps,
                "p_e_ratio": record.p_e_ratio,
                "beta": record.beta
            } for record in historical_records
        ]

        # Add to the comprehensive dictionary
        all_stock_data[ticker] = stock_data

    # Print total number of stocks
    print(f"Total stocks generated: {len(all_stock_data)}")

    return all_stock_data


# Optional: If you want to use it with a main block
if __name__ == "__main__":
    # Generate 3 stocks and get their data
    stock_data = main(number_of_stocks=3)

    # Example of accessing the data
    for ticker, data in stock_data.items():
        print(f"\nStock: {ticker}")
        print(f"Company Name: {data['stock_info']['company_name']}")
        print(f"Current Price: ${data['price_trading_info']['current_price']}")
        print(
            f"Number of Historical Data Points: {len(data['historical_data'])}")

# if __name__ == "__main__":
#     for _ in range(1):
#         main()  # Call the main function when the script is run directly
