import json
from math import comb
import requests
import pandas as pd
import streamlit as st
import numpy as np
from twelvedata import TDClient
import plotly.express as px
import requests
import json
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
from dateutil.relativedelta import relativedelta

from datetime import date
from datetime import timedelta
st.set_page_config(layout="wide")


APIKEY=st.secrets["mainAPI"]
FMPAPI=st.secrets["FMPAPI"]

FMP2 = st.secrets["mainAPI"]


# apikey=st.secrets["APIKEY"]
# td = TDClient(apikey=apikey)
# fmpAPI = st.secrets["FMPAPI"]

apikey=APIKEY
fmpAPI = FMPAPI
year = 2022
fpm1 = st.secrets["mainAPI"]
fpm2 = st.secrets["mainAPI"]

mainAPI = st.secrets["mainAPI"]


today = (datetime.datetime.now((datetime.timezone.utc)) - relativedelta(minutes=16)).isoformat()

maxRating = 21



def chart_data(asset):

    symbol = asset

    URL = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=500&apikey={fmpAPI}"


    data = requests.get(URL)
    data = data.json()


    lSymbol = []
    lDate = []
    lEps =[]
    lEbitda =[]
    lRevenue =[]

    for value in data:

        date = value['date']
        eps = value['eps']
        ebitda = value['ebitda']
        revenue = value['revenue']

        lDate.append(date)
        lEps.append(eps)
        lRevenue.append(revenue)
        lEbitda.append(ebitda)


    df = pd.DataFrame()


    df['date'] = lDate 
    df['eps'] = lEps
    df['ebitda'] = lEbitda 
    df['revenue'] = lRevenue 

    df = df.set_index('date')

    return df

def dcf(asset):
    URL = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{asset}?limit=500&apikey={fmpAPI}"


    data = requests.get(URL)
    data = data.json()

    lDate = []
    lDcf =[]
    lPrice =[]

    for value in data:

        date = value['date']
        currentPrice = value['Stock Price']
        dcfPrice = value['dcf']

        lDate.append(date)
        lPrice.append(currentPrice)
        lDcf.append(dcfPrice)


    df = pd.DataFrame()


    df['date'] = lDate 
    df['DCF'] = lDcf
    df['Price'] = lPrice 
    df = df.set_index('date')

    return df

def sectorPerformance():
    URL = f"https://financialmodelingprep.com/api/v3/sector-performance?apikey={fmpAPI}"
    data = requests.get(URL)
    data = data.json()

    sectorl =[]
    changesPercentagel =[]


    for value in data:
        sector = value['sector']
        perChange = value['changesPercentage']  

        perChange = perChange.replace("%", "")
        perChange = pd.to_numeric(perChange)

        

        sectorl.append(sector)
        changesPercentagel.append(perChange)


    df = pd.DataFrame()


    df['Sector'] = sectorl 
    df['Movement (%)'] = changesPercentagel

    df = df.set_index('Sector')

    return df

def tickerGraph(asset):

    # Define the API endpoint for getting the AAPL stock data
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{asset}?apikey={mainAPI}"

    # Make the API request and get the data
    response = requests.get(url)
    data = response.json()["historical"]

    # Convert the data to a pandas dataframe and select the relevant columns
    df = pd.DataFrame(data)
    df = df[["date", "open", "high", "low", "close"]]

    # Convert the date column to datetime format
    df["date"] = pd.to_datetime(df["date"])

    
    fig2 = go.Figure(data=go.Scatter(x=df["date"], y=df["close"]))

    # Set the chart layout
    fig2.update_layout(title=f"{asset} Historic price",
                    yaxis_title=f"{asset} Stock Price",
                    xaxis_rangeslider_visible=False)

    # Define the plotly candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=df['date'],
                                        open=df['open'],
                                        high=df['high'],
                                        low=df['low'],
                                        close=df['close'])])

    # Set the chart layout
    fig.update_layout(title=f"{asset} Historic price",
                    yaxis_title=f"{asset} Stock Price",
                    xaxis_rangeslider_visible=False)
    
    return fig, fig2


def sectorgraph():
    df = sectorPerformance()
    fig = px.bar(df, x=df.index, y='Movement (%)')
    # fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=True)
    fig.update_layout(yaxis={'visible': True, 'showticklabels': True})
    sectorGraphObject = fig
    return sectorGraphObject

def gainerslosers():

    loserSymbolsl = []
    gainersSymbolsl = []
    losernamel = []
    gainernamel = []
    loserchangel=[]
    gainerchangel = []
    typeLoser = []
    typeGainer = []

    fmpAPI = 'aa005c9f1003c4b4d396cc1e7037272f'



    URL = f"https://financialmodelingprep.com/api/v3/stock_market/losers?apikey={fmpAPI}"
    URLGainer = f"https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey={fmpAPI}"
    data = requests.get(URL)
    data = data.json()

    dataGainer = requests.get(URLGainer)
    dataGainer = dataGainer.json()


    for value in data:
        symbol = value['symbol']
        name = value['name']
        changeLoser = np.absolute(value['changesPercentage'])

        loserSymbolsl.append(symbol)
        losernamel.append(name)
        loserchangel.append(changeLoser)
        typeLoser.append('Loser')

    for value in dataGainer:
        symbol = value['symbol']
        name = value['name']
        changeGainer = value['changesPercentage']

        gainersSymbolsl.append(symbol)
        gainernamel.append(name)
        gainerchangel.append(changeGainer)
        typeGainer.append('Gainer')

    dfLoser = pd.DataFrame()
    dfGainer = pd.DataFrame()

    dfLoser['Symbol'] = loserSymbolsl 
    dfLoser['Name'] = losernamel
    dfLoser['Type'] = typeLoser
    dfLoser['Change'] = loserchangel

    dfGainer['Symbol'] = gainersSymbolsl 
    dfGainer['Name'] = gainernamel
    dfGainer['Type'] = typeGainer
    dfGainer['Change'] = gainerchangel

    dfLoser = dfLoser.set_index('Symbol')
    dfGainer = dfGainer.set_index('Symbol')


    frames = [dfGainer, dfLoser]

    result = pd.concat(frames)
    result = result.sort_values('Name')

    fig = px.scatter(result, x='Name', y="Change", color="Type",
                hover_name="Name",size="Change")

    return dfLoser, dfGainer, result, fig

def incomeStatement(asset):
    URL = f'https://financialmodelingprep.com/api/v3/income-statement/{asset}?limit=240&apikey={fmpAPI}'
    data = requests.get(URL)
    data = data.json()

    datel= []
    revenuel = []
    grossProfitl = []
    netIncomel = []


    for value in data:
        date = value['date']
        revenue = value['revenue']
        grossProfit = value['grossProfit']
        netIncome = value['netIncome']

        datel.append(date)
        revenuel.append(revenue)
        grossProfitl.append(grossProfit)
        netIncomel.append(netIncome)

    df = pd.DataFrame()

    df['Date'] = datel
    df['Revenue'] = revenuel
    df['Gross profit'] = grossProfitl
    df['Net income'] = netIncomel

    df = df.set_index('Date')

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df['Revenue'],
                        mode='lines+markers',
                        name='Revenue'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Gross profit'],
                        mode='lines+markers',
                        name='Gross profit'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Net income'],
                        mode='lines+markers',
                        name='Net income'))


    return df, fig

def companyProfile(symbol):
    url = f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey=f24751d54f3deaca88cd37e1d08d6f62'

    df = requests.get(url).json()
    df= df[0]

    description = df["description"]

    return description


def incomeSatement(symbol):
    url = f'https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=240&apikey={fpm1}'

    response = requests.get(url)
    data = response.json()
    # Extract the data for the last 5 years
    years = [f'{i}-12-31' for i in range(year, 2017, -1)]

    end_date = date(year, 12, 31)
    quarters = [end_date - relativedelta(months=3*i) for i in range(10)]
    quarters = [quarter.strftime('%Y-%m-%d') for quarter in quarters]

    data_5_years = {year: data[i] for i, year in enumerate(years)}


    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data_5_years)


    df = df.drop(['reportedCurrency', 'cik', 'link', 'finalLink', 'period', 'acceptedDate', 'fillingDate', 'symbol', 'calendarYear'])

    new_index = ['Date','Total revenue', 'Cost of revenue',
                'Gross profit', 'Gross profit ratio', 'Research and development expenses',
                'General and administrative expenses', 'Selling and marketing expenses',
                'Selling, general and administrative expenses', 'Other expenses',
                'Operating expenses', 'Cost and expenses', 'Interest income',
                'Interest expense', 'Depreciation and amortization', 'EBITDA',
                'EBITDA ratio', 'Operating income', 'Operating income ratio',
                'Total other income expenses net', 'Income before tax',
                'Income before tax ratio', 'Income tax expense', 'Net income',
                'Net income ratio', 'EPS', 'EPS diluted', 
                'Weighted average shares outstanding',
                'Weighted average shares outstanding diluted']

    df.index = new_index

    new_index = ['Date','Total revenue', 'Cost of revenue',
             'Gross profit', 'Research and development expenses',
             'General and administrative expenses', 'Selling and marketing expenses',
             'Selling, general and administrative expenses', 'Other expenses',
             'Operating expenses', 'Cost and expenses', 'Interest income',
             'Interest expense', 'Depreciation and amortization', 'EBITDA',
             'Operating income', 'Total other income expenses net', 
             'Income before tax', 'Income tax expense', 'Net income',
             'EPS', 'EPS diluted', 
             'Weighted average shares outstanding',
             'Weighted average shares outstanding diluted',
             'Gross profit ratio', 'EBITDA ratio', 
             'Operating income ratio', 'Income before tax ratio',
             'Net income ratio']

    df = df.reindex(new_index)




    df = df.dropna()
    
    df = df.loc[(df != 0).any(axis=1)]




    new_header = df.iloc[0].values.tolist()
    df = df[1:] # remove the first row
    df.columns = new_header # set the subheader row as the column names



    return df

def balanceSheet(symbol):
    url = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}?limit=120&apikey={fpm2}'

    response = requests.get(url)
    data = response.json()
    # Extract the data for the last 5 years
    years = [f'{i}-12-31' for i in range(year, 2017, -1)]


    data_5_years = {year: data[i] for i, year in enumerate(years)}

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data_5_years)


    df = df.drop(['symbol', 'reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period', 'link', 'finalLink'])


    df = df.rename(index = {
        'cashAndCashEquivalents': 'Cash and cash equivalents',
        'shortTermInvestments': 'Short-term investments',
        'cashAndShortTermInvestments': 'Cash and short-term investments',
        'netReceivables': 'Net receivables',
        'inventory': 'Inventory',
        'otherCurrentAssets': 'Other current assets',
        'totalCurrentAssets': 'Total current assets',
        'propertyPlantEquipmentNet': 'Property, plant, and equipment, net',
        'netDebt': 'Net debt',
        'goodwillAndIntangibleAssets': 'Goodwill and intangible assets',
        'intangibleAssets': 'Intangible assets',
        'goodwill': 'Goodwill',
        'longTermInvestments': 'Long-term investments',
        'otherNonCurrentAssets': 'Other non-current assets',
        'totalNonCurrentAssets': 'Total non-current assets',
        'totalAssets': 'Total assets',
        'accountPayables': 'Accounts payable',
        'shortTermDebt': 'Short-term debt',
        'deferredRevenue': 'Deferred revenue',
        'otherCurrentLiabilities': 'Other current liabilities',
        'totalCurrentLiabilities': 'Total current liabilities',
        'longTermDebt': 'Long-term debt',
        'deferredRevenueNonCurrent': 'Deferred revenue, non-current',
        'deferredTaxLiabilitiesNonCurrent': 'Deferred tax liabilities, non-current',
        'otherNonCurrentLiabilities': 'Other non-current liabilities',
        'totalNonCurrentLiabilities': 'Total non-current liabilities',
        'totalLiabilities': 'Total liabilities',
        'commonStock': 'Common stock',
        'retainedEarnings': 'Retained earnings',
        'accumulatedOtherComprehensiveIncomeLoss': 'Accumulated other comprehensive income (loss)',
        'totalStockholdersEquity': 'Total stockholders\' equity',
        'totalLiabilitiesAndStockholdersEquity': 'Total liabilities and stockholders\' equity',
        'totalEquity': 'Total equity',
        'totalLiabilitiesAndTotalEquity': 'Total liabilities and total equity',
        'totalInvestments': 'Total investments',
        'totalDebt': 'Total debt'
    })


    df = df.loc[(df != 0).any(axis=1)]


    new_header = df.iloc[0].values.tolist()
    df = df[1:] # remove the first row
    df.columns = new_header # set the subheader row as the column names



    return df


def cfStatement(symbol):
    url = f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}?limit=120&apikey={fpm2}'

    response = requests.get(url)
    data = response.json()
    # Extract the data for the last 5 years
    years = [f'{i}-12-31' for i in range(year, 2017, -1)]


    data_5_years = {year: data[i] for i, year in enumerate(years)}

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data_5_years)




    df = df.drop(['symbol', 'reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear', 'period', 'link', 'finalLink'])


    df = df.rename(index={
    'netIncome': 'Net Income',
    'depreciationAndAmortization': 'Depreciation and Amortization',
    'deferredIncomeTax': 'Deferred Income Tax',
    'stockBasedCompensation': 'Stock-Based Compensation',
    'changeInWorkingCapital': 'Change in Working Capital',
    'accountsReceivables': 'Accounts Receivables',
    'inventory': 'Inventory',
    'accountsPayables': 'Accounts Payables',
    'otherWorkingCapital': 'Other Working Capital',
    'otherNonCashItems': 'Other Non-Cash Items',
    'netCashProvidedByOperatingActivities': 'Net Cash Provided by Operating Activities',
    'investmentsInPropertyPlantAndEquipment': 'Investments in Property, Plant and Equipment',
    'acquisitionsNet': 'Acquisitions (Net)',
    'purchasesOfInvestments': 'Purchases of Investments',
    'salesMaturitiesOfInvestments': 'Sales/Maturities of Investments',
    'otherInvestingActivites': 'Other Investing Activities',
    'netCashUsedForInvestingActivites': 'Net Cash Used for Investing Activities',
    'debtRepayment': 'Debt Repayment',
    'commonStockIssued': 'Common Stock Issued',
    'commonStockRepurchased': 'Common Stock Repurchased',
    'dividendsPaid': 'Dividends Paid',
    'otherFinancingActivites': 'Other Financing Activities',
    'netCashUsedProvidedByFinancingActivities': 'Net Cash Used/Provided by Financing Activities',
    'effectOfForexChangesOnCash': 'Effect of Forex Changes on Cash',
    'netChangeInCash': 'Net Change in Cash',
    'cashAtEndOfPeriod': 'Cash at End of Period',
    'cashAtBeginningOfPeriod': 'Cash at Beginning of Period',
    'operatingCashFlow': 'Operating Cash Flow',
    'capitalExpenditure': 'Capital Expenditure',
    'freeCashFlow': 'Free Cash Flow'
    })



    df = df.loc[(df != 0).any(axis=1)]


    new_header = df.iloc[0].values.tolist()
    df = df[1:] # remove the first row
    df.columns = new_header # set the subheader row as the column names



    return df

def ttmratio(symbol):
    url = f'https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={mainAPI}'

    response = requests.get(url)
    data = response.json()[0]

    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.rename(index={
        'dividendYielTTM': 'Dividend Yield',
        'dividendYielPercentageTTM': 'Dividend Yield Percentage',
        'peRatioTTM': 'PE Ratio',
        'pegRatioTTM': 'PEG Ratio',
        'payoutRatioTTM': 'Payout Ratio',
        'currentRatioTTM': 'Current Ratio',
        'quickRatioTTM': 'Quick Ratio',
        'cashRatioTTM': 'Cash Ratio',
        'daysOfSalesOutstandingTTM': 'Days of Sales Outstanding',
        'daysOfInventoryOutstandingTTM': 'Days of Inventory Outstanding',
        'operatingCycleTTM': 'Operating Cycle',
        'daysOfPayablesOutstandingTTM': 'Days of Payables Outstanding',
        'cashConversionCycleTTM': 'Cash Conversion Cycle',
        'grossProfitMarginTTM': 'Gross Profit Margin',
        'operatingProfitMarginTTM': 'Operating Profit Margin',
        'pretaxProfitMarginTTM': 'Pretax Profit Margin',
        'netProfitMarginTTM': 'Net Profit Margin',
        'effectiveTaxRateTTM': 'Effective Tax Rate',
        'returnOnAssetsTTM': 'Return on Assets',
        'returnOnEquityTTM': 'Return on Equity',
        'returnOnCapitalEmployedTTM': 'Return on Capital Employed',
        'netIncomePerEBTTTM': 'Net Income per EBT',
        'ebtPerEbitTTM': 'EBT per EBIT',
        'ebitPerRevenueTTM': 'EBIT per Revenue',
        'debtRatioTTM': 'Debt Ratio',
        'debtEquityRatioTTM': 'Debt-to-Equity Ratio',
        'longTermDebtToCapitalizationTTM': 'Long-term Debt to Capitalization',
        'totalDebtToCapitalizationTTM': 'Total Debt to Capitalization',
        'interestCoverageTTM': 'Interest Coverage',
        'cashFlowToDebtRatioTTM': 'Cash Flow to Debt Ratio',
        'companyEquityMultiplierTTM': 'Company Equity Multiplier',
        'receivablesTurnoverTTM': 'Receivables Turnover',
        'payablesTurnoverTTM': 'Payables Turnover',
        'inventoryTurnoverTTM': 'Inventory Turnover',
        'fixedAssetTurnoverTTM': 'Fixed Asset Turnover',
        'assetTurnoverTTM': 'Asset Turnover',
        'operatingCashFlowPerShareTTM': 'Operating Cash Flow per Share',
        'freeCashFlowPerShareTTM': 'Free Cash Flow per Share',
        'cashPerShareTTM': 'Cash per Share',
        'operatingCashFlowSalesRatioTTM': 'Operating Cash Flow Sales Ratio',
        'freeCashFlowOperatingCashFlowRatioTTM': 'Free Cash Flow Operating Cash Flow Ratio',
        'cashFlowCoverageRatiosTTM': 'Cash Flow Coverage Ratios',
        'shortTermCoverageRatiosTTM': 'Short Term Coverage Ratio',
        'capitalExpenditureCoverageRatioTTM': 'Capital Expenditure Coverage Ratio',
        'dividendPaidAndCapexCoverageRatioTTM': 'Dividend Paid and Capex Coverage Ratio',
        'priceBookValueRatioTTM': 'Price to Book Value Ratio',
        'priceToBookRatioTTM': 'Price to Book Ratio',
        'priceToSalesRatioTTM': 'Price to Sales Ratio',
        'priceEarningsRatioTTM': 'Price to Earnings Ratio',
        'priceToFreeCashFlowsRatioTTM': 'Price to Free Cash Flows Ratio',
        'priceToOperatingCashFlowsRatioTTM': 'Price to Operating Cash Flows Ratio',
        'priceCashFlowRatioTTM': 'Price Cash Flow Ratio',
        'priceEarningsToGrowthRatioTTM': 'Price Earnings to Growth Ratio',
        'priceSalesRatioTTM': 'Price Sales Ratio',
        'dividendYieldTTM': 'Dividend Yield',
        'enterpriseValueMultipleTTM': 'Enterprise Value Multiple',
        'priceFairValueTTM': 'Price Fair Value',
        'dividendPerShareTTM': 'Dividend Per Share'
    })

    df = df.rename(columns={0: ""}) # Rename column 0 to an empty string


    return df


def get_news_articles(ticker):
    url = 'https://financialmodelingprep.com/api/v3/stock_news'
    api_key = mainAPI
    params = {'tickers': ticker, 'apikey': api_key, 'page': 0}
    response = requests.get(url, params=params)
    news_data = response.json()
    return news_data




with st.sidebar:
    st.write('BG Dashboard - Case Study')
    chartType = st.radio(
        "Chart type",
        ("Line", "Candlestick")
    )

    dashType = st.selectbox("Switch dashboard", 
                            ('Main', 'News'))

    







if dashType == 'Main':

    st.title('BG - Market Dashboard')
    st.subheader('Enter a ticker')

    ticker = st.text_input('Enter a ticker', value='ACI')
    ticker = ticker.upper()


    buttonPressed = st.button('Run ticker')


    if buttonPressed:
        if ticker != "":
            st.success(f'Ticker found: {ticker}, loading please wait')
            incState, incomeStatementChart = incomeStatement(ticker)
            chart_data = chart_data(ticker)
            dcfData = dcf(ticker)
            tickerChart, tickerChartLine = tickerGraph(ticker)
            script = companyProfile(ticker)
            balanceSheet = balanceSheet(ticker)
            incomeStatement = incomeSatement(ticker)
            cfStatement = cfStatement(ticker)
            ratios = ttmratio(ticker)
            
            upside = round((((round((dcfData['DCF'][-1]),2) - round((dcfData['Price'][-1]),2))/round((dcfData['Price'][-1]),2))*100),2)

            curretStockPrice = round((dcfData['Price'][-1]),2)

            
            epsData = chart_data['eps']


            currenEPS = round(chart_data['eps'][0], 2)
            priorYearEPS = round(chart_data['eps'][1], 2)
            priorTwoEPS = round(chart_data['eps'][2], 2)

            yearOneMovement = round((((chart_data['eps'][0] - chart_data['eps'][1])/chart_data['eps'][1])*100),2)
            yearTwoMovement = round((((chart_data['eps'][1] - chart_data['eps'][2])/chart_data['eps'][2])*100),2)
            yearThreeMovement = round((((chart_data['eps'][2] - chart_data['eps'][3])/chart_data['eps'][3])*100),2)


            # MAIN SITE


            if chartType == 'Candlestick':
                st.plotly_chart(tickerChart, use_container_width=True)
            else:
                st.plotly_chart(tickerChartLine, use_container_width=True)


            st.divider()

            st.subheader('Company profile')
            with st.expander('Read'):
                st.write(script)

            st.divider()

            bsTab, isTab, cfTab = st.tabs(["Balance Sheet", "Income statement", "Cashflow statement"])

            with bsTab:
                st.subheader("Balance Sheet")
                st.dataframe(balanceSheet, use_container_width=True) 
    

            with isTab:
                st.subheader("Income statement")
                st.dataframe(incomeStatement, use_container_width=True) 


            with cfTab:
                st.subheader("Cashflow statement")
                st.dataframe(cfStatement, use_container_width=True) 

            st.divider()





            st.subheader('Ratios')
            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("PE Ratio", round(ratios.loc['PE Ratio'],2), delta=None)
            col2.metric("Current Ratio", round(ratios.loc['Current Ratio'],2), delta=None)
            col3.metric("Quick Ratio", round(ratios.loc['Quick Ratio'],2), delta=None)
            col4.metric("Price to Book Ratio", round(ratios.loc['Price to Book Ratio'],2), delta=None)
            col5.metric("Debt-to-Equity Ratio", round(ratios.loc['Debt-to-Equity Ratio'],2), delta=None)







            st.divider()

            st.subheader('TTM Ratios')
            st.dataframe(ratios, use_container_width=True)





            st.divider()




            co1, co2, co3 = st.columns(3)   
            co1.metric('DCF', round(dcfData['DCF'][-1],2), delta=None)
            co2.metric("Share Price", curretStockPrice, delta=None)
            co3.metric("Upside", f'{upside}%', delta=None)

            st.divider()


            st.subheader('EPS Movement')
            col1, col2, col3 = st.columns(3)

            col1.metric("Current Year EPS Movement", currenEPS, f'{yearOneMovement}%')
            col2.metric("Prior Year EPS Movement", priorYearEPS, f'{yearTwoMovement}%')
            col3.metric("2 Years Prior EPS Movement", priorTwoEPS, f'{yearThreeMovement}%')

            st.divider()

            st.plotly_chart(incomeStatementChart, use_container_width= True)


            col1, col2, col3 = st.columns(3)

            with col1:
                df = epsData
                fig = px.bar(df, x=df.index, y='eps', text_auto='.2s', title="EPS Growth")
                fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=True)
                fig.update_layout(yaxis={'visible': True, 'showticklabels': False})
                epsBarChart = fig
                st.plotly_chart(epsBarChart, use_container_width=True)


            with col2:
                ebitdaGrowth = chart_data['ebitda']
                fig = px.bar(ebitdaGrowth, x=df.index, y='ebitda', text_auto='.2s', title="Ebitda Growth")
                fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=True)
                fig.update_layout(yaxis={'visible': True, 'showticklabels': False})
                edbitdaChart = fig
                st.plotly_chart(edbitdaChart, use_container_width= True)

            
            with col3:
                revenueGrowth = chart_data['revenue']
                fig = px.bar(revenueGrowth, x=df.index, y='revenue', text_auto='.2s', title="Revenue Growth")
                fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=True)
                fig.update_layout(yaxis={'visible': True, 'showticklabels': False})
                revenueChart = fig
                st.plotly_chart(revenueChart, use_container_width= True)


            st.divider()

if dashType == 'News':

    st.title('BG - News Dashboard')
    st.subheader('Enter a ticker')

    ticker = st.text_input('Enter a ticker', value='ACI')
    ticker = ticker.upper()


    buttonPressed = st.button('View the news')

    
    news_data = get_news_articles(ticker)

    if news_data:
        # Display news articles
        for article in news_data:
            st.write('## ' + article['title'])
            st.write(article['text'])
            st.write('Link: ' + article['url'])
            st.write('Published on ' + article['publishedDate'])
            st.write('---')

