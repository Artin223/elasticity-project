import pandas as pd
import os
from dotenv import load_dotenv
from fredapi import Fred
load_dotenv("APIFredKey.env")
FredAPIKey= os.getenv("APIFredKey")
FredReady = Fred(api_key=FredAPIKey)

objectID = {
    "gas": {"price": "GASREGW", "demand": "DNRGRA3M086SBEA"},
    "food": {"price": "CPIUFDNS", "demand": "DFXARA3M086SBEA"},
    "electricity": {"price": "APU000072610", "demand": "DNRERA3M086SBEA"}
}

IDChoice = input("Enter your object of interest: ") 
IDChoice = IDChoice.strip().lower()