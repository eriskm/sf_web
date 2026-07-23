import pymysql

def search_sparepart_local(query: str):
    \"\"\"
    Mencari stok sparepart di database lokal Sukabumi Flasher.
    Gunakan fungsi ini jika user menanyakan ketersediaan barang atau harga di toko.
    Argumen 'query' bisa berupa merk, tipe HP, atau jenis barang (misal: 'LCD Oppo A5').
    \"\"\"
    try:
        db = pymysql.connect(
            host='127.0.0.1', 
            user='root', 
            password='', 
            database='db_ais_systems',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = db.cursor()
        
        search_term = f"%{query}%"
        sql = \"\"\"
        SELECT kategori, merek, jenis_barang, jenis_device, qty, harga_jual 
        FROM data_sparepart 
        WHERE merek LIKE %s OR jenis_barang LIKE %s OR jenis_device LIKE %s
        LIMIT 5
        \"\"\"
        cursor.execute(sql, (search_term, search_term, search_term))
        results = cursor.fetchall()
        db.close()

        if not results:
            return "Maaf Bro, sparepart tersebut ngga ketemu di stok gudang lokal."
        
        teks = "📦 **HASIL CEK STOK GUDANG SF:**\n--------------------------\n"
        for r in results:
            teks += f"• {r['merek']} {r['jenis_barang']} ({r['jenis_device']}): {r['qty']} pcs | Harga: Rp {r['harga_jual']:,}\n"
        
        return teks
    except Exception as e:
        return f"❌ Gagal akses database lokal: {str(e)}"
