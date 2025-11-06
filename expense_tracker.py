import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import base64
import os

FILE_PATH = "expenses.csv"


if os.path.exists(FILE_PATH):
    st.session_state["expenses"] = pd.read_csv(FILE_PATH)
else:
    st.session_state["expenses"] = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])


st.title(" 💰 Daily Expense Tracker")


def add_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("/Users/naveenkothi/Documents/Vscode/python/proj.png")

st.header("Add a New Expense")

with st.form("expense_form", clear_on_submit=True):
    exp_date = st.date_input("Date", value=date.today())
    category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"])
    amount = st.number_input("Amount ($)", min_value=0.0, step=0.5, format="%.2f")
    note = st.text_input("Note (optional)")
    submitted = st.form_submit_button("Add Expense")

    if submitted and amount > 0:
        new_expense = pd.DataFrame([[exp_date, category, amount, note]], 
                                   columns=["Date", "Category", "Amount", "Note"])
        st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_expense], ignore_index=True)
        
        # Save to CSV
        st.session_state["expenses"].to_csv(FILE_PATH, index=False)
        st.success("Expense added successfully ")


st.header(" Expense Records")
if not st.session_state["expenses"].empty:
    st.dataframe(st.session_state["expenses"], use_container_width=True)

    
    st.subheader("Delete an Expense")
    delete_index = st.number_input("Enter the index of the expense to delete:", 
                                   min_value=0, 
                                   max_value=len(st.session_state["expenses"])-1, 
                                   step=1)

    if st.button("Delete Expense"):
        st.session_state["expenses"].drop(delete_index, inplace=True)
        st.session_state["expenses"].reset_index(drop=True, inplace=True)
        
        
        st.session_state["expenses"].to_csv(FILE_PATH, index=False)
        st.success(f"Expense at index {delete_index} deleted successfully ")


   
st.subheader("Edit an Expense")

if not st.session_state["expenses"].empty:
    edit_index = st.number_input(
        "Enter index of expense to edit:",
        min_value=0,
        max_value=len(st.session_state["expenses"]) - 1,
        value=0,
        step=1,
        key="edit_index"
    )

    if st.button("Load Expense for Edit"):
        st.session_state["current_edit_index"] = edit_index


if "current_edit_index" in st.session_state:
    idx = st.session_state["current_edit_index"]
    if 0 <= idx < len(st.session_state["expenses"]):
        expense_to_edit = st.session_state["expenses"].iloc[idx]

        st.write("Editing:", expense_to_edit)

       
        new_date = st.date_input(
            "Edit Date",
            value=pd.to_datetime(expense_to_edit["Date"]).date(),
            key="edit_date"
        )

        categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
        new_category = st.selectbox(
            "Edit Category",
            categories,
            index=categories.index(expense_to_edit["Category"]),
            key="edit_category"
        )

        new_amount = st.number_input(
            "Edit Amount",
            min_value=0.0,
            value=float(expense_to_edit["Amount"]),
            step=0.5,
            format="%.2f",
            key="edit_amount"
        )

        new_note = st.text_input(
            "Edit Note",
            value=str(expense_to_edit["Note"]),
            key="edit_note"
        )

        if st.button("Save Changes"):
            st.session_state["expenses"].at[idx, "Date"] = new_date
            st.session_state["expenses"].at[idx, "Category"] = new_category
            st.session_state["expenses"].at[idx, "Amount"] = new_amount
            st.session_state["expenses"].at[idx, "Note"] = new_note

            
            st.session_state["expenses"].to_csv(FILE_PATH, index=False)

            st.success("Expense updated successfully ")

else:
    st.info("No expenses available to edit yet.")
    
    # Filter Expenses 
    st.subheader(" Filter Expenses")
    filter_category = st.selectbox("Filter by Category", ["All"] + st.session_state["expenses"]["Category"].unique().tolist())
    filter_date = st.date_input("Filter by Date (optional)", value=None, key="filter_date")

    filtered_expenses = st.session_state["expenses"]

    if filter_category != "All":
        filtered_expenses = filtered_expenses[filtered_expenses["Category"] == filter_category]

    if filter_date:
        filtered_expenses = filtered_expenses[filtered_expenses["Date"] == str(filter_date)]

    st.write("Filtered Expenses:")
    st.dataframe(filtered_expenses, use_container_width=True)

    #  Monthly Summary
    st.subheader("Monthly Summary")
    st.session_state["expenses"]["Date"] = pd.to_datetime(st.session_state["expenses"]["Date"])
    monthly_summary = st.session_state["expenses"].groupby(st.session_state["expenses"]["Date"].dt.to_period("M"))["Amount"].sum().reset_index()
    monthly_summary["Date"] = monthly_summary["Date"].astype(str)

    st.dataframe(monthly_summary, use_container_width=True)

    bar_month = alt.Chart(monthly_summary).mark_bar().encode(
        x="Date",
        y="Amount",
        tooltip=["Date", "Amount"]
    )
    st.altair_chart(bar_month, use_container_width=True)

# Summary 
st.header("Summary")
if not st.session_state["expenses"].empty:
    total = st.session_state["expenses"]["Amount"].sum()
    st.metric("Total Expenses", f"${total:.2f}")

    by_category = st.session_state["expenses"].groupby("Category")["Amount"].sum().reset_index()
    pie = alt.Chart(by_category).mark_arc().encode(
        theta="Amount",
        color="Category",
        tooltip=["Category", "Amount"]
    )
    st.altair_chart(pie, use_container_width=True)

    # Bar Chart for Expenses by Category
    st.subheader("Expenses by Category (Bar Chart)")
    bar = alt.Chart(by_category).mark_bar().encode(
        x=alt.X("Category", sort="-y"),
        y="Amount",
        color="Category",
        tooltip=["Category", "Amount"]
    ).properties(height=400)
    st.altair_chart(bar, use_container_width=True)
