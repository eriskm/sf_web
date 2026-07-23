import json

log_path = r"C:\Users\SFTECH\.gemini\antigravity\brain\21794dc7-48cb-4024-b1a6-7b0d23c05e46\.system_generated\logs\transcript_full.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    try:
        data = json.loads(lines[i])
        if data.get("type") == "VIEW_FILE" and "dashboard.html" in data.get("content", ""):
            content = data["content"]
            if len(content) > 1000:
                print(f"Step {data.get('step_index')}: {len(content)} chars. Starts with: {content.split('The following code')[0].strip()}")
    except Exception as e:
        pass
