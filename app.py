import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from fredapi import Fred


try:
    FredAPIKey = st.secrets["FRED_API_KEY"]
except:
    load_dotenv("APIFredKey.env")
    FredAPIKey = os.getenv("APIFredKey")

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

def GetSingleValue(RawData):
    if isinstance(RawData, pd.Series):
        return RawData.iloc[0]   
    else:
        return RawData

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

st.title("Real-Time Price Elasticity Index")


IDChoice = st.selectbox("Select your object of interest:", list(objectID.keys()))
UseLatest = st.checkbox("Use latest available Year-over-Year data")


if UseLatest:
    StartTimeChoice = "latest"
    EndTimeChoice = "latest" 
else:
    StartTimeChoice = st.text_input("Enter Start Date (YYYY-MM):")
    EndTimeChoice = st.text_input("Enter End Date (YYYY-MM):")


if st.button("Calculate"):
    
    PriceID = objectID[IDChoice]["price"]
    DemandID = objectID[IDChoice]["demand"]

    PriceSeries = FredActivate.get_series(PriceID)
    DemandSeries = FredActivate.get_series(DemandID)
    
    AlignedSeries = pd.DataFrame({"price": PriceSeries, "demand": DemandSeries}).dropna()
    CleanPriceSeries = AlignedSeries["price"]
    CleanDemandSeries = AlignedSeries["demand"]

    MonthlyPriceSeries = ToMonthly(CleanPriceSeries)
    MonthlyDemandSeries = ToMonthly(CleanDemandSeries)


    try:
        if StartTimeChoice != "latest":
            Price1 = MonthlyPriceSeries.loc[StartTimeChoice]
            Price2 = MonthlyPriceSeries.loc[EndTimeChoice]
            Demand1 = MonthlyDemandSeries.loc[StartTimeChoice]
            Demand2 = MonthlyDemandSeries.loc[EndTimeChoice] 
            Price1 = GetSingleValue(Price1)
            Price2 = GetSingleValue(Price2)
            Demand1 = GetSingleValue(Demand1)
            Demand2 = GetSingleValue(Demand2)        
        else:
            Price1 = MonthlyPriceSeries.iloc[-13]
            Price2 = MonthlyPriceSeries.iloc[-1]
            Demand1 = MonthlyDemandSeries.iloc[-13]
            Demand2 = MonthlyDemandSeries.iloc[-1]

        
        PriceElasticity = ((Demand2 - Demand1) / (Demand2 + Demand1)) * ((Price2 + Price1) / (Price2 - Price1))
        PriceElasticity = abs(PriceElasticity)
        PriceElasticity = round(PriceElasticity, 2)
        
        if pd.isna(PriceElasticity):
            st.error(f"Could not calculate elasticity. Data for **{IDChoice}** might not be available for both selected months.")
            st.stop() 
        
        st.write(f"The price elasticity of {IDChoice} is: **{PriceElasticity}**")

        if PriceElasticity > 1:
            st.write(f"{IDChoice.title()} is elastic, meaning that a change in price changes demand greatly.")
        else:
            st.write(f"{IDChoice.title()} is not elastic, meaning that a change in price does not change demand significantly.")

    except KeyError:
        st.write("Error: Invalid date format or date not available. Please check your dates and try again.")

st.markdown("---")
st.caption("*Data is dynamically sourced from the Federal Reserve Economic Data (FRED) API.*")