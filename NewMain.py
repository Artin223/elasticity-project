import pandas as pd
import os
from dotenv import load_dotenv
from fredapi import Fred
import numpy 
import scipy.stats
import scipy.optimize
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

def calcRevenue(price, demandLine):
    revenue = price * (demandLine.intercept + (demandLine.slope * price))
    return revenue

def revenueForOptimizer(price, demandLine):
    return -(calcRevenue(price, demandLine))

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
sampleSize = len(CleanPriceSeries)

loggedPriceSeries = numpy.log(CleanPriceSeries)
loggedDemandSeries = numpy.log(CleanDemandSeries)

elasticityLine = scipy.stats.linregress(loggedPriceSeries, loggedDemandSeries)
demandLine = scipy.stats.linregress(CleanPriceSeries, CleanDemandSeries)

elasticity = elasticityLine.slope
standardOfError = elasticityLine.stderr
criticalValues = scipy.stats.t.ppf(0.975, (sampleSize - 2))

marginOfError = standardOfError * criticalValues
# upperBound = elasticity + marginOfError
# lowerBound = elasticity - marginOfError

print(f"{IDChoice}'s elasticity is {round(elasticity, 2)} with a +- {round(marginOfError, 2)} margin of error")
print(demandLine.slope, demandLine.intercept)
optimizedResult = scipy.optimize.minimize_scalar(revenueForOptimizer, args = (demandLine, ), bounds = (0, (-demandLine.intercept)/(demandLine.slope)))
optimizedPrice = optimizedResult.x
print(optimizedPrice)