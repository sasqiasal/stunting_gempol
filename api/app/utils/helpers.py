"""
Helper functions untuk kalkulasi usia dan tanggal
"""

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

def calculate_age_in_months(birth_date: date, measurement_date: date = None) -> int:
    """
    Menghitung usia dalam bulan berdasarkan tanggal lahir
    
    Args:
        birth_date: Tanggal lahir
        measurement_date: Tanggal pengukuran (default: hari ini)
    
    Returns:
        Usia dalam bulan
    """
    if measurement_date is None:
        measurement_date = date.today()
    
    # Hitung perbedaan
    delta = relativedelta(measurement_date, birth_date)
    
    # Total bulan
    total_months = delta.years * 12 + delta.months
    
    return total_months

def format_date_indonesia(date_obj: date) -> str:
    """
    Format tanggal ke format Indonesia (DD/MM/YYYY)
    
    Args:
        date_obj: Object date
    
    Returns:
        String tanggal format Indonesia
    """
    return date_obj.strftime("%d/%m/%Y")
