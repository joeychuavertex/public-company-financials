import pandas as pd
import requests
import streamlit as st
import datetime as dt

# key = open("api_token.txt").read()
key = st.secrets["key"]
today = dt.date.today()
start_date = today - dt.timedelta(365 * 100)


def inputs():
    st.sidebar.header("Chart Inputs")
    ticker = st.sidebar.text_input("Symbol", "LULU")
    button = st.sidebar.button("Get Data")
    return ticker, button


def get_data(ticker):
    call = f"https://eodhistoricaldata.com/api/fundamentals/{ticker}.US?api_token={key}"
    json_data = requests.get(call).json()
    general_data = json_data["General"]
    outstanding_shares_data = pd.DataFrame(json_data["outstandingShares"]["quarterly"]).T

    financial_data = json_data["Financials"]
    income_statement_data = pd.DataFrame(financial_data["Income_Statement"]["quarterly"]).T

    return general_data, outstanding_shares_data, income_statement_data


def get_ipo_data(ticker, start=start_date, end=today):
    ipo_call = f"https://eodhistoricaldata.com/api/eod/{ticker}.US?api_token={key}"
    ipo_call += f"&fmt=json&from={start}&to={end}"
    ipo_data = pd.DataFrame(requests.get(ipo_call).json())
    return ipo_data


def main():
    ticker, button = inputs()

    if button:
        general_data, outstanding_shares_data, income_statement_data = get_data(ticker.upper())
        ipo_data = get_ipo_data(ticker.upper())

        code = general_data["Code"]
        name = general_data["Name"]
        description = general_data["Description"]
        exchange = general_data["Exchange"]
        country = general_data["CountryName"]
        ipo_date = general_data["IPODate"]
        sector = general_data["Sector"]
        industry = general_data["Industry"]
        address = general_data["Address"]
        fiscal_month = general_data["FiscalYearEnd"]

        st.header(f"{name} ({code})")
        st.write(f"Exchange: {exchange}")
        st.write(f"Description: {description}")
        st.write(f"Country: {country}")
        st.write(f"IPO Date: {ipo_date}")
        st.write(f"Industry: {industry}")
        st.write(f"Sector: {sector}")
        st.write(f"Sector: {address}")
        st.write(f"Fiscal Month: {fiscal_month}")

        ipo_eod = ipo_data.loc[ipo_data['date'] == general_data["IPODate"]]
        ipo_adjusted_close = ipo_eod["adjusted_close"].values[0]
        st.write(ipo_eod)

        ipo_date = dt.datetime.strptime(ipo_date, '%Y-%m-%d').date()
        ipo_year = pd.Timestamp(ipo_date).year
        ipo_quarter = pd.Timestamp(ipo_date).quarter
        ipo_year_quarter = str(ipo_year) + "-Q" + str(ipo_quarter)
        outstanding_shares = outstanding_shares_data.loc[outstanding_shares_data['date'] == ipo_year_quarter]
        outstanding_shares_value = outstanding_shares["shares"].values[0]
        st.write(outstanding_shares)

        ipo_market_cap = ipo_adjusted_close * outstanding_shares_value
        st.write(
            f"IPO Market Cap = outstanding shares*EOD price "
            f"= {outstanding_shares_value} x {ipo_adjusted_close} "
            f"= {ipo_market_cap}"
        )

        pd.to_datetime(income_statement_data["date"], utc=False)
        income_statement_data['year'] = pd.DatetimeIndex(income_statement_data['date']).year
        income_statement_data['quarter'] = pd.DatetimeIndex(income_statement_data['date']).quarter
        st.write(income_statement_data)
        income_statement_data = income_statement_data.loc[(income_statement_data["year"] == ipo_year)
                                                & (income_statement_data["quarter"] == ipo_quarter)]
        ipo_revenue = income_statement_data["totalRevenue"][0]
        ipo_ps_ratio = float(ipo_adjusted_close) / (float(ipo_revenue)/float(outstanding_shares_value))

        st.write(
            f"P/S = adjusted_close / (totalRevenue / shares) "
            f"= {ipo_adjusted_close} / ({ipo_revenue}/{outstanding_shares_value}) "
            f"= {ipo_ps_ratio}"
        )


if __name__ == "__main__":
    main()
