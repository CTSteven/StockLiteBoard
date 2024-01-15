from django.db import models

# Create your models here.
# models.py
from dataclasses import dataclass
import pandas as pd

@dataclass
class FinancialReportData:
    """
    Represents a summary of financial reports.
    """
    financial_report: pd.DataFrame
    financial_info: pd.DataFrame
    financial_warning_list: list
    

@dataclass
class StockPriceHistoryData:
    """
    Represents a summary of stock price history.
    """
    stock_price_history: pd.DataFrame
    yearly_stock_price: pd.DataFrame
