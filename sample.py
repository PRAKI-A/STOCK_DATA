import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt

# Database connection
# Connection credentials
user = '2LLo4bZkC31yEUV.root'
password = 'LuChtj8gRkjbD3XE'
host = "gateway01.us-west-2.prod.aws.tidbcloud.com"
port = 4000
database = 'test'

# Secure connection using SSL
connect_args = {
    "ssl": {
        "ssl_ca": "/path/to/public-cert.pem"  # 🔺 Required!
    }
}

# Create SQLAlchemy engine
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
    connect_args=connect_args
)
#engine = create_engine("mysql+pymysql://root:Vani%401234567@127.0.0.1:3306/stock_analysis")

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
selection = st.sidebar.radio("Go to", [
    "Home",
    "Volatility Analysis",
    "Cumulative Returns",
    "Sector Performance",
    "Stock Correlation",
    "Gainers & Losers"
])

# Page functions
def home():
    st.title("📊 Stock Analysis Dashboard")
    st.write("Welcome! Use the sidebar to navigate through different analyses.")

def volatility_analysis():
    st.header("🔄 Top 10 Most Volatile Stocks")
    query = "SELECT * FROM volatility_analysis ORDER BY volatility DESC LIMIT 10"
    df = pd.read_sql(query, engine)
    st.bar_chart(data=df.set_index("symbol")["volatility"])

def cumulative_return():
    st.header("📈 Cumulative Return for Top 5 Stocks")
    query = "SELECT * FROM cumulative_return"
    df = pd.read_sql(query, engine)

    # Fix potential 'date' error
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        for symbol in df['symbol'].unique():
            st.line_chart(df[df['symbol'] == symbol].set_index('date')["cumulative_return"])
    else:
        st.error("❌ 'date' column not found in 'cumulative_return' table.")

def sector_performance():
    st.header("🏭 Sector-wise Average Yearly Return")
    query = "SELECT sector, AVG(yearly_return) AS avg_return FROM sectorwise_performance GROUP BY sector"
    df = pd.read_sql(query, engine)
    st.bar_chart(data=df.set_index("sector")["avg_return"])

def stock_correlation():
    st.header("📊 Stock Price Correlation Heatmap")
    query = "SELECT * FROM correlation_matrix"
    df = pd.read_sql(query, engine)
    fig, ax = plt.subplots(figsize=(30, 25))  # Set the figure size here
    sns.heatmap(df.set_index("symbol"), cmap="coolwarm", annot=True, ax=ax)
    st.pyplot(fig)

def gainers_losers():
    st.header("📅 Monthly Top Gainers & Losers")

    # Dropdown
    
    months_query = "SELECT DISTINCT month FROM top_5_gainers_monthly"
    months = pd.read_sql(months_query, engine)["month"].tolist()
    selected_month = st.selectbox("Select a Month", months)

    gainers = pd.read_sql(f"SELECT * FROM top_5_gainers_monthly WHERE month = '{selected_month}'", engine)
    st.subheader("Top 5 Gainers")
    st.bar_chart(gainers.set_index("symbol")["monthly_return"])

    losers = pd.read_sql(f"SELECT * FROM top_5_losers_monthly WHERE month = '{selected_month}'", engine)
    st.subheader("Top 5 Losers")
    st.bar_chart(losers.set_index("symbol")["monthly_return"])
 


# Routing
pages = {
    "Home": home,
    "Volatility Analysis": volatility_analysis,
    "Cumulative Returns": cumulative_return,
    "Sector Performance": sector_performance,
    "Stock Correlation": stock_correlation,
    "Gainers & Losers": gainers_losers
}
pages[selection]()