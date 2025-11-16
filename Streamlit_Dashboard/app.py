import streamlit as st
import pandas as pd
import plotly.express as px

# page configuration
st.title("Company performance dashboard")
st.write("Upload your company performance data to see the insights")
st.sidebar.header("Upload your data file")


def _standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common column name variants to standard names and coerce types.

    - 'Date' for date-like columns
    - 'Revenue' for revenue/sales/amount columns
    - 'Expenses' for expense/cost columns
    If a column is missing, create it with sensible defaults (0 for numeric).
    """
    # build mapping from existing column names to standardized names
    col_map = {}
    for col in df.columns:
        name = col.strip()
        lname = name.lower()
        if 'date' in lname or 'month' in lname or 'period' in lname:
            col_map[col] = 'Date'
        elif 'revenue' in lname or 'sale' in lname or 'sales' in lname or 'amount' in lname:
            col_map[col] = 'Revenue'
        elif 'expense' in lname or 'cost' in lname:
            col_map[col] = 'Expenses'
        else:
            col_map[col] = name

    df = df.rename(columns=col_map)

    # Date conversion (may end up NaT if not parseable)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    else:
        df['Date'] = pd.NaT

    # Numeric coercion and sensible defaults
    if 'Revenue' in df.columns:
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
    else:
        df['Revenue'] = 0.0

    if 'Expenses' in df.columns:
        df['Expenses'] = pd.to_numeric(df['Expenses'], errors='coerce').fillna(0)
    else:
        # If expenses are missing in both files, assume 0 to avoid KeyError
        df['Expenses'] = 0.0

    return df


col1, col2 = st.columns(2)
with col1:
    uploaded_file1 = st.file_uploader("Choose a file", type="csv", key="file_uploader1")
with col2:
    uploaded_file2 = st.file_uploader("Choose a file", type="csv", key="file_uploader2")

if uploaded_file1 is not None and uploaded_file2 is not None:
    try:
        df1 = pd.read_csv(uploaded_file1)
        df2 = pd.read_csv(uploaded_file2)
        df1 = _standardize_dataframe(df1)
        df2 = _standardize_dataframe(df2)
        df1['Company'] = "Company A"
        df2['Company'] = "Company B"
        df_combined = pd.concat([df1, df2], ignore_index=True)
        st.sidebar.success("Data uploaded successfully")
    except Exception as e:
        st.sidebar.error(f"Error loading files: {e}")

    # show dashboard only if data was loaded successfully
    if 'df_combined' in locals():
        st.header("Side-by-side performance")
        st.subheader("Overall Totals")
        kp_col1, kp_col2, kp_col3 = st.columns(3)
        with kp_col1:
            total_revenue = df_combined['Revenue'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        with kp_col2:
            total_expenses = df_combined['Expenses'].sum()
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        with kp_col3:
            total_profit = total_revenue - total_expenses
            st.metric("Total Profit", f"${total_profit:,.2f}")

        st.subheader("Revenue and Expenses over Time")
        # Only show metrics that exist (we always ensure both columns exist above,
        # but keep selection robust for future datasets)
        metrics_available = [m for m in ['Revenue', 'Expenses'] if m in df_combined.columns]
        metric_to_plot = st.selectbox("Select Metric to Plot", metrics_available)

        # Ensure there is a Date-like column for plotting; if not, create an index-based period
        if 'Date' not in df_combined.columns or df_combined['Date'].isna().all():
            df_combined = df_combined.reset_index().rename(columns={'index': 'Period'})
            x_col = 'Period'
        else:
            df_combined = df_combined.sort_values('Date')
            x_col = 'Date'

        fig = px.bar(
            df_combined,
            x=x_col,
            y=metric_to_plot,
            color='Company',
            barmode='group',
            title=f"{metric_to_plot} Over Time",
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("View Data Summary"):
            st.dataframe(df_combined.describe())
else:
    st.sidebar.info("Please upload both data files to see the dashboard.")

