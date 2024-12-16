# Example usage
from save_to_db import setup_database,clear_database,save_random_stock_data
from initialization import generate_random_stock_data
from sqlalchemy.orm import sessionmaker
from model.model import Base, Stock, PriceTradingInfo, FundamentalMetrics, VolatilityRisk, MarketIndicators
from gui import main
if __name__ == "__main__":
    # # Setup the database
    # engine = setup_database()
    # Session = sessionmaker(bind=engine)
    # session = Session()
    
    # clear_database(session)

    # for _ in range(50):  # Generate and save 10 entries
    #     stock_data = generate_random_stock_data()
    #     save_random_stock_data(session, stock_data)

    # # Verify the saved data
    # total_stocks = session.query(Stock).count()
    # print(f"Total stocks in the database: {total_stocks}")
    
    main()
