import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from fredapi import Fred
import numpy as np
import scipy.stats
import scipy.optimize
 
 
try:
    FredAPIKey = st.secrets["FRED_API_KEY"]
except Exception:
    load_dotenv("APIFredKey.env")
    FredAPIKey = os.getenv("APIFredKey")
 
FredActivate = Fred(api_key=FredAPIKey)
 
 
def ToMonthly(series):
    FrequencyIndex = pd.infer_freq(series.index)
    if FrequencyIndex is not None:
        if FrequencyIndex == "M" or FrequencyIndex == "MS":
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
 
 
def CalcRevenue(price, slope, intercept):
    return price * (intercept + slope * price)
 
 
def RevenueForOptimizer(price, slope, intercept):
    return -CalcRevenue(price, slope, intercept)
 
 
def ConfidenceInterval(RegressionLine, SampleSize):
    DegreesOfFreedom = SampleSize - 2
    CriticalValue = scipy.stats.t.ppf(0.975, DegreesOfFreedom)
    Margin = RegressionLine.stderr * CriticalValue
    return RegressionLine.slope, Margin
 
 
objectID = {
    "gas": {"price": "GASREGCOVM", "demand": "DNRGRA3M086SBEA"},
    "food": {"price": "CPIUFDNS", "demand": "DFXARA3M086SBEA"},
    "electricity": {"price": "APU000072610", "demand": "IPN22112RS"},
    "durables": {"price": "CUSR0000SAD", "demand": "PCEDGC96"},
    "nondurables": {"price": "CUSR0000SAC", "demand": "PCENDC96"},
    "services": {"price": "CUSR0000SAS", "demand": "PCESC96"},
    "dining": {"price": "CUSR0000SEFV", "demand": "RSFSDP"},
    "apparel": {"price": "SUUR0000SAA", "demand": "RSCCASN"},
    "vehicles": {"price": "CUUR0000SETA01", "demand": "RSMVPD"},
    "furniture": {"price": "CUSR0000SAH3", "demand": "RSFHFS"},
    "alcohol": {"price": "CUSR0000SAF116", "demand": "MRTSSM4453USN"},
    "shelter": {"price": "CUSR0000SAH1", "demand": "HSN1F"},
    "health services": {"price": "CPIMEDSL", "demand": "DHLCRX1Q020SBEA"},
    "retail trade": {"price": "CPIAUCSL", "demand": "RSXFS"},
    "medical goods": {"price": "CUSR0000SAM1", "demand": "RSHPCS"},
    "recreational goods": {"price": "CPIRECSL", "demand": "MRTSSM451USN"},
    "education services": {"price": "CUSR0000SAE1", "demand": "USEDCATNQGSP"},
}
 
st.title("Real-Time Price Elasticity Index")
st.caption("Live data from the Federal Reserve Economic Data (FRED) API.")
 
IDChoice = st.selectbox("Select your object of interest:", list(objectID.keys()))
 
TwoPointTab, RegressionTab = st.tabs(["Two-point elasticity", "Full regression analysis"])
 
with TwoPointTab:
    st.write("Compute elasticity between two specific dates, using the arc (midpoint) elasticity formula.")
 
    UseLatest = st.checkbox("Use latest available year-over-year data")
 
    if UseLatest:
        StartTimeChoice = "latest"
        EndTimeChoice = "latest"
    else:
        StartTimeChoice = st.text_input("Enter Start Date (YYYY-MM):")
        EndTimeChoice = st.text_input("Enter End Date (YYYY-MM):")
 
    if st.button("Calculate", key="two_point_calc"):
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
                Price1 = GetSingleValue(MonthlyPriceSeries.loc[StartTimeChoice])
                Price2 = GetSingleValue(MonthlyPriceSeries.loc[EndTimeChoice])
                Demand1 = GetSingleValue(MonthlyDemandSeries.loc[StartTimeChoice])
                Demand2 = GetSingleValue(MonthlyDemandSeries.loc[EndTimeChoice])
            else:
                Price1 = MonthlyPriceSeries.iloc[-13]
                Price2 = MonthlyPriceSeries.iloc[-1]
                Demand1 = MonthlyDemandSeries.iloc[-13]
                Demand2 = MonthlyDemandSeries.iloc[-1]
 
            PriceElasticity = ((Demand2 - Demand1) / (Demand2 + Demand1)) * ((Price2 + Price1) / (Price2 - Price1))
            PriceElasticity = round(abs(PriceElasticity), 2)
 
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
 
with RegressionTab:
    st.write("Fit a regression across the entire FRED history instead of just two dates, and search for the revenue-maximizing price.")
 
    if st.button("Run full analysis", key="full_analysis"):
        PriceID = objectID[IDChoice]["price"]
        DemandID = objectID[IDChoice]["demand"]
 
        PriceSeries = FredActivate.get_series(PriceID)
        DemandSeries = FredActivate.get_series(DemandID)
 
        MonthlyPriceSeries = ToMonthly(PriceSeries)
        MonthlyDemandSeries = ToMonthly(DemandSeries)
 
        AlignedSeries = pd.DataFrame({"price": MonthlyPriceSeries, "demand": MonthlyDemandSeries}).dropna()
        CleanPriceSeries = AlignedSeries["price"]
        CleanDemandSeries = AlignedSeries["demand"]
        SampleSize = len(CleanPriceSeries)
 
        if SampleSize < 10:
            st.error(f"Not enough overlapping monthly data for {IDChoice} to run a regression.")
            st.stop()
 
        LoggedPriceSeries = np.log(CleanPriceSeries)
        LoggedDemandSeries = np.log(CleanDemandSeries)
 
        
        RawElasticityLine = scipy.stats.linregress(LoggedPriceSeries, LoggedDemandSeries)
        RawSlope, RawMargin = ConfidenceInterval(RawElasticityLine, SampleSize)
 
        
        DiffLoggedPriceSeries = LoggedPriceSeries.diff().dropna()
        DiffLoggedDemandSeries = LoggedDemandSeries.diff().dropna()
        TrendCorrectedLine = scipy.stats.linregress(DiffLoggedPriceSeries, DiffLoggedDemandSeries)
        TrendSlope, TrendMargin = ConfidenceInterval(TrendCorrectedLine, len(DiffLoggedPriceSeries))
 
        st.subheader("Elasticity: two approaches")
        Col1, Col2 = st.columns(2)
        with Col1:
            st.metric("Raw levels regression", f"{RawSlope:.2f}", f"± {RawMargin:.2f}")
            st.caption("Fit on raw price/demand history. Can be biased by shared trends (inflation, growth) unrelated to real price sensitivity.")
        with Col2:
            st.metric("Trend-corrected (differenced)", f"{TrendSlope:.2f}", f"± {TrendMargin:.2f}")
            st.caption("Fit on month-to-month percent changes. Removes shared-trend bias, at the cost of a wider, noisier interval.")
 
        st.info(
            "These two numbers can disagree because of a statistical tradeoff. the raw regression is "
            "biased but precise, and the differenced version is unbiased but with a higher margin of error."
        )
 
        # Revenue-maximizing price, built on a differenced (trend-corrected) demand curve
        DiffPriceSeries = CleanPriceSeries.diff().dropna()
        DiffDemandSeries = CleanDemandSeries.diff().dropna()
        DemandLine = scipy.stats.linregress(DiffPriceSeries, DiffDemandSeries)
        DemandSlope = DemandLine.slope
        DemandIntercept = CleanDemandSeries.mean() - (DemandSlope * CleanPriceSeries.mean())
 
        st.subheader("Revenue-maximizing price")
 
        if DemandSlope >= 0 or DemandIntercept <= 0:
            st.warning(
                f"The fitted demand curve for **{IDChoice}** doesn't behave like a normal downward-sloping "
                "curve, so a revenue-maximizing price can't be reliably computed here."
            )
        else:
            ChokePrice = -DemandIntercept / DemandSlope
            OptimizerResult = scipy.optimize.minimize_scalar(
                RevenueForOptimizer,
                args=(DemandSlope, DemandIntercept),
                bounds=(0, ChokePrice),
                method="bounded",
            )
            OptimizedPrice = OptimizerResult.x
            MaxRevenue = CalcRevenue(OptimizedPrice, DemandSlope, DemandIntercept)
 
            Col3, Col4 = st.columns(2)
            with Col3:
                st.metric("Optimal price", f"{OptimizedPrice:.2f}")
            with Col4:
                st.metric("Choke price (demand hits 0)", f"{ChokePrice:.2f}")
            st.caption(
                f"Estimated revenue at this price: {MaxRevenue:.2f}. Units match the underlying FRED series, "
                "not real-world dollars. This is what a straight-line demand model implies, not a guaranteed "
                "real-world profit-maximizing price."
            )
 
st.markdown("---")
st.caption("*Data is dynamically sourced from the Federal Reserve Economic Data (FRED) API.*")