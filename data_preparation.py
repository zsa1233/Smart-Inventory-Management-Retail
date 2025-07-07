# Import required libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_electronics_inventory_data():
    """
    Generate realistic electronics inventory and sales data for smart inventory management.
    Creates data for 15 electronics products over 1 year with realistic seasonal patterns.
    """
    
    # Define electronics products with realistic categories and characteristics
    electronics_products = [
        {"product_id": "ELEC001", "name": "iPhone 15 Pro", "category": "Smartphones", "base_price": 999.99, "avg_daily_sales": 3, "volatility": 0.4},
        {"product_id": "ELEC002", "name": "Samsung Galaxy S24", "category": "Smartphones", "base_price": 899.99, "avg_daily_sales": 2.5, "volatility": 0.5},
        {"product_id": "ELEC003", "name": "MacBook Air M2", "category": "Laptops", "base_price": 1199.99, "avg_daily_sales": 1.5, "volatility": 0.3},
        {"product_id": "ELEC004", "name": "Dell XPS 13", "category": "Laptops", "base_price": 999.99, "avg_daily_sales": 1.2, "volatility": 0.4},
        {"product_id": "ELEC005", "name": "iPad Air", "category": "Tablets", "base_price": 599.99, "avg_daily_sales": 2.8, "volatility": 0.6},
        {"product_id": "ELEC006", "name": "Samsung Galaxy Tab S9", "category": "Tablets", "base_price": 649.99, "avg_daily_sales": 2.2, "volatility": 0.5},
        {"product_id": "ELEC007", "name": "AirPods Pro", "category": "Audio", "base_price": 249.99, "avg_daily_sales": 4.5, "volatility": 0.7},
        {"product_id": "ELEC008", "name": "Sony WH-1000XM5", "category": "Audio", "base_price": 349.99, "avg_daily_sales": 2.1, "volatility": 0.4},
        {"product_id": "ELEC009", "name": "Apple Watch Series 9", "category": "Wearables", "base_price": 399.99, "avg_daily_sales": 3.2, "volatility": 0.6},
        {"product_id": "ELEC010", "name": "Samsung Galaxy Watch 6", "category": "Wearables", "base_price": 349.99, "avg_daily_sales": 2.8, "volatility": 0.5},
        {"product_id": "ELEC011", "name": "Nintendo Switch OLED", "category": "Gaming", "base_price": 349.99, "avg_daily_sales": 2.5, "volatility": 0.8},
        {"product_id": "ELEC012", "name": "PlayStation 5", "category": "Gaming", "base_price": 499.99, "avg_daily_sales": 1.8, "volatility": 0.9},
        {"product_id": "ELEC013", "name": "Canon EOS R7", "category": "Cameras", "base_price": 1499.99, "avg_daily_sales": 0.8, "volatility": 0.3},
        {"product_id": "ELEC014", "name": "DJI Mini 3 Pro", "category": "Drones", "base_price": 759.99, "avg_daily_sales": 1.2, "volatility": 0.6},
        {"product_id": "ELEC015", "name": "Ring Video Doorbell", "category": "Smart Home", "base_price": 99.99, "avg_daily_sales": 3.5, "volatility": 0.5}
    ]
    
    # Generate date range (1 year of data)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Initialize lists to store data
    all_data = []
    
    for product in electronics_products:
        # Set initial inventory levels
        initial_stock = random.randint(50, 200)
        current_stock = initial_stock
        reorder_threshold = max(10, int(initial_stock * 0.2))  # 20% of initial stock
        
        for date in date_range:
            # Generate realistic daily sales with seasonal patterns
            base_sales = product['avg_daily_sales']
            
            # 1. Weekend effect (higher sales on weekends)
            weekend_multiplier = 1.3 if date.weekday() >= 5 else 1.0
            
            # 2. Monthly seasonality (higher sales at month end/beginning)
            day_of_month = date.day
            if day_of_month <= 5 or day_of_month >= 25:
                month_end_multiplier = 1.2
            else:
                month_end_multiplier = 1.0
            
            # 3. Holiday season effects (November-December)
            holiday_multiplier = 1.0
            if date.month == 11:  # November - Black Friday prep
                holiday_multiplier = 1.4
            elif date.month == 12:  # December - Holiday season
                holiday_multiplier = 1.6
                # Extra boost for Christmas week
                if 20 <= date.day <= 25:
                    holiday_multiplier = 2.0
            
            # 4. Back-to-school season (August-September)
            if date.month in [8, 9]:
                if product['category'] in ['Laptops', 'Tablets', 'Smartphones']:
                    holiday_multiplier = 1.5
            
            # 5. Summer season effects (June-August)
            if date.month in [6, 7, 8]:
                if product['category'] in ['Gaming', 'Audio', 'Wearables']:
                    holiday_multiplier = 1.3  # Summer entertainment boost
            
            # 6. Spring season (March-May) - Graduation gifts
            if date.month in [4, 5]:
                if product['category'] in ['Smartphones', 'Laptops', 'Wearables']:
                    holiday_multiplier = 1.2
            
            # 7. Product-specific seasonal effects
            product_seasonal_multiplier = 1.0
            if product['category'] == 'Gaming':
                # Gaming peaks during holidays and summer
                if date.month in [11, 12, 6, 7, 8]:
                    product_seasonal_multiplier = 1.4
            elif product['category'] == 'Smart Home':
                # Smart home peaks during holidays (gift giving)
                if date.month in [11, 12]:
                    product_seasonal_multiplier = 1.5
            elif product['category'] == 'Cameras':
                # Cameras peak during summer (vacation season)
                if date.month in [6, 7, 8]:
                    product_seasonal_multiplier = 1.3
            elif product['category'] == 'Drones':
                # Drones peak during summer and holidays
                if date.month in [6, 7, 8, 11, 12]:
                    product_seasonal_multiplier = 1.4
            
            # 8. Special event effects
            special_event_multiplier = 1.0
            # Black Friday (day after Thanksgiving - typically last Thursday of November)
            if date.month == 11 and date.weekday() == 4 and 22 <= date.day <= 28:
                special_event_multiplier = 2.5
            # Cyber Monday (Monday after Thanksgiving)
            elif date.month == 11 and date.weekday() == 0 and 25 <= date.day <= 30:
                special_event_multiplier = 2.0
            # Valentine's Day (February 14)
            elif date.month == 2 and date.day == 14:
                if product['category'] in ['Wearables', 'Audio']:
                    special_event_multiplier = 1.8
            # Mother's Day (second Sunday in May)
            elif date.month == 5 and date.weekday() == 6 and 8 <= date.day <= 14:
                if product['category'] in ['Smartphones', 'Tablets', 'Wearables']:
                    special_event_multiplier = 1.6
            # Father's Day (third Sunday in June)
            elif date.month == 6 and date.weekday() == 6 and 15 <= date.day <= 21:
                if product['category'] in ['Gaming', 'Cameras', 'Drones']:
                    special_event_multiplier = 1.6
            
            # 9. Add some randomness
            random_factor = np.random.normal(1, product['volatility'])
            
            # Calculate daily sales with all seasonal effects
            daily_sales = max(0, int(base_sales * weekend_multiplier * month_end_multiplier * 
                                    holiday_multiplier * product_seasonal_multiplier * 
                                    special_event_multiplier * random_factor))
            
            # Update current stock
            current_stock = max(0, current_stock - daily_sales)
            
            # Simulate restocking (when stock gets low)
            if current_stock <= reorder_threshold and random.random() < 0.3:  # 30% chance of restocking
                restock_amount = random.randint(30, 80)
                current_stock += restock_amount
            
            # Add data point
            all_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'product_id': product['product_id'],
                'product_name': product['name'],
                'category': product['category'],
                'units_sold': daily_sales,
                'current_stock': current_stock,
                'reorder_threshold': reorder_threshold,
                'price': product['base_price']
            })
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    return df

def clean_and_preprocess_data(df):
    """
    Clean and preprocess the inventory data.
    """
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Ensure numeric columns are properly typed
    numeric_columns = ['units_sold', 'current_stock', 'reorder_threshold', 'price']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove any rows with missing data
    df = df.dropna()
    
    # Add derived columns for analysis
    df['stock_status'] = df.apply(lambda row: 
        'Low Stock' if row['current_stock'] <= row['reorder_threshold'] else 'In Stock', axis=1)
    
    df['days_until_stockout'] = df.apply(lambda row: 
        int(row['current_stock'] / row['units_sold']) if row['units_sold'] > 0 else 999, axis=1)
    
    # Sort by date and product_id
    df = df.sort_values(['date', 'product_id'])
    
    return df

def main():
    """
    Main function to generate, clean, and save the inventory data.
    """
    print("Generating electronics inventory and sales data...")
    
    # Generate the data
    df = generate_electronics_inventory_data()
    
    print(f"Generated {len(df)} data points for {df['product_id'].nunique()} products")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Clean and preprocess the data
    print("Cleaning and preprocessing data...")
    df_clean = clean_and_preprocess_data(df)
    
    # Save to CSV
    output_file = "electronics_inventory_data.csv"
    df_clean.to_csv(output_file, index=False)
    
    print(f"Data saved to {output_file}")
    
    # Display summary statistics
    print("\n=== DATA SUMMARY ===")
    print(f"Total records: {len(df_clean)}")
    print(f"Number of products: {df_clean['product_id'].nunique()}")
    print(f"Date range: {df_clean['date'].min().strftime('%Y-%m-%d')} to {df_clean['date'].max().strftime('%Y-%m-%d')}")
    print(f"Categories: {', '.join(df_clean['category'].unique())}")
    
    print("\n=== SAMPLE DATA ===")
    print(df_clean.head(10))
    
    print("\n=== STOCK STATUS SUMMARY ===")
    stock_summary = df_clean.groupby('stock_status').size()
    print(stock_summary)
    
    return df_clean

if __name__ == "__main__":
    df = main() 