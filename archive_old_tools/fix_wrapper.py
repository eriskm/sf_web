import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# I need to find the </div> that closes the ACTION & INSIGHT ROW, and move it to after the Teknisi Terbaik block.
# Looking at the code:
#             <!-- ACTION & INSIGHT ROW -->
#             <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
#                 <!-- AKSI CEPAT CONTAINER -->...
#                 <!-- INSIGHT HARI INI CONTAINER -->...
#             </div>
#             
#             <!-- TEKNISI TERBAIK -->
#                 <div>
#                     ...
#                 </div>

# Replace the closing </div> before TEKNISI TERBAIK with nothing, and add it after TEKNISI TERBAIK
target = '''            </div>
            
            <!-- TEKNISI TERBAIK -->'''

replacement = '''            <!-- TEKNISI TERBAIK -->'''

html = html.replace(target, replacement)

# Now find the end of Teknisi Terbaik and add the closing </div>
# Look for the end of Teknisi Terbaik block, which is followed by:
#             </div>
#             
#             <!-- CHARTS AREA (Old Charts Repurposed) -->
end_target = '''                      </div>
                  </div>
              </div>
              
              <!-- CHARTS AREA (Old Charts Repurposed) -->'''

end_replacement = '''                      </div>
                  </div>
              </div>
              </div>
              
              <!-- CHARTS AREA (Old Charts Repurposed) -->'''

html = html.replace(end_target, end_replacement)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Wrapper fixed!")
