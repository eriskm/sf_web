# ============================================
# KONFIGURASI LOCAL - DISABLE MYSQL
# ============================================
# File ini untuk development lokal tanpa MySQL server

USE_MYSQL = True  # Set ke False jika MySQL tidak tersedia

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_ais_systems'
}

# Jika Anda punya MySQL di server lain, ubah host di atas
# Contoh:
# 'host': '192.168.1.100'  # IP server MySQL
# 'password': 'your_password'
