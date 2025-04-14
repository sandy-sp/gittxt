import json
from datetime import datetime
from pathlib import Path


def export_chat_as_json(chat_history, output_dir="/tmp/gittxt_exports"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = Path(output_dir) / f"chat_{timestamp}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, indent=2, ensure_ascii=False)
    return file_path


def export_chat_as_markdown(chat_history, output_dir="/tmp/gittxt_exports"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = Path(output_dir) / f"chat_{timestamp}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        for msg in chat_history:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            f.write(f"### {role}\n\n{content}\n\n")
    return file_path
