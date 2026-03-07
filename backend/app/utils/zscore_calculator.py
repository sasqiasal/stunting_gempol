"""
Z-Score Calculator berdasarkan Standar WHO 2006/2007
Menghitung Z-Score untuk Berat Badan/Usia (BB/U) dan Tinggi Badan/Usia (TB/U)

Menggunakan metode LMS (Lambda-Mu-Sigma):
Z = ((value/M)^L - 1) / (L * S)

Referensi: WHO Child Growth Standards
"""

import numpy as np
from typing import Literal, Tuple

# Data standar WHO untuk BB/U (Berat Badan per Usia) dalam bulan 0-60
# Format: {usia_bulan: {"L": L, "M": M, "S": S}}

WHO_WFA_BOYS = {
    0: {"L": 0.3487, "M": 3.3464, "S": 0.14602},
    1: {"L": 0.2297, "M": 4.4709, "S": 0.13395},
    2: {"L": 0.1970, "M": 5.5675, "S": 0.12385},
    3: {"L": 0.1738, "M": 6.3762, "S": 0.11727},
    4: {"L": 0.1553, "M": 7.0023, "S": 0.11316},
    5: {"L": 0.1395, "M": 7.5105, "S": 0.11080},
    6: {"L": 0.1257, "M": 7.9340, "S": 0.10958},
    12: {"L": 0.0449, "M": 9.6479, "S": 0.10930},
    18: {"L": -0.0131, "M": 10.9049, "S": 0.11035},
    24: {"L": -0.0604, "M": 12.0458, "S": 0.11327},
    36: {"L": -0.1349, "M": 14.0196, "S": 0.12158},
    48: {"L": -0.1845, "M": 15.7517, "S": 0.13032},
    60: {"L": -0.2176, "M": 17.4182, "S": 0.13647},
}

WHO_WFA_GIRLS = {
    0: {"L": 0.3809, "M": 3.2322, "S": 0.14171},
    1: {"L": 0.1714, "M": 4.1873, "S": 0.13724},
    2: {"L": 0.0962, "M": 5.1282, "S": 0.13000},
    3: {"L": 0.0402, "M": 5.8458, "S": 0.12619},
    4: {"L": -0.0050, "M": 6.4237, "S": 0.12402},
    5: {"L": -0.0430, "M": 6.8985, "S": 0.12274},
    6: {"L": -0.0756, "M": 7.2970, "S": 0.12204},
    12: {"L": -0.1749, "M": 8.9481, "S": 0.12137},
    18: {"L": -0.2267, "M": 10.2297, "S": 0.12306},
    24: {"L": -0.2612, "M": 11.3479, "S": 0.12626},
    36: {"L": -0.3071, "M": 13.2737, "S": 0.13573},
    48: {"L": -0.3306, "M": 14.9462, "S": 0.14522},
    60: {"L": -0.3449, "M": 16.6380, "S": 0.15251},
}

# Data standar WHO untuk TB/U (Tinggi Badan per Usia) dalam bulan 0-60
WHO_HFA_BOYS = {
    0: {"L": 1, "M": 49.8842, "S": 0.03795},
    1: {"L": 1, "M": 54.7244, "S": 0.03557},
    2: {"L": 1, "M": 58.4249, "S": 0.03424},
    3: {"L": 1, "M": 61.4292, "S": 0.03328},
    4: {"L": 1, "M": 63.8856, "S": 0.03257},
    5: {"L": 1, "M": 65.9026, "S": 0.03199},
    6: {"L": 1, "M": 67.6236, "S": 0.03145},
    12: {"L": 1, "M": 75.7488, "S": 0.02950},
    18: {"L": 1, "M": 82.2988, "S": 0.02854},
    24: {"L": 1, "M": 87.0756, "S": 0.02807},
    36: {"L": 1, "M": 95.7790, "S": 0.02806},
    48: {"L": 1, "M": 103.0282, "S": 0.02881},
    60: {"L": 1, "M": 109.1732, "S": 0.02992},
}

WHO_HFA_GIRLS = {
    0: {"L": 1, "M": 49.1477, "S": 0.03790},
    1: {"L": 1, "M": 53.6872, "S": 0.03612},
    2: {"L": 1, "M": 57.0673, "S": 0.03476},
    3: {"L": 1, "M": 59.8029, "S": 0.03379},
    4: {"L": 1, "M": 62.0899, "S": 0.03306},
    5: {"L": 1, "M": 63.9977, "S": 0.03251},
    6: {"L": 1, "M": 65.7311, "S": 0.03202},
    12: {"L": 1, "M": 74.0157, "S": 0.03000},
    18: {"L": 1, "M": 80.7002, "S": 0.02919},
    24: {"L": 1, "M": 85.7163, "S": 0.02890},
    36: {"L": 1, "M": 94.5348, "S": 0.02908},
    48: {"L": 1, "M": 101.6226, "S": 0.02999},
    60: {"L": 1, "M": 107.8628, "S": 0.03119},
}

def interpolate_lms(age_months: int, reference_data: dict) -> Tuple[float, float, float]:
    """
    Interpolasi linear untuk mendapatkan nilai L, M, S pada usia tertentu
    
    Args:
        age_months: Usia dalam bulan
        reference_data: Data referensi WHO (WFA atau HFA)
    
    Returns:
        Tuple (L, M, S)
    """
    # Jika data tersedia langsung
    if age_months in reference_data:
        data = reference_data[age_months]
        return data["L"], data["M"], data["S"]
    
    # Cari dua titik terdekat untuk interpolasi
    ages = sorted(reference_data.keys())
    
    # Jika di bawah range minimum
    if age_months < ages[0]:
        data = reference_data[ages[0]]
        return data["L"], data["M"], data["S"]
    
    # Jika di atas range maksimum
    if age_months > ages[-1]:
        data = reference_data[ages[-1]]
        return data["L"], data["M"], data["S"]
    
    # Interpolasi linear
    for i in range(len(ages) - 1):
        if ages[i] <= age_months <= ages[i + 1]:
            age1, age2 = ages[i], ages[i + 1]
            data1, data2 = reference_data[age1], reference_data[age2]
            
            # Proporsi
            t = (age_months - age1) / (age2 - age1)
            
            # Interpolasi untuk L, M, S
            L = data1["L"] + t * (data2["L"] - data1["L"])
            M = data1["M"] + t * (data2["M"] - data1["M"])
            S = data1["S"] + t * (data2["S"] - data1["S"])
            
            return L, M, S
    
    # Fallback (seharusnya tidak pernah tercapai)
    data = reference_data[ages[0]]
    return data["L"], data["M"], data["S"]

def calculate_zscore_lms(value: float, L: float, M: float, S: float) -> float:
    """
    Menghitung Z-Score menggunakan metode LMS
    
    Formula: Z = ((value/M)^L - 1) / (L * S)
    
    Args:
        value: Nilai pengukuran (berat atau tinggi)
        L: Parameter L dari WHO
        M: Parameter M dari WHO (median)
        S: Parameter S dari WHO (coefficient of variation)
    
    Returns:
        Z-Score
    """
    if L == 0:
        # Jika L = 0, gunakan formula alternatif
        z_score = np.log(value / M) / S
    else:
        z_score = (np.power(value / M, L) - 1) / (L * S)
    
    return round(z_score, 2)

def calculate_zscore_bbu(
    berat_badan: float,
    usia_bulan: int,
    jenis_kelamin: Literal["L", "P"]
) -> float:
    """
    Menghitung Z-Score Berat Badan/Usia (BB/U atau WFA - Weight-for-Age)
    
    Args:
        berat_badan: Berat badan dalam kg
        usia_bulan: Usia dalam bulan
        jenis_kelamin: "L" untuk laki-laki, "P" untuk perempuan
    
    Returns:
        Z-Score BB/U
    """
    # Pilih data referensi berdasarkan jenis kelamin
    reference_data = WHO_WFA_BOYS if jenis_kelamin == "L" else WHO_WFA_GIRLS
    
    # Dapatkan nilai L, M, S
    L, M, S = interpolate_lms(usia_bulan, reference_data)
    
    # Hitung Z-Score
    return calculate_zscore_lms(berat_badan, L, M, S)

def calculate_zscore_tbu(
    tinggi_badan: float,
    usia_bulan: int,
    jenis_kelamin: Literal["L", "P"]
) -> float:
    """
    Menghitung Z-Score Tinggi Badan/Usia (TB/U atau HFA - Height-for-Age)
    
    Args:
        tinggi_badan: Tinggi badan dalam cm
        usia_bulan: Usia dalam bulan
        jenis_kelamin: "L" untuk laki-laki, "P" untuk perempuan
    
    Returns:
        Z-Score TB/U
    """
    # Pilih data referensi berdasarkan jenis kelamin
    reference_data = WHO_HFA_BOYS if jenis_kelamin == "L" else WHO_HFA_GIRLS
    
    # Dapatkan nilai L, M, S
    L, M, S = interpolate_lms(usia_bulan, reference_data)
    
    # Hitung Z-Score
    return calculate_zscore_lms(tinggi_badan, L, M, S)

def determine_nutrition_status(zscore_bbu: float, zscore_tbu: float) -> str:
    """
    Menentukan status gizi berdasarkan Z-Score BB/U dan TB/U
    
    Klasifikasi:
    - Stunting: TB/U < -2 SD
    - Severely Stunted: TB/U < -3 SD
    - Wasting: BB/U < -2 SD
    - Severely Wasted: BB/U < -3 SD
    - Normal: -2 SD <= Z-Score <= 2 SD
    - Overweight: Z-Score > 2 SD
    
    Args:
        zscore_bbu: Z-Score Berat Badan/Usia
        zscore_tbu: Z-Score Tinggi Badan/Usia
    
    Returns:
        Status gizi
    """
    status_parts = []
    
    # Klasifikasi berdasarkan TB/U (Stunting)
    if zscore_tbu < -3:
        status_parts.append("Severely Stunted")
    elif zscore_tbu < -2:
        status_parts.append("Stunting")
    elif zscore_tbu > 2:
        status_parts.append("Tinggi")
    
    # Klasifikasi berdasarkan BB/U (Wasting/Underweight)
    if zscore_bbu < -3:
        status_parts.append("Severely Underweight")
    elif zscore_bbu < -2:
        status_parts.append("Underweight")
    elif zscore_bbu > 2:
        status_parts.append("Overweight")
    
    # Jika tidak ada masalah
    if not status_parts:
        return "Normal"
    
    return ", ".join(status_parts)

def is_stunting(zscore_tbu: float) -> bool:
    """
    Menentukan apakah balita mengalami stunting
    
    Args:
        zscore_tbu: Z-Score Tinggi Badan/Usia
    
    Returns:
        True jika stunting (TB/U < -2 SD), False jika tidak
    """
    return zscore_tbu < -2.0
