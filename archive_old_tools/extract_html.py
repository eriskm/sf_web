import json

log_path = r"C:\Users\SFTECH\.gemini\antigravity\brain\21794dc7-48cb-4024-b1a6-7b0d23c05e46\.system_generated\logs\transcript_full.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines:
    try:
        data = json.loads(line)
        if data.get("type") == "VIEW_FILE" and "dashboard.html" in data.get("content", "") and "Showing lines 1 to" in data.get("content", ""):
            print("FOUND VIEW FILE FOR HTML")
            content = data["content"]
            lines_part = content.split("The following code has been modified")[1].split("The above content does NOT show the entire file contents")[0]
            
            cleaned_lines = []
            for l in lines_part.strip().split("\n"):
                if ": " in l:
                    cleaned_lines.append(l.split(": ", 1)[1].rstrip('\r'))
            
            with open("dashboard_top_backup.txt", "w", encoding='utf-8') as out:
                out.write('\n'.join(cleaned_lines))
            print("Wrote top to dashboard_top_backup.txt")
            break
    except Exception as e:
        pass
