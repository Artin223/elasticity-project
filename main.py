
import pandas as pd
import os
from dotenv import load_dotenv
from fredapi import Fred
load_dotenv("APIFredKey.env")
FredAPIKey= os.getenv("APIFredKey")
FredActivate = Fred(api_key=FredAPIKey)

def to_monthly(series):
    FrequancyIndex = pd.infer_freq(series.index)
    if FrequancyIndex == "M" or FrequancyIndex == "MS":
        return series.resample("MS").mean()
    else:
        return series.resample("MS").ffill()

objectID = {
    "gas": {"price": "GASREGCOVM", "demand": "DNRGRA3M086SBEA"}, 
    "food": {"price": "CPIUFDNS", "demand": "DFXARA3M086SBEA"},
    "electricity": {"price": "APU000072610", "demand": "IPN22112RS"},
    "durables": {"price": "CUSR0000SAD","demand": "PCEDGC96"},
    "nondurables": {"price": "CUSR0000SAC","demand": "PCEND"},
    "services": {"price": "CUSR0000SAS","demand": "PCESC96"},
    "dining": {"price": "CUSR0000SEFV", "demand": "RSFSDP"},
    "apparel": {"price": "SUUR0000SAA", "demand": "RSCCASN"},
    "vehicles": {"price": "CUUR0000SETA01", "demand": "RSMVPD"},
    "furniture": {"price": "CUSR0000SAH3", "demand": "RSFHFS"},
    "alcohol": {"price": "CUSR0000SAF116", "demand": "MRTSSM4453USN"},
    "shelter": {"price": "CUSR0000SAH1", "demand": "HSN1F"},
    "health services": {"price": "CUSR0000SAM2", "demand": "USPCEHLTHCARE"},
    "retail trade": {"price": "CPIAUCSL", "demand": "RSXFS"},
    "medical goods": {"price": "CUSR0000SAM1", "demand": "RSHPCS"},
    "recreational goods": {"price": "CPIRECSL","demand": "MRTSSM451USN"},
    "education services": {"price": "CUSR0000SAE1","demand": "USEDCATNQGSP"}
}
while True:
    try:
        IDChoice = input("Enter your object of interest: ").strip().lower() 
        #also do supply elasticity of workers
        PriceID = objectID[IDChoice]["price"]
        DemandID = objectID[IDChoice]["demand"]
        break
    except KeyError:        
        print("Invalid input. Please enter a valid object of interest")
#end of while loop
PriceSeries = FredActivate.get_series(PriceID)
DemandSeries = FredActivate.get_series(DemandID)

MonthlyPriceSeries = to_monthly(PriceSeries)
MonthlyDemandSeries = to_monthly(DemandSeries)
while True:
    try:
        StartTimeChoice = input('Enter desired start time as YYYY-MM or enter "latest" for latest avaible date: ').strip().lower()
        if StartTimeChoice != "latest":
            EndTimeChoice = input("Enter desired end time as YYYY-MM: ")
        if StartTimeChoice != "latest":
                Price1 = MonthlyPriceSeries.loc[StartTimeChoice]
                Price2 = MonthlyPriceSeries.loc[EndTimeChoice]
                Demand1 = MonthlyDemandSeries.loc[StartTimeChoice]
                Demand2 = MonthlyDemandSeries.loc[EndTimeChoice]         
                
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
