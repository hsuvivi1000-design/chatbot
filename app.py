"""
Gradio 網頁介面 - LangChain + Gemini 對話機器人
功能：多輪對話 / 自動讀取 PDF & 圖片 / 自動存檔 / 讀取歷史對話 / 開新對話
"""

import os
import json
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

# ─────────────────────────────────────────────
# 路徑設定
# ─────────────────────────────────────────────
_env_dir = os.getenv("FILES_DIR")
FILES_DIR   = Path(_env_dir) if _env_dir else Path(__file__).parent / "files"
HISTORY_DIR = Path(__file__).parent / "history"
FILES_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
SUPPORTED_DOCS   = {".pdf"}
SUPPORTED_ALL    = SUPPORTED_IMAGES | SUPPORTED_DOCS
MIME_MAP = {".png":"image/png",".jpg":"image/jpeg",
            ".jpeg":"image/jpeg",".webp":"image/webp",".gif":"image/gif"}

SYSTEM_PROMPT = (
    "你是一個友善、博學的 AI 助手，名叫「小智」。"
    "請用繁體中文回答所有問題，回答要簡潔清晰。"
    "若資料夾中有圖片或 PDF，你可以直接參考其內容來回答問題。"
    "若遇到不確定的問題，請誠實告知。"
)

# ─────────────────────────────────────────────
# 模型
# ─────────────────────────────────────────────
LLM = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# ─────────────────────────────────────────────
# 檔案處理
# ─────────────────────────────────────────────
def list_files() -> list[Path]:
    return sorted(f for f in FILES_DIR.iterdir()
                  if f.is_file() and f.suffix.lower() in SUPPORTED_ALL)

def _image_block(path: Path) -> dict:
    mime = MIME_MAP.get(path.suffix.lower(), "image/jpeg")
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode()
    return {"type":"image_url","image_url":{"url":f"data:{mime};base64,{data}"}}

def _pdf_text(path: Path) -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, 1):
        t = (page.extract_text() or "").strip()
        if t: pages.append(f"[第{i}頁]\n{t}")
    return "\n\n".join(pages) if pages else "[此 PDF 無法提取文字]"

def build_file_context():
    img_blocks, pdf_parts = [], []
    for f in list_files():
        s = f.suffix.lower()
        if s in SUPPORTED_IMAGES: img_blocks.append(_image_block(f))
        elif s == ".pdf": pdf_parts.append(f"=== PDF：{f.name} ===\n{_pdf_text(f)}")
    return img_blocks, "\n\n".join(pdf_parts)

def get_files_status() -> str:
    files = list_files()
    if not files:
        return f"目前無檔案\n路徑：{FILES_DIR}"
    lines = [f"已偵測 {len(files)} 個檔案：\n"]
    for f in files:
        icon = "🖼️" if f.suffix.lower() in SUPPORTED_IMAGES else "📄"
        lines.append(f"{icon} {f.name}  ({f.stat().st_size/1024:.1f} KB)")
    return "\n".join(lines)

# ─────────────────────────────────────────────
# 歷史對話 - 儲存 / 讀取
# ─────────────────────────────────────────────
def _conv_title(history: list) -> str:
    """以第一句使用者訊息作為標題"""
    for msg in history:
        if msg.get("role") == "user":
            text = msg["content"][:30]
            return text + ("…" if len(msg["content"]) > 30 else "")
    return "（空對話）"

def auto_save(history: list, conv_path: str | None) -> tuple[str, str]:
    """
    自動存檔：
    - conv_path 為 None   → 建立新檔案
    - conv_path 有值      → 覆寫原始檔案
    回傳 (new_conv_path_str, status_msg)
    """
    if not history:
        return conv_path or "", ""
    title = _conv_title(history)
    now   = datetime.now()
    data  = {"timestamp": now.isoformat(), "title": title, "messages": history}
    if conv_path:
        path = Path(conv_path)
    else:
        ts   = now.strftime("%Y%m%d_%H%M%S")
        path = HISTORY_DIR / f"conv_{ts}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path), f"💾 已自動存檔"

def list_conversations() -> list[str]:
    """回傳所有儲存對話的顯示名稱（最新在前）"""
    files = sorted(HISTORY_DIR.glob("conv_*.json"), reverse=True)
    results = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            ts_str = data.get("timestamp", "")[:16].replace("T", " ")
            title = data.get("title", f.stem)
            results.append(f"[{ts_str}] {title}")
        except Exception:
            results.append(f.stem)
    return results

def load_conversation(selected: str) -> tuple[list, str, str]:
    """根據顯示名稱載入對話，回傳 (history, conv_path_str, status_msg)"""
    if not selected:
        return [], "", "請選擇一筆對話。"
    files = sorted(HISTORY_DIR.glob("conv_*.json"), reverse=True)
    conv_list = list_conversations()
    try:
        idx = conv_list.index(selected)
        fpath = files[idx]
        data = json.loads(fpath.read_text(encoding="utf-8"))
        history = data.get("messages", [])
        return history, str(fpath), f"✅ 已載入：{data.get('title','')}"
    except (ValueError, IndexError, Exception) as e:
        return [], "", f"❌ 載入失敗：{e}"

# ─────────────────────────────────────────────
# 對話邏輯
# ─────────────────────────────────────────────
def respond(user_message: str, history: list) -> str:
    img_blocks, pdf_text = build_file_context()
    text_parts = []
    if pdf_text:
        text_parts.append(f"以下是資料夾中的 PDF 內容：\n\n{pdf_text}\n\n---")
    text_parts.append(user_message)
    combined = "\n\n".join(text_parts)

    human_msg = HumanMessage(
        content=(img_blocks + [{"type":"text","text":combined}]) if img_blocks else combined
    )
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for item in history:
        role, text = item.get("role",""), item.get("content","")
        if role == "user":      messages.append(HumanMessage(content=text))
        elif role == "assistant": messages.append(AIMessage(content=text))
    messages.append(human_msg)
    return LLM.invoke(messages).content

# ─────────────────────────────────────────────
# 事件函式
# ─────────────────────────────────────────────
def user_send(message, history):
    if not message.strip():
        return "", history, history
    history = (history or []) + [{"role":"user","content":message}]
    return "", history, history

def bot_reply(history, conv_path):
    """取得 AI 回覆，並自動存檔。回傳 (chatbot, history_state, conv_file_state, conv_list, autosave_status)"""
    if not history or history[-1]["role"] != "user":
        return history, history, conv_path, gr.update(), ""
    reply = respond(history[-1]["content"], history[:-1])
    history = history + [{"role":"assistant","content":reply}]
    new_path, status = auto_save(history, conv_path or None)
    choices = list_conversations()
    return history, history, new_path, gr.update(choices=choices, value=None), status

def do_retry(history, conv_path):
    if len(history) >= 2 and history[-1]["role"] == "assistant":
        history = history[:-1]
    return bot_reply(history, conv_path)

def new_conversation():
    """開新對話：清空聊天、歷史、存檔路徑"""
    return [], [], "", ""  # chatbot, history_state, conv_file_state, msg_box

def do_load(selected):
    history, fpath, status = load_conversation(selected)
    return history, history, fpath, status

def do_refresh_convs():
    choices = list_conversations()
    return gr.update(choices=choices, value=None)

# ─────────────────────────────────────────────
# Gradio UI
# ─────────────────────────────────────────────
CSS = """
footer { display: none !important; }
.file-box textarea, .hist-box textarea {
    font-family: monospace !important; font-size: 0.83em !important;
}
#save-status { color: #2d7d46; font-size: 0.85em; }
"""

with gr.Blocks(title="小智 AI 助手") as demo:

    gr.Markdown("# 🤖 小智 AI 助手\n直接輸入問題，AI 自動讀取資料夾中的圖片與 PDF。每次回覆後**自動存檔**。")

    with gr.Row():
        # ── 左側：歷史對話清單 ───────────────────
        with gr.Column(scale=1, min_width=220):
            gr.Markdown("### 💬 歷史對話")
            conv_list = gr.Dropdown(
                choices=list_conversations(),
                label="選擇對話",
                interactive=True,
                allow_custom_value=False,
            )
            load_btn         = gr.Button("📂 載入", variant="primary", size="sm")
            refresh_conv_btn = gr.Button("🔄 重新整理", size="sm")
            load_status      = gr.Markdown("", elem_id="save-status")
            gr.Markdown("---")
            new_btn      = gr.Button("✏️ 開新對話", variant="secondary")
            autosave_lbl = gr.Markdown("", elem_id="save-status")  # 自動存檔狀態

        # ── 中間：聊天 ───────────────────────────
        with gr.Column(scale=4):
            chatbot_ui    = gr.Chatbot(label="對話", height=500)
            history_state = gr.State([])   # 對話歷史
            conv_file_state = gr.State("") # 目前存檔路徑（空字串=新對話）

            with gr.Row():
                msg_box  = gr.Textbox(placeholder="輸入問題，按 Enter 送出…",
                                      show_label=False, scale=5)
                send_btn = gr.Button("發送 ▶", variant="primary", scale=1)
            retry_btn = gr.Button("🔄 重新發送上一句", variant="secondary", size="sm")

        # ── 右側：檔案狀態 ────────────────────────
        with gr.Column(scale=1, min_width=220):
            gr.Markdown("### 📂 檔案偵測")
            file_box = gr.Textbox(
                value=get_files_status,
                label=f"資料夾：{FILES_DIR.name}",
                lines=12, interactive=False,
                elem_classes=["file-box"],
            )
            file_refresh_btn = gr.Button("🔄 重新掃描", size="sm")
            gr.Markdown("**支援格式**\n- 🖼️ PNG / JPG / WEBP / GIF\n- 📄 PDF")

    # ── 事件綁定 ──────────────────────────────
    # bot_reply 輸出：chatbot, history_state, conv_file_state, conv_list, autosave_lbl
    REPLY_OUTPUTS = [chatbot_ui, history_state, conv_file_state, conv_list, autosave_lbl]

    msg_box.submit(
        user_send, [msg_box, history_state], [msg_box, chatbot_ui, history_state]
    ).then(bot_reply, [history_state, conv_file_state], REPLY_OUTPUTS)

    send_btn.click(
        user_send, [msg_box, history_state], [msg_box, chatbot_ui, history_state]
    ).then(bot_reply, [history_state, conv_file_state], REPLY_OUTPUTS)

    retry_btn.click(do_retry, [history_state, conv_file_state], REPLY_OUTPUTS)

    # 新對話（清空 conv_file_state → 下次自動存檔建新檔）
    new_btn.click(new_conversation, outputs=[chatbot_ui, history_state, conv_file_state, msg_box])

    # 載入對話（把 conv_file_state 設為對應的 JSON 路徑）
    load_btn.click(
        do_load, conv_list,
        [chatbot_ui, history_state, conv_file_state, load_status]
    )

    # 重新整理清單
    refresh_conv_btn.click(do_refresh_convs, outputs=conv_list)

    # 重新掃描檔案
    file_refresh_btn.click(get_files_status, outputs=file_box)


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        inbrowser=True,
        share=False,
        css=CSS,
    )
