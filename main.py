
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
    "electricity": {"price": "APU000072610", "demand": "DNRERA3M086SBEA"},
    "durables": {"price": "CUSR0000SAD","demand": "PCEDGC96"},
    "nondurables": {"price": "CUSR0000SAC","demand": "PCNDC96"},
    "services": {"price": "CUSR0000SAS","demand": "PCESC96"},
    "dining": {"price": "CUSR0000SEFV", "demand": "RSFSDP"},
    "apparel": {"price": "CUSR0000SAA", "demand": "RSAPPFS"},
    "vehicles": {"price": "CUUR0000SETA01", "demand": "RSMVDFED"},
    "furniture": {"price": "CUSR0000SEHG", "demand": "RSFHFS"},
    "alcohol": {"price": "CUSR0000SAF116", "demand": "RSBDFS"}
}
while True:
    try:
        IDChoice = input("Enter your object of interest: ").strip().lower() 
        #also do supply elasticity of workers
        PriceID = objectID[IDChoice]["price"]
        DemandID = objectID[IDChoice]["demand"]
        break
    except KeyError:        
        print("Invalid input. Please enter a valid object of interest from the list: gas, food, electricity, durables, nondurables, services, dining, apparel, vehicles, furniture, alcohol.")
#end of while loop
PriceSeries = FredActivate.get_series(PriceID)
DemandSeries = FredActivate.get_series(DemandID)

MonthlyPriceSeries = PriceSeries.resample('MS').mean()
MonthlyDemandSeries = DemandSeries.resample('MS').mean()
while True:
    try:
        StartTimeChoice = input('Enter desired start time as YYYY-MM or enter "latest" for latest avaible date: ').strip().lower()
        if StartTimeChoice != "latest":
            EndTimeChoice = input("Enter desired end time as YYYY-MM: ")
        if StartTimeChoice != "latest":
                Price1 = MonthlyPriceSeries.loc[StartTimeChoice].iloc[0]
                Price2 = MonthlyPriceSeries.loc[EndTimeChoice].iloc[0]
                Demand1 = MonthlyDemandSeries.loc[StartTimeChoice].iloc[0]
                Demand2 = MonthlyDemandSeries.loc[EndTimeChoice].iloc[0]
                print(f"Price1: {Price1}, Price2: {Price2}, Demand1: {Demand1}, Demand2: {Demand2}")
                
        else:
                Price1 = MonthlyPriceSeries.iloc[-2]
                Price2 = MonthlyPriceSeries.iloc[-1]
                Demand1 = MonthlyDemandSeries.iloc[-2]
                Demand2 = MonthlyDemandSeries.iloc[-1]
        break
    except KeyError:
            print("Invalid date format or date not available. Please enter dates in YYYY-MM format and ensure they are within the available range.")
            
#end of while loop
PriceElasticity = ((Demand2-Demand1)/Demand1) / ((Price2-Price1)/Price1)
PriceElasticity = abs(PriceElasticity)
PriceElasticity = round(PriceElasticity, 2)
print(f"The price elasticity of {IDChoice} is: {PriceElasticity}")

if PriceElasticity > 1:
    print(f"{IDChoice} is elastic, meaning that a change in price changes demand greatly.")
else:
    print(f"{IDChoice} is not elastic, meaning that a change in price does not change demand significantly.")
