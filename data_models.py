"""
Data models and generators for life insurance premium forecasting.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class PolicyType(str, Enum):
    TERM = "Term Life"
    WHOLE_LIFE = "Whole Life"


class Group(str, Enum):
    INDIVIDUAL = "Individual"
    FAMILY = "Family"
    CORPORATE = "Corporate"


class SmokingStatus(str, Enum):
    SMOKER = "Smoker"
    NON_SMOKER = "Non-Smoker"


@dataclass
class MortalityData:
    """Mortality rate data structure"""
    age: int
    gender: Gender
    country: str
    mortality_rate: float  # per 1000
    life_expectancy: float  # years
    year: int


@dataclass
class EconomicData:
    """Economic indicators data structure"""
    year: int
    country: str
    inflation_rate: float  # percentage
    interest_rate: float  # percentage
    gdp_growth: float  # percentage


@dataclass
class PremiumData:
    """Premium data structure"""
    age: int
    gender: Gender
    country: str
    policy_type: PolicyType
    base_premium: float
    year: int

# DataGenerator class removed - data is now loaded from CSV files
# Use create_data_csvs.py to generate CSV data files in the data/ directory
