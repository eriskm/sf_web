import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# I will add a loading text update
# find: document.body.style.cursor = 'wait';
# replace with: 
# document.body.style.cursor = 'wait';
# let btn = document.querySelector('#popupKas button:last-child');
# btn.innerText = 'Memproses... Jangan Tutup Web!';
# btn.style.backgroundColor = '#6c757d';
# btn.disabled = true;

old_js = "document.body.style.cursor = 'wait';"
new_js = '''document.body.style.cursor = 'wait';
          
          let btn = document.querySelector('#popupKas button:nth-child(2)');
          if(btn) {
              btn.innerText = 'Tunggu 10-20 Detik...';
              btn.style.backgroundColor = '#6c757d';
              btn.disabled = true;
          }
          
          // Tampilkan overlay loading layar penuh
          let loader = document.createElement('div');
          loader.id = 'fullScreenLoader';
          loader.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:9999;display:flex;flex-direction:column;justify-content:center;align-items:center;color:white;font-family:Poppins,sans-serif;';
          loader.innerHTML = '<div style="font-size:2em;margin-bottom:20px;">dY?~</div><h2>Sedang Memproses Tutup Kas...</h2><p>Mohon jangan menutup atau me-refresh halaman ini.<br>Proses ini memakan waktu sekitar 15-20 detik.</p>';
          document.body.appendChild(loader);
'''

html = html.replace(old_js, new_js)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Loader added!")
