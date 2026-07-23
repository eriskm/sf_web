import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_marker = r'<!-- TEKNISI TERBAIK -->'
end_marker = r'<!-- CHARTS AREA \(Old Charts Repurposed\) -->'

start_match = re.search(start_marker, html)
end_match = re.search(end_marker, html)

if start_match and end_match:
    start_idx = start_match.start()
    end_idx = end_match.start()
    
    original_card = """<!-- TEKNISI TERBAIK -->
                    <div>
                        <div style="font-weight: 700; margin-bottom: 15px; font-size: 1.1em; color: var(--dark);">Teknisi Terbaik</div>
                        <div style="width: 280px; height: 175px; border-radius: 20px; padding: 24px; background: linear-gradient(135deg, #1e293b, #0f172a); color: white; border: 1px solid var(--border); position: relative; overflow: hidden; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2);">
                            <!-- Dekorasi -->
                            <div style="position: absolute; right: -20px; top: -20px; opacity: 0.1;">
                                <svg width="150" height="150" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
                            </div>
                            
                            <div style="display: flex; align-items: flex-start; gap: 15px; position: relative; z-index: 2;">
                                <!-- Avatar -->
                                <div style="width: 72px; height: 72px; border-radius: 50%; border: 3px solid #FBBF24; overflow: hidden; background: white; flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
                                    <img src="https://api.dicebear.com/7.x/adventurer-neutral/svg?seed={{ teknisi_terbaik['nama'] }}&backgroundColor=e2e8f0" alt="Avatar" style="width: 100%; height: 100%; object-fit: cover;">
                                </div>
                                <div>
                                    <!-- Crown & Title -->
                                    <div style="display: flex; align-items: center; gap: 5px; color: #FBBF24; margin-bottom: 2px;">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"></path></svg>
                                        <span style="font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">Top of the Day</span>
                                    </div>
                                    <div style="font-size: 24px; font-weight: 700; line-height: 1.1; margin-bottom: 4px;">{{ teknisi_terbaik['nama'] }}</div>
                                    <div style="font-size: 14px; color: #94a3b8;">{{ teknisi_terbaik['jobs'] }} Unit Selesai</div>
                                </div>
                            </div>
                            
                            <div style="position: relative; z-index: 2; display: flex; align-items: flex-end; justify-content: space-between;">
                                <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Total Revenue</div>
                                <div style="font-size: 24px; font-weight: 800; color: #22C55E; font-family: 'Poppins', sans-serif; line-height: 1;">Rp {{ "{:,}".format(teknisi_terbaik['revenue'] or 0) }}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
  """

    new_html = html[:start_idx] + original_card + html[end_idx:]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Reverted to original Teknisi Terbaik Card!")
else:
    print("Markers not found!")

