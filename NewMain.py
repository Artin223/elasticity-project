import pandas as pd
import os
from dotenv import load_dotenv
from fredapi import Fred
import numpy 
import scipy.stats
load_dotenv("APIFredKey.env")
FredAPIKey= os.getenv("APIFredKey")
FredActivate = Fred(api_key=FredAPIKey)

def ToMonthly(series):
    FrequancyIndex = pd.infer_freq(series.index)
    if FrequancyIndex is not None:
        if FrequancyIndex == "M" or FrequancyIndex == "MS":
            return series.resample("MS").mean()
        else:
            return series.resample("MS").ffill()
    else:
        return series.resample("MS").ffill()


objectID = {
    "gas": {"price": "GASREGCOVM", "demand": "DNRGRA3M086SBEA"}, 
    "food": {"price": "CPIUFDNS", "demand": "DFXARA3M086SBEA"},
    "electricity": {"price": "APU000072610", "demand": "IPN22112RS"},
    "durables": {"price": "CUSR0000SAD","demand": "PCEDGC96"},
    "nondurables": {"price": "CUSR0000SAC","demand": "PCENDC96"},
    "services": {"price": "CUSR0000SAS","demand": "PCESC96"},
    "dining": {"price": "CUSR0000SEFV", "demand": "RSFSDP"},
    "apparel": {"price": "SUUR0000SAA", "demand": "RSCCASN"},
    "vehicles": {"price": "CUUR0000SETA01", "demand": "RSMVPD"},
    "furniture": {"price": "CUSR0000SAH3", "demand": "RSFHFS"},
    "alcohol": {"price": "CUSR0000SAF116", "demand": "MRTSSM4453USN"},
    "shelter": {"price": "CUSR0000SAH1", "demand": "HSN1F"},
    "health services": {"price": "CPIMEDSL", "demand": "DHLCRX1Q020SBEA"},
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

PriceSeries = FredActivate.get_series(PriceID)
DemandSeries = FredActivate.get_series(DemandID)

MonthlyPriceSeries = ToMonthly(PriceSeries)
MonthlyDemandSeries = ToMonthly(DemandSeries)

AlignedSeries = pd.DataFrame({"price": MonthlyPriceSeries, "demand": MonthlyDemandSeries}).dropna()
CleanPriceSeries = AlignedSeries["price"]
CleanDemandSeries = AlignedSeries["demand"]

loggedPriceSeries = numpy.log(CleanPriceSeries)
loggedDemandSeries = numpy.log(CleanDemandSeries)
print(loggedPriceSeries)
ElasticityLine = scipy.stats.linregress(loggedPriceSeries, loggedDemandSeries)
