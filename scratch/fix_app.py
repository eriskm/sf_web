file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Target baris 1505 sampai 1740 (Index 1504 sampai 1739)
del lines[1504:1740]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Berhasil membersihkan duplikat raksasa!")
