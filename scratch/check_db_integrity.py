import sqlite3
import glob

def check_dbs():
    dbs = glob.glob('*.db')
    for db in dbs:
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute('PRAGMA integrity_check;')
            result = cursor.fetchone()
            print(f'{db}: {result[0]}')
            conn.close()
        except Exception as e:
            print(f'{db}: ERROR - {e}')

if __name__ == '__main__':
    check_dbs()
