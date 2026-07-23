import json

log_path = r"C:\Users\SFTECH\.gemini\antigravity\brain\21794dc7-48cb-4024-b1a6-7b0d23c05e46\.system_generated\logs\transcript_full.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)-1, -1, -1):
    try:
        data = json.loads(lines[i])
        if data.get("type") == "VIEW_FILE" and "dashboard.html" in data.get("content", ""):
            content = data["content"]
            if "hero-grid" in content and "card-keuangan" in content:
                print(f"FOUND FULL VIEW FILE at step {data.get('step_index')}")
                lines_part = content.split("The following code has been modified")[1].split("The above content does NOT show the entire file contents")[0]
                
                cleaned_lines = []
                for l in lines_part.strip().split("\n"):
                    if ": " in l:
                        cleaned_lines.append(l.split(": ", 1)[1].rstrip('\r'))
                
                with open("dashboard_hero_backup.txt", "w", encoding='utf-8') as out:
                    out.write('\n'.join(cleaned_lines))
                print("Wrote to dashboard_hero_backup.txt")
                break
    except Exception as e:
        pass
