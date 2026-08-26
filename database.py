import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_FILE

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            subscription TEXT DEFAULT 'free',
            expires INTEGER DEFAULT 0,
            daily_requests INTEGER DEFAULT 0,
            last_reset INTEGER DEFAULT 0,
            ref_code TEXT,
            balance INTEGER DEFAULT 0,
            registered_at INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER,
            earned INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0,
            FOREIGN KEY (referrer_id) REFERENCES users (user_id),
            FOREIGN KEY (referred_id) REFERENCES users (user_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            timestamp INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pocket_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT,
            price REAL,
            change REAL,
            timestamp INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user(user_id: int) -> dict:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, username, subscription, expires, daily_requests, 
               last_reset, ref_code, balance, registered_at
        FROM users WHERE user_id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'user_id': row[0],
            'username': row[1],
            'subscription': row[2],
            'expires': row[3],
            'daily_requests': row[4],
            'last_reset': row[5],
            'ref_code': row[6],
            'balance': row[7],
            'registered_at': row[8]
        }
    return None

def create_user(user_id: int, username: str = None):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    ref_code = f"ref_{user_id}_{datetime.now().strftime('%Y%m%d')}"
    now = int(datetime.now().timestamp())
    
    cursor.execute('''
        INSERT INTO users (user_id, username, subscription, expires, daily_requests, 
                          last_reset, ref_code, balance, registered_at)
        VALUES (?, ?, 'free', 0, 0, ?, ?, 0, ?)
    ''', (user_id, username, now, ref_code, now))
    
    conn.commit()
    conn.close()
    return ref_code

def update_user(user_id: int, **kwargs):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    for key, value in kwargs.items():
        cursor.execute(f'UPDATE users SET {key} = ? WHERE user_id = ?', (value, user_id))
    
    conn.commit()
    conn.close()

def add_referral(referrer_id: int, referred_id: int):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    now = int(datetime.now().timestamp())
    cursor.execute('''
        INSERT INTO referrals (referrer_id, referred_id, earned, created_at)
        VALUES (?, ?, 0, ?)
    ''', (referrer_id, referred_id, now))
    
    conn.commit()
    conn.close()

def get_referrals(user_id: int) -> list:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT referred_id, earned, created_at
        FROM referrals WHERE referrer_id = ?
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{'referred_id': r[0], 'earned': r[1], 'created_at': r[2]} for r in rows]

def get_referral_earnings(user_id: int) -> int:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(earned) FROM referrals WHERE referrer_id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row[0] else 0

def log_request(user_id: int, action: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    now = int(datetime.now().timestamp())
    cursor.execute('''
        INSERT INTO requests_history (user_id, action, timestamp)
        VALUES (?, ?, ?)
    ''', (user_id, action, now))
    
    conn.commit()
    conn.close()

def reset_daily_requests():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    now = int(datetime.now().timestamp())
    cursor.execute('UPDATE users SET daily_requests = 0, last_reset = ?', (now,))
    
    conn.commit()
    conn.close()

init_db()