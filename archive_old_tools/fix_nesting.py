import re

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The problem is there is an extra </div> right before INSIGHT HARI INI CONTAINER.
# Let's find:
target = '''                  </div>
                  </div>
                                <!-- INSIGHT HARI INI CONTAINER -->'''

replacement = '''                  </div>
                                <!-- INSIGHT HARI INI CONTAINER -->'''

if target in html:
    html = html.replace(target, replacement)
    
    # But wait, now we need to add the closing </div> AFTER the insight container, before TEKNISI TERBAIK
    # Let's find:
    end_target = '''                      </div>
                  </div>
              <!-- TEKNISI TERBAIK -->'''
    
    end_replacement = '''                      </div>
                  </div>
              </div>
              <!-- TEKNISI TERBAIK -->'''
              
    html = html.replace(end_target, end_replacement)

    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed nesting!")
else:
    print("Could not find exact target string")
