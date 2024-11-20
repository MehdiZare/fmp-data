import logging

from dotenv import load_dotenv

from fmp_data.client import FMPDataClient
from fmp_data.logger import FMPLogger

load_dotenv()

timeout = 20

###
client = FMPDataClient.from_env(debug=False)

FMPLogger().get_logger().setLevel(logging.DEBUG)

# Get company profile
# profile = client.company.get_profile(symbol="AAPL")

# Search companies
# results = client.company.search(query="Apple", limit=5)

dates = client.institutional.get_form_13f_dates("0001067983")

# Form13FDate(date="2022-01-01")
roster = client.institutional.get_insider_roster("AAPL")
trades = client.institutional.get_insider_trades("AAPL")
