import pandas as pd
import os
from dotenv import load_dotenv
from fredapi import Fred
load_dotenv("APIFredKey.env")
FredAPIKey= os.getenv("APIFredKey")
FredReady = Fred(api_key=FredAPIKey)

IDChoice = input("Enter your object of interest: ")

