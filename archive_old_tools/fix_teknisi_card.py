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
    
    new_card = """<!-- TEKNISI TERBAIK -->
                    <div style="flex: 1; min-width: 320px;">
                        <div style="background: #ffffff; border-radius: 24px; padding: 24px; border: 1px solid #F1F5F9; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); position: relative; box-sizing: border-box; height: 100%; display: flex; flex-direction: column; justify-content: center;">
                            
                            <!-- Header -->
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px;">
                                <div style="width: 32px; height: 32px; border-radius: 50%; background: #8B5CF6; display: flex; align-items: center; justify-content: center; color: white;">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"></path></svg>
                                </div>
                                <div style="color: #6D28D9; font-size: 11px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;">Top of the Day</div>
                            </div>
                            
                            <!-- Main Content -->
                            <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 25px;">
                                <div style="flex: 1;">
                                    <div style="font-size: 18px; font-weight: 800; color: #0F172A; line-height: 1.2;">Teknisi Terbaik</div>
                                    <div style="font-size: 14px; color: #64748B; margin-bottom: 12px; font-weight: 500;">Hari Ini</div>
                                    
                                    <div style="font-size: 26px; font-weight: 900; color: #0F172A; margin-bottom: 12px; font-family: 'Poppins', sans-serif;">{{ teknisi_terbaik['nama'] }}</div>
                                    
                                    <div style="display: flex; flex-direction: column; gap: 4px;">
                                        <div style="display: flex; align-items: baseline; gap: 6px;">
                                            <span style="font-size: 16px; font-weight: 800; color: #0F172A;">{{ teknisi_terbaik['jobs'] }}</span>
                                            <span style="font-size: 12px; color: #64748B; font-weight: 500;">Unit Selesai</span>
                                        </div>
                                        <div style="display: flex; align-items: baseline; gap: 6px;">
                                            <span style="font-size: 15px; font-weight: 800; color: #0F172A;">Rp {{ "{:,}".format(teknisi_terbaik['revenue'] or 0) }}</span>
                                            <span style="font-size: 11px; color: #64748B; font-weight: 500;">Revenue</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Avatar -->
                                <div style="position: relative; width: 110px; height: 110px; flex-shrink: 0;">
                                    <div style="position: absolute; inset: 0; border-radius: 50%; background: linear-gradient(135deg, #DDD6FE, #EDE9FE); box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);"></div>
                                    <div style="position: absolute; top: 15px; right: -5px; color: #A78BFA;"><svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg></div>
                                    <div style="position: absolute; bottom: 10px; right: 0px; color: #60A5FA;"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg></div>
                                    
                                    <div style="position: absolute; inset: 4px; border-radius: 50%; border: 3px solid white; overflow: hidden; background: white;">
                                        <img src="https://api.dicebear.com/7.x/adventurer-neutral/svg?seed={{ teknisi_terbaik['nama'] }}&backgroundColor=e2e8f0" alt="Avatar" style="width: 100%; height: 100%; object-fit: cover; background: #EEF2FF;">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Bottom Pills -->
                            <div style="display: flex; gap: 10px;">
                                <div style="flex: 1; background: #F5F3FF; border-radius: 12px; padding: 12px 15px; display: flex; align-items: center; justify-content: space-between;">
                                    <span style="font-size: 11px; font-weight: 700; color: #0F172A;">Efficiency</span>
                                    <span style="font-size: 20px; font-weight: 800; color: #6D28D9;">96%</span>
                                </div>
                                <div style="flex: 1.2; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 15px; display: flex; align-items: center; justify-content: center; gap: 6px;">
                                    <span style="color: #10B981; font-size: 12px; font-weight: 700;">? 18%</span>
                                    <span style="color: #94A3B8; font-size: 11px; font-weight: 500;">vs kemarin</span>
                                </div>
                            </div>
                            
                        </div>
                    </div>
                </div>
                
  """

    new_html = html[:start_idx] + new_card + html[end_idx:]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("New Teknisi Terbaik Card Applied!")
else:
    print("Markers not found!")

