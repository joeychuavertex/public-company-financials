import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# key = open("api_token.txt").read()
key = st.secrets["key"]
today = dt.date.today()
start_date = today - dt.timedelta(365 * 10)
#
# fig = go.Figure(go.Waterfall(
#     name="20", orientation="v",
#     measure=["relative", "relative", "total", "relative", "relative", "total"],
#     x=["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
#     textposition="outside",
#     text=["+60", "+80", "", "-40", "-20", "Total"],
#     y=[60, 80, 0, -40, -20, 0],
#     connector={"line": {"color": "rgb(63, 63, 63)"}},
# ))
#
# fig.update_layout(
#     title="Profit and loss statement 2018",
#     showlegend=True
# )
#
# st.plotly_chart(fig, use_container_width=True)


def inputs():
    st.sidebar.header("Chart Inputs")
    ticker = st.sidebar.text_input("Symbol", "AAPL")
    start = st.sidebar.date_input("Start Date", start_date)
    end = st.sidebar.date_input("Start Date", today)
    button = st.sidebar.button("Get Data")
    return ticker, start, end, button


def get_data(ticker):
    call = f"https://eodhistoricaldata.com/api/fundamentals/{ticker}.US?api_token={key}"
    json_data = requests.get(call).json()
    financial_data = json_data["Financials"]

    balance_sheet = pd.DataFrame(financial_data["Balance_Sheet"]["quarterly"])
    st.header("Balance Sheet")
    st.write(balance_sheet)

    cash_flow = pd.DataFrame(financial_data["Cash_Flow"]["quarterly"])
    st.header("Cash Flow")
    st.write(cash_flow)

    income_statement = pd.DataFrame(financial_data["Income_Statement"]["quarterly"])
    st.header("Income Statement")
    st.write(income_statement)

    income_statement_transpose = income_statement.T

    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("Total Revenue")
        income_statement_transpose['date'] = pd.to_datetime(income_statement_transpose['date']).dt.date
        income_statement_transpose = income_statement_transpose.loc[
            (income_statement_transpose['date'] >= start_date)
            & (income_statement_transpose['date'] < today)
            ]
        st.line_chart(income_statement_transpose['totalRevenue'], height=200, width=200, use_container_width=True)

    with col2:
        st.header("Gross Profit")
        st.line_chart(income_statement_transpose['grossProfit'], height=200, width=200, use_container_width=True)

    with col3:
        st.header("EBITDA")
        st.line_chart(income_statement_transpose['ebitda'], height=200, width=200, use_container_width=True)

    return balance_sheet, cash_flow, income_statement


def main():
    ticker, start, end, button = inputs()
    if button:
        get_data(ticker.upper())


if __name__ == "__main__":
    main()
