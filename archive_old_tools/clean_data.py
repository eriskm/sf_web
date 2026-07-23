import pandas as pd
import os

def bersihkan_data():
    # Nama file sesuai yang kelihatan di terminal lo tadi
    file_name = 'data SUKABUMIFLASHER.xlsx'
    
    print(f"Mulai memproses file Excel: {file_name}")
    
    try:
        # Baca Sheet 'Data Servis', skip 3 baris awal
        # Kita pakai engine='openpyxl' supaya bisa baca .xlsx
        df = pd.read_excel(file_name, sheet_name='Data Servis', skiprows=3, engine='openpyxl')
        
        # Hapus kolom yang nggak ada namanya
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Daftar kolom biaya yang mau dibersihin
        kolom_angka = ['Estimasi Biaya', 'Harga Jual', 'Modal Part', 'Modal Jasa', 'Laba Kotor']

        def clean_val(val):
            if pd.isna(val) or val == '':
                return 0
            # Ubah jadi teks, hapus 'k', '.', 'rp', dan spasi
            text = str(val).lower()
            text = text.replace('k', '000').replace('.', '').replace('rp', '').replace(' ', '')
            # Ambil hanya angkanya saja
            angka = ''.join(filter(str.isdigit, text))
            return int(angka) if angka else 0

        for col in kolom_angka:
            if col in df.columns:
                df[col] = df[col].apply(clean_val)

        # Simpan hasilnya jadi CSV biar enteng buat langkah selanjutnya
        df.to_csv('data_servis_clean.csv', index=False)
        print("-----------------------------------------")
        print("MANTAP BRO! File 'data_servis_clean.csv' BERHASIL dibuat.")
        print("Data lo sekarang udah 'Clean' dan siap masuk ke sistem web.")
        
    except Exception as e:
        print(f"Waduh, ada kendala: {e}")
        print("Pastiin file Excelnya lagi nggak lo buka di aplikasi Excel ya.")

if __name__ == "__main__":
    bersihkan_data()