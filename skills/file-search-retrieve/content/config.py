# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "file_meta.db")
INDEX_DIR = os.path.join(BASE_DIR, "data", "index")
CONTENT_MAX_LENGTH = 5000

HOST = "127.0.0.1"
PORT = 5050
DEFAULT_PAGE = 1
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
HOT_TAGS_LIMIT = 20

CATEGORIES = {
    "A_General-Management": {"A01": "General-Affairs", "A02": "Admin-Services"},
    "B_HR-Management": {"B01": "Org-Structure", "B02": "Personnel"},
    "C_Strategic-Planning": {"C01": "Five-Year-Plan", "C02": "Reform", "C03": "Strategic-Cooperation"},
    "D_Finance": {"D01": "Budget", "D02": "Treasury", "D03": "Asset-Management"},
    "E_Compliance-Risk": {"E01": "Risk-Management", "E02": "Internal-Audit", "E03": "Compliance"},
    "F_IT": {"F01": "IT-Planning", "F02": "System-Development"},
}

CATEGORY_CODES = {}
for cat1, cat2_dict in CATEGORIES.items():
    for cat2_code, cat2_name in cat2_dict.items():
        CATEGORY_CODES[cat2_code] = {"category1": cat1, "category2": cat2_code, "category_name": cat2_name}
