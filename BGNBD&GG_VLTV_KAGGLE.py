##############################################################
# CLTV Prediction wtih BG-NBD ve Gamma-Gamma models
##############################################################

# 1. (Data Preperation)
# 2. Expected Sales Forecasting with BG-NBD Model
# 3. Expected Average Profit with Gamma-Gamma Modeli
# 4. Calculation of CLTV with BG-NBD and Gamma-Gamma Model
# 5. Creating Segments by CLTV
# 6. Functionalization of work
# 7. Submitting Results to Database

# CLTV = (Customer_Value / Churn_Rate) x Profit_margin.
# Customer_Value = Average_Order_Value * Purchase_Frequency



# Necessary libraries and Functions

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import  plot_period_transactions

pd.set_option("display.max_columns", None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.4f' % x)
from sklearn.preprocessing import MinMaxScaler

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    lower_limit = quartile1 - 1.5 * interquantile_range
    return lower_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

df_ = pd.read_excel("Hafta_03/Ödevler/online_retail_II.xlsx", sheet_name="Year 2010-2011")

df = df_.copy()

df.shape
df.info()
df.head()

##############################################################
# 1. DATA PREPERATION
##############################################################

df.describe().T
df.dropna(inplace=True)
df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

replace_with_thresholds(df, "Quantity")
replace_with_thresholds(df, "Price")

df.describe().T

df["Total_Price"] = df["Quantity"] * df["Price"]

today_date = dt.datetime(2011,12,11)
df["InvoiceDate"].max()

# Preperation of Lifetime dataset

# Recency: Time since last purchase. Weekly.
# T: How long before the analysis date was the first purchase made. Weekly.
# Frequency: total number of repeat purchases
# monetary_value: average earnings per purchase

def cltv_df_maker(df,country):


cltv = df.groupby(["Customer ID", "Country"]).agg({"InvoiceDate" : [lambda date: (date.max() - date.min()).days,
                                                                 lambda date: (today_date - date.min()).days],
                                                "Invoice" : lambda num: num.nunique(),
                                                "Total_Price" : lambda price: price.sum()})

cltv.columns = ["recency", "T", "frequency", "monetary"]

cltv["monetary"] = cltv["monetary"] / cltv["frequency"]

cltv = cltv[cltv["frequency"] > 1]
cltv = cltv[cltv["monetary"] > 0]
cltv["recency"] = cltv["recency"] / 7 # to make it weekly.
cltv["T"] = cltv["T"] / 7 # to make it weekly.



# Establishment of BG-NBD Model

bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(frequency=cltv["fre"])

cltv[cltv.Country == "France"]["frequency"]
