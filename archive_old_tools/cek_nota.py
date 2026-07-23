from html2image import Html2Image
import os

print("--- DIAGNOSA MESIN NOTA ---")

output_dir = os.path.join(os.getcwd(), 'static', 'nota_digital')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Folder created: {output_dir}")

hti = Html2Image(output_path=output_dir, custom_flags=['--headless=new', '--no-sandbox', '--default-background-color=ffffffff'])

test_html = "<h1>Tes Mesin Nota AIS</h1><p>Kalau gambar ini muncul, berarti mesin OK!</p>"

try:
    print("Sedang mencoba mengambil gambar...")
    hti.screenshot(html_str=test_html, save_as='test_debug.png')
    
    path_hasil = os.path.join(output_dir, 'test_debug.png')
    if os.path.exists(path_hasil):
        print("\n✅ MANTAP! Mesin Nota OK.")
        print(f"Hasil tes ada di: {path_hasil}")
    else:
        print("\n❌ WADUH! File nggak kebuat tapi nggak ada error.")
except Exception as e:
    print("\n❌ ERROR TERDETEKSI:")
    print(str(e))
    print("\nSaran: Pastiin Google Chrome sudah terinstal di lokasi standar.")
