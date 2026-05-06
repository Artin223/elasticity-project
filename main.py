import pandas as pd
import os
from dotenv import load_dotenv
from fredapi import Fred
load_dotenv("APIFredKey.env")
FredAPIKey= os.getenv("APIFredKey")
FredActivate = Fred(api_key=FredAPIKey)

objectID = {
    "gas": {"price": "GASREGW", "demand": "DNRGRA3M086SBEA"}, 
    "food": {"price": "CPIUFDNS", "demand": "DFXARA3M086SBEA"},
    "electricity": {"price": "APU000072610", "demand": "DNRERA3M086SBEA"}
}
 
IDChoice = input("Enter your object of interest: ").strip().lower() 
StartTimeChoice = input('Enter desired start time as YYYY-MM or enter "latest" for latest avaible date: ').strip().lower()
if StartTimeChoice != "latest":
    EndTimeChoice = input("Enter desired end time as YYYY-MM: ")

#also do supply elasticity of workers
PriceID = objectID[IDChoice]["price"]
DemandID = objectID[IDChoice]["demand"]

PriceSeries = FredActivate.get_series(PriceID)
DemandSeries = FredActivate.get_series(DemandID)

MonthlyPriceSeries = PriceSeries.resample('MS').mean()
MonthlyDemandSeries = DemandSeries.resample('MS').mean()

if StartTimeChoice != "latest":
    Price1 = MonthlyPriceSeries.loc[StartTimeChoice].iloc[0]
    Price2 = MonthlyPriceSeries.loc[EndTimeChoice].iloc[0]
    Demand1 = MonthlyDemandSeries.loc[StartTimeChoice].iloc[0]
    Demand2 = MonthlyDemandSeries.loc[EndTimeChoice].iloc[0]
else:
    Price1 = MonthlyPriceSeries.iloc[-2]
    Price2 = MonthlyPriceSeries.iloc[-1]
    Demand1 = MonthlyDemandSeries.iloc[-2]
    Demand2 = MonthlyDemandSeries.iloc[-1]

PriceElasticity = ((Demand2 - Demand1) / Demand1) / ((Price2 - Price1) / Price1)
PriceElasticity = abs(PriceElasticity)
PriceElasticity = round(PriceElasticity, 2)
print(f"The price elasticity of {IDChoice} is: {PriceElasticity}")
