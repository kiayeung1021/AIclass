import streamlit as st
import pandas as pd
import io
import os

# --- Configuration ---
# Updated path based on your new location and filename
FILE_PATH = r"C:\Users\toget\Desktop\Python\Bookdata 2.xlsx"

st.set_page_config(page_title="Data Pro - Book Analyzer v2.0", layout="wide")

# --- UI Header ---
st.title("📊 Book Data Analyzer")

# Check if the file exists at the hardcoded path
if os.path.exists(FILE_PATH):
    try:
        # Load the Excel file
        xl = pd.ExcelFile(FILE_PATH)
        
        # --- Sidebar ---
        with st.sidebar:
            st.header("Settings")
            sheet_name = st.selectbox("Select Sheet", xl.sheet_names)
            clean_data = st.checkbox("Auto-Clean Data", value=True)
            run_btn = st.button("Run Analysis", type="primary")

        # Load the specific sheet
        df = pd.read_excel(FILE_PATH, sheet_name=sheet_name)

        if run_btn:
            # 1. Cleaning
            if clean_data:
                df = df.dropna(subset=['User Rating', 'Price', 'Reviews'])

            # 2. Logic
            max_rating = df['User Rating'].max()
            best_books = df[df['User Rating'] == max_rating]['Name'].tolist()
            
            df['Revenue'] = df['Price'] * df['Reviews']
            top_earner = df.loc[df['Revenue'].idxmax()]
            pop_year = df.groupby('Year')['Reviews'].sum().idxmax()

            # 3. Display Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Highest Rating", f"{max_rating} ⭐")
            col2.metric("Most Popular Year", int(pop_year))
            col3.metric("Top Revenue", f"${top_earner['Revenue']:,.2f}")

            # 4. Results
            st.subheader(f"Insights from {sheet_name}")
            st.write(f"**Top Earner:** {top_earner['Name']}")
            st.write(f"**Best Rated Sample:** {', '.join(best_books[:2])}...")
            
            st.dataframe(df, use_container_width=True)

            # 5. Export
            report_df = pd.DataFrame([{
                "Highest Rating": max_rating,
                "Top Earner": top_earner['Name'],
                "Total Revenue": f"${top_earner['Revenue']:,.2f}",
                "Most Popular Year": pop_year
            }])
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                report_df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Download Report",
                data=buffer.getvalue(),
                file_name="Book_Analysis_Report.xlsx",
                mime="application/vnd.ms-excel"
            )

    except Exception as e:
        st.error(f"Error reading the file: {e}")
else:
    st.error("File Not Found!")
    st.info(f"Please ensure your file is named **Bookdata 2.xlsx** and is located at: \n`{FILE_PATH}`")