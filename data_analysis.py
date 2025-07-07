# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def analyze_inventory_data():
    """
    Analyze the generated electronics inventory data to verify quality and show insights.
    """
    
    # Load the data
    print("Loading electronics inventory data...")
    df = pd.read_csv("electronics_inventory_data.csv")
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"Data loaded successfully!")
    print(f"Shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Number of products: {df['product_id'].nunique()}")
    
    # Basic data quality checks
    print("\n=== DATA QUALITY CHECKS ===")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    
    # Verify required columns exist
    required_columns = ['date', 'product_id', 'units_sold', 'current_stock', 'reorder_threshold']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"WARNING: Missing required columns: {missing_columns}")
    else:
        print("✓ All required columns present")
    
    # Data summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    print(df[['units_sold', 'current_stock', 'reorder_threshold', 'price']].describe())
    
    # Product category analysis
    print("\n=== PRODUCT CATEGORY ANALYSIS ===")
    category_summary = df.groupby('category').agg({
        'product_id': 'nunique',
        'units_sold': 'sum',
        'current_stock': 'mean',
        'price': 'mean'
    }).round(2)
    category_summary.columns = ['Product Count', 'Total Units Sold', 'Avg Current Stock', 'Avg Price']
    print(category_summary)
    
    # Stock status analysis
    print("\n=== STOCK STATUS ANALYSIS ===")
    stock_status_summary = df.groupby('stock_status').size()
    print(stock_status_summary)
    
    # Low stock alerts analysis
    low_stock_data = df[df['stock_status'] == 'Low Stock']
    if len(low_stock_data) > 0:
        print(f"\nLow stock events: {len(low_stock_data)}")
        print("Products with most low stock events:")
        low_stock_counts = low_stock_data.groupby(['product_id', 'product_name']).size().sort_values(ascending=False)
        print(low_stock_counts.head(5))
    
    # Time series analysis
    print("\n=== TIME SERIES ANALYSIS ===")
    daily_sales = df.groupby('date')['units_sold'].sum()
    print(f"Average daily total sales: {daily_sales.mean():.2f}")
    print(f"Highest daily sales: {daily_sales.max()} on {daily_sales.idxmax().strftime('%Y-%m-%d')}")
    print(f"Lowest daily sales: {daily_sales.min()} on {daily_sales.idxmin().strftime('%Y-%m-%d')}")
    
    # Top performing products
    print("\n=== TOP PERFORMING PRODUCTS ===")
    product_performance = df.groupby(['product_id', 'product_name', 'category']).agg({
        'units_sold': 'sum',
        'price': 'first'
    }).sort_values('units_sold', ascending=False)
    product_performance['total_revenue'] = product_performance['units_sold'] * product_performance['price']
    print(product_performance.head(10))
    
    # Inventory turnover analysis
    print("\n=== INVENTORY TURNOVER ANALYSIS ===")
    inventory_turnover = df.groupby(['product_id', 'product_name']).agg({
        'units_sold': 'sum',
        'current_stock': 'mean'
    })
    inventory_turnover['turnover_ratio'] = inventory_turnover['units_sold'] / inventory_turnover['current_stock']
    inventory_turnover = inventory_turnover.sort_values('turnover_ratio', ascending=False)
    print("Products with highest inventory turnover:")
    print(inventory_turnover.head(5))
    
    return df

def create_visualizations(df):
    """
    Create basic visualizations for the inventory data.
    """
    print("\n=== CREATING VISUALIZATIONS ===")
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Electronics Inventory Management - Data Analysis', fontsize=16, fontweight='bold')
    
    # 1. Daily sales trend
    daily_sales = df.groupby('date')['units_sold'].sum()
    axes[0, 0].plot(daily_sales.index, daily_sales.values, linewidth=2, color='blue')
    axes[0, 0].set_title('Daily Total Sales Trend')
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel('Total Units Sold')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Sales by category
    category_sales = df.groupby('category')['units_sold'].sum().sort_values(ascending=True)
    axes[0, 1].barh(category_sales.index, category_sales.values, color='green', alpha=0.7)
    axes[0, 1].set_title('Total Sales by Category')
    axes[0, 1].set_xlabel('Total Units Sold')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Stock status distribution
    stock_status_counts = df['stock_status'].value_counts()
    axes[1, 0].pie(stock_status_counts.values, labels=stock_status_counts.index, autopct='%1.1f%%', 
                   colors=['lightgreen', 'lightcoral'])
    axes[1, 0].set_title('Stock Status Distribution')
    
    # 4. Top 10 products by sales
    top_products = df.groupby(['product_id', 'product_name'])['units_sold'].sum().sort_values(ascending=False).head(10)
    axes[1, 1].barh(range(len(top_products)), top_products.values, color='orange', alpha=0.7)
    axes[1, 1].set_title('Top 10 Products by Sales')
    axes[1, 1].set_xlabel('Total Units Sold')
    axes[1, 1].set_yticks(range(len(top_products)))
    axes[1, 1].set_yticklabels([f"{pid}: {name[:20]}..." for pid, name in top_products.index], fontsize=8)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('inventory_analysis.png', dpi=300, bbox_inches='tight')
    print("Visualizations saved as 'inventory_analysis.png'")
    
    return fig

def main():
    """
    Main function to run the data analysis.
    """
    print("=== ELECTRONICS INVENTORY DATA ANALYSIS ===")
    
    # Analyze the data
    df = analyze_inventory_data()
    
    # Create visualizations
    try:
        create_visualizations(df)
        print("\n✓ Data analysis completed successfully!")
        print("✓ Visualizations created and saved")
    except Exception as e:
        print(f"Warning: Could not create visualizations: {e}")
        print("Data analysis completed without visualizations")
    
    print("\n=== DATA READY FOR SAGEMAKER ===")
    print("Your electronics inventory data is now ready for:")
    print("1. Uploading to S3 for SageMaker")
    print("2. Training time series forecasting models")
    print("3. Building the smart inventory management system")
    
    return df

if __name__ == "__main__":
    df = main() 