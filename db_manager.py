import requests
import time

# --- FIREBASE SETUP ---
FIREBASE_URL = "https://volleyball-auction-17228-default-rtdb.firebaseio.com/.json"
TOTAL_PURSE = 50000

# --- DEFAULT DATA ---
DEFAULT_USER_DATA = {"Masterji": {"password": "Mishraji041411", "team": "👑 ADMIN"}}

DEFAULT_PLAYERS = [
    {"Name": "GOLU", "Photo": "golu.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 900},
    {"Name": "SIDHU", "Photo": "sidhu.jpg", "Role": "ATTACKER", "Base_Points": 2000},
    {"Name": "MITHU", "Photo": "mithu.jpg", "Role": "MIDDLE BLOCKER", "Base_Points": 2000},
    {"Name": "ABHISHEK", "Photo": "abhishek.jpg", "Role": "LIBERO", "Base_Points": 1600},
    {"Name": "ROHIT", "Photo": "rohit.jpg", "Role": "ALL ROUNDER", "Base_Points": 1600},
    {"Name": "YASH", "Photo": "yash.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 1000},
    {"Name": "SHASHWAT", "Photo": "shashwat.jpg", "Role": "RIGHT SIDE HITTER", "Base_Points": 1200},
    {"Name": "MOHIT", "Photo": "mohit.jpg", "Role": "LIBERO", "Base_Points": 1800},
    {"Name": "ABHINANDAN", "Photo": "abhinandan.jpg", "Role": "SETTER", "Base_Points": 500},
    {"Name": "RISHI", "Photo": "rishi.jpg", "Role": "LIBERO", "Base_Points": 1200},
    {"Name": "RAHIL", "Photo": "rahil.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 900},
    {"Name": "KISHU", "Photo": "kishu.jpg", "Role": "LIBERO", "Base_Points": 1100},
    {"Name": "KESHAV", "Photo": "keshav.jpg", "Role": "RIGHT SIDE HITTER", "Base_Points": 800},
    {"Name": "KUNAL", "Photo": "kunal.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 250},
    {"Name": "CHULBUL", "Photo": "chulbul.jpg", "Role": "SETTER", "Base_Points": 1400},
    {"Name": "PIYUSH", "Photo": "piyush.jpg", "Role": "ALL ROUNDER", "Base_Points": 2000},
    {"Name": "PIYUSH 1", "Photo": "piyush1.jpg", "Role": "SETTER", "Base_Points": 500},
    {"Name": "PIYUSH 2", "Photo": "piyush2.jpg", "Role": "SETTER", "Base_Points": 250},
    {"Name": "PANCHAM", "Photo": "pancham.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 800},
    {"Name": "ABHI", "Photo": "abhi.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 500},
    {"Name": "RISHU", "Photo": "rishu.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 700},
    {"Name": "RITIK", "Photo": "ritik.jpg", "Role": "LIBERO", "Base_Points": 1500},
    {"Name": "ANKUSH", "Photo": "ankush.jpg", "Role": "LIBERO", "Base_Points": 1600},
    {"Name": "AYUSH", "Photo": "ayush.jpg", "Role": "MIDDLE BLOCKER", "Base_Points": 1750},
    {"Name": "PRITHVI", "Photo": "prithvi.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 900},
    {"Name": "SHRESHTH", "Photo": "shreshth.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 1000},
    {"Name": "ABHINAV", "Photo": "abhinav.jpg", "Role": "ALL ROUNDER", "Base_Points": 2000}
]

# --- DATABASE FUNCTIONS ---
def get_default_db():
    return {
        "users": DEFAULT_USER_DATA, "players": DEFAULT_PLAYERS, "player_index": 0, "current_bid": 0, "current_team": "None", 
        "sold_data": [], "last_sold_trigger": False, "winner_name": "", "round_2": False, "last_bid_time": time.time(), 
        "passed_teams": [], "rtm_cards": {}
    }

def save_db(data):
    try: requests.put(FIREBASE_URL, json=data)
    except: pass

def load_db():
    default_db = get_default_db()
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                for key in default_db:
                    if key not in data: data[key] = default_db[key]
                return data
    except: pass
    
    save_db(default_db)
    return default_db
