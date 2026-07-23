import pymysql

try:
    db_mysql = pymysql.connect(host='localhost', user='root', password='', database='db_ais_systems')
    cur_mysql = db_mysql.cursor()
    
    # Check if column already exists
    cur_mysql.execute("SHOW COLUMNS FROM data_sparepart LIKE 'qty'")
    result = cur_mysql.fetchone()
    
    if not result:
        print("Adding 'qty' column to data_sparepart table...")
        cur_mysql.execute("ALTER TABLE data_sparepart ADD COLUMN qty INT DEFAULT 0 AFTER jenis_device")
        db_mysql.commit()
        print("Column 'qty' added successfully!")
    else:
        print("Column 'qty' already exists.")
    
    cur_mysql.close()
    db_mysql.close()
except Exception as e:
    print(f"Error: {e}")
