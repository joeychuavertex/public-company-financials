import pandas as pd
import requests
import streamlit as st
import datetime as dt

key = open("api_token.txt").read()
today = dt.date.today()
start_date = today - dt.timedelta(365)


def inputs():
    st.sidebar.header("Chart Inputs")
    ticker = st.sidebar.text_input("Symbol", "AAPL")
    start = st.sidebar.date_input("Start Date", start_date)
    end = st.sidebar.date_input("End Date", today)
    button = st.sidebar.button("Get Chart")
    return ticker, start, end, button


def get_data(ticker, start=start_date, end=today):
    call = f"https://eodhistoricaldata.com/api/eod/{ticker}.US?api_token={key}"
    call += f"&fmt=json&from={start}&to={end}"
    data = pd.DataFrame(requests.get(call).json())
    st.write(data)
    return data



def main():
    ticker, start, end, button = inputs()
    if button:
        data = get_data(ticker.upper(), start, end)
        st.header(f"Stock Price Graph for {ticker}")
        st.write(f"{start} to {end}")
        st.line_chart(data['adjusted_close'])


if __name__ == "__main__":
    main()
