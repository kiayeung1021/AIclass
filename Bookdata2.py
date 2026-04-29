import streamlit as st
import pandas as pd
import io

# --- Page Config ---
st.set_page_config(page_title="Data Pro - Book Analyzer", layout="wide")

st.title("📚 Universal Book Data Analyzer")
st.markdown("Upload any Excel file to begin your analysis.")

# --- Sidebar: File Upload ---
with st.sidebar:
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    
    st.divider()
    
    # These settings only appear if a file is actually uploaded
    if uploaded_file is not None:
        # Load the Excel object to extract sheet names
        xl = pd.ExcelFile(uploaded_file)
        sheet_name = st.selectbox("2. Select Sheet", xl.sheet_names)
        
        st.header("3. Options")
        clean_data = st.checkbox("Auto-Clean Data", value=True, 
                                 help="Removes rows with missing Rating, Price, or Reviews")
        
        run_btn = st.button("🚀 Run Analysis", type="primary")

# --- Main Logic ---
if uploaded_file is not None:
    try:
        # Read the selected sheet into a DataFrame
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

        if run_btn:
            # Data Cleaning (Logic from original Tkinter app)
            if clean_data:
                df = df.dropna(subset=['User Rating', 'Price', 'Reviews'])

            # Core Calculations
            max_rating = df['User Rating'].max()
            best_books = df[df['User Rating'] == max_rating]['Name'].tolist()
            
            df['Revenue'] = df['Price'] * df['Reviews']
            top_earner = df.loc[df['Revenue'].idxmax()]
            
            pop_year = df.groupby('Year')['Reviews'].sum().idxmax()

            # --- Results Display ---
            st.success(f"Analysis complete for: {uploaded_file.name}")
            
            # Metrics Row
            col1, col2, col3 = st.columns(3)
            col1.metric("Highest Rating", f"{max_rating} ⭐")
            col2.metric("Most Popular Year", int(pop_year))
            col3.metric("Top Revenue", f"${top_earner['Revenue']:,.2f}")

            # Detailed Insights
            st.subheader("Key Insights")
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**Top Rated Book(s):**\n{', '.join(best_books[:3])}...")
            with c2:
                st.info(f"**Highest Earner:**\n{top_earner['Name']}")

            # Data Preview
            with st.expander("View Full Processed Data"):
                st.dataframe(df, use_container_width=True)

            # --- Export / Download ---
            report_df = pd.DataFrame([{
                "Source File": uploaded_file.name,
                "Highest Rating": max_rating,
                "Top Earner": top_earner['Name'],
                "Total Revenue": f"${top_earner['Revenue']:,.2f}",
                "Most Popular Year": pop_year
            }])

            # Generate Excel in memory
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                report_df.to_excel(writer, index=False, sheet_name='Summary')
            
            st.download_button(
                label="📥 Download Summary Report",
                data=buffer.getvalue(),
                file_name=f"Analysis_Report_{uploaded_file.name}",
                mime="application/vnd.ms-excel"
            )
        else:
            st.info("File uploaded! Configure settings in the sidebar and click 'Run Analysis'.")

    except Exception as e:
        st.error(f"Error processing file: {e}")
        st.warning("Ensure your Excel file has columns named: 'User Rating', 'Price', 'Reviews', 'Name', and 'Year'.")

else:
    # Display a placeholder when no file is uploaded
    st.info("Please upload an Excel file using the sidebar to get started.")