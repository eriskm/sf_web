import json

log_path = r"C:\Users\SFTECH\.gemini\antigravity\brain\21794dc7-48cb-4024-b1a6-7b0d23c05e46\.system_generated\logs\transcript_full.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    try:
        data = json.loads(lines[i])
        if data.get("type") == "VIEW_FILE" and "dashboard.css" in data.get("content", ""):
            content = data["content"]
            print(f"Step {data.get('step_index')}: {len(content)} chars")
            lines_part = content.split("The following code has been modified")[1]
            if "The above content does NOT show the entire file contents" in lines_part:
                lines_part = lines_part.split("The above content does NOT show the entire file contents")[0]
            elif "<EPHEMERAL_MESSAGE>" in lines_part:
                lines_part = lines_part.split("The following is an <EPHEMERAL_MESSAGE>")[0]
            
            cleaned_lines = []
            for l in lines_part.strip().split("\n"):
                if ": " in l:
                    cleaned_lines.append(l.split(": ", 1)[1].rstrip('\r'))
            
            with open(f"dashboard_css_{data.get('step_index')}.txt", "w", encoding='utf-8') as out:
                out.write('\n'.join(cleaned_lines))
    except Exception as e:
        pass
