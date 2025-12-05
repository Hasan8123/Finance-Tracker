import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import calendar

# Add the project root to the Python path
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..')) # Go up one level from dashboard/app.py (dashboard/ -> project root)
sys.path.insert(0, project_root)

# Import functions/logic from CLI features to reuse data reading
# We need to explicitly import from the correct paths
# Assuming 'database' is relative to the project root
# For get_month_range, we can reuse the one from analytics or transactions
from features.analytics.analytics import get_month_range

st.set_page_config(layout="wide", page_title="Personal Finance Dashboard")

st.title("💰 Personal Finance Dashboard")

# --- Helper Functions to Read and Process Data ---

def load_transactions():
    transactions_path = os.path.join(project_root, "database", "transactions.txt")
    if not os.path.exists(transactions_path):
        return pd.DataFrame(columns=["ID", "Timestamp", "Type", "Category", "Amount", "Description"])
    
    data = []
    with open(transactions_path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 6: # Ensure correct number of columns
                data.append(parts)
    
    df = pd.DataFrame(data, columns=["ID", "Timestamp", "Type", "Category", "Amount", "Description"])
    df["Amount"] = pd.to_numeric(df["Amount"]) / 100 # Convert paisa to actual amount
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

def load_budgets():
    budgets_path = os.path.join(project_root, "database", "budgets.txt")
    if not os.path.exists(budgets_path):
        return pd.DataFrame(columns=["Category", "Budget"])
    
    data = []
    with open(budgets_path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 2: # Ensure correct number of columns
                data.append(parts)
    
    df = pd.DataFrame(data, columns=["Category", "Budget"])
    df["Budget"] = pd.to_numeric(df["Budget"]) / 100 # Convert paisa to actual amount
    return df

# --- Load Data ---
transactions_df = load_transactions()
budgets_df = load_budgets()

# --- Current Month Filtering ---
now = datetime.now()
current_month_start, current_month_end = get_month_range(now) # Reusing CLI helper

current_month_transactions = transactions_df[
    (transactions_df["Timestamp"] >= current_month_start) & 
    (transactions_df["Timestamp"] <= current_month_end)
].copy() # Use .copy() to avoid SettingWithCopyWarning

# --- Financial Summary ---
total_income = current_month_transactions[current_month_transactions["Type"] == "income"]["Amount"].sum()
total_expenses = current_month_transactions[current_month_transactions["Type"] == "expense"]["Amount"].sum()
balance = total_income - total_expenses

st.subheader("📊 Current Month Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"₹{total_income:,.2f}", delta_color="normal")
col2.metric("Total Expenses", f"₹{total_expenses:,.2f}", delta_color="inverse")
col3.metric("Balance", f"₹{balance:,.2f}", delta_color="normal")

st.markdown("---")

# --- Recent Transactions ---
st.subheader("💸 Recent Transactions")
# Sort by timestamp, newest first
recent_transactions = transactions_df.sort_values(by="Timestamp", ascending=False).head(10)

# Apply color based on transaction type
def color_amount_row(row):
    color = "green" if row["Type"] == "income" else "red"
    return [f"color: {color}" for _ in row]

if not recent_transactions.empty:
    st.dataframe(
        recent_transactions.style.apply(color_amount_row, axis=1),
        hide_index=True,
        use_container_width=True,
        column_order=["Timestamp", "Type", "Category", "Amount", "Description"]
    )
else:
    st.info("No recent transactions to display.")

st.markdown("---")

# --- Spending Breakdown (Current Month) ---
st.subheader("📈 Spending Breakdown (Current Month)")
if not current_month_transactions.empty:
    expense_breakdown = current_month_transactions[current_month_transactions["Type"] == "expense"]
    if not expense_breakdown.empty:
        expense_by_category = expense_breakdown.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        st.bar_chart(expense_by_category)
    else:
        st.info("No expenses recorded this month.")
else:
    st.info("No transactions recorded this month.")

st.markdown("---")

# --- Budget Performance (Current Month) ---
st.subheader("🎯 Budget Performance (Current Month)")
if not budgets_df.empty:
    budget_performance_data = []
    for index, budget_row in budgets_df.iterrows():
        category = budget_row["Category"]
        budget_amount = budget_row["Budget"]
        spent_amount = current_month_transactions[
            (current_month_transactions["Type"] == "expense") & 
            (current_month_transactions["Category"] == category)
        ]["Amount"].sum()
        
        remaining = budget_amount - spent_amount
        utilization = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0

        budget_performance_data.append({
            "Category": category,
            "Budget": budget_amount,
            "Spent": spent_amount,
            "Remaining": remaining,
            "Utilization (%)": utilization
        })
    
    budget_performance_df = pd.DataFrame(budget_performance_data)
    
    # Apply color based on utilization for the table
    def color_utilization_cell(val):
        if not isinstance(val, (int, float)):
            return ''
        if val > 100:
            return 'background-color: #ffcccc' # Light red
        elif val >= 70:
            return 'background-color: #ffffcc' # Light yellow
        else:
            return ''

    st.dataframe(
        budget_performance_df.style.applymap(
            color_utilization_cell, 
            subset=["Utilization (%)"]
        ).format({"Budget": "₹{:.2f}", "Spent": "₹{:.2f}", "Remaining": "₹{:.2f}", "Utilization (%)": "{:.2f}%"}),
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No budgets set. Please set budgets using the CLI.")


# --- Instructions to run ---
st.sidebar.header("How to run the CLI")
st.sidebar.markdown("""
To manage your finances, use the command-line interface:
`python main.py <command> <subcommand> [options]`

**Examples:**
- Add an expense: `python main.py transactions add expense Food 50 "Lunch"`
- List transactions: `python main.py transactions list`
- Set a budget: `python main.py budgets add Food 500`
- Get recommendations: `python main.py smart-assistant recommend`
""")