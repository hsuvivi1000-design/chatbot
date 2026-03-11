"""
LangChain + Gemini API 對話程式
支援多輪對話、自動讀取資料夾內的 PDF 與圖片
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import base64
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 載入 .env 環境變數
load_dotenv()

# ─────────────────────────────────────────────
# 設定：檔案資料夾（可在 .env 設定 FILES_DIR）
# ─────────────────────────────────────────────
_env_dir = os.getenv("FILES_DIR")
FILES_DIR = Path(_env_dir) if _env_dir else Path(__file__).parent / "files"
FILES_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
SUPPORTED_DOCS   = {".pdf"}
SUPPORTED_ALL    = SUPPORTED_IMAGES | SUPPORTED_DOCS

MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

# ─────────────────────────────────────────────
# 檔案處理函式
# ─────────────────────────────────────────────
def list_files() -> list[Path]:
    """列出資料夾中所有支援的檔案"""
    return sorted(
        f for f in FILES_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_ALL
    )

def _image_block(path: Path) -> dict:
    """將圖片編碼為 base64 content block"""
    mime = MIME_MAP.get(path.suffix.lower(), "image/jpeg")
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}}

def _pdf_text(path: Path) -> str:
    """用 pypdf 提取 PDF 文字"""
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"[第{i}頁]\n{text}")
    return "\n\n".join(pages) if pages else "[此 PDF 無法提取文字]"

def build_file_context() -> tuple[list[dict], str]:
    """
    掃描資料夾，回傳：
      - image_blocks: list，供 HumanMessage content 使用的圖片 block
      - pdf_text: str，所有 PDF 的合併文字，附在訊息前段
    """
    files = list_files()
    image_blocks = []
    pdf_parts = []

    for f in files:
        suffix = f.suffix.lower()
        if suffix in SUPPORTED_IMAGES:
            image_blocks.append(_image_block(f))
        elif suffix == ".pdf":
            text = _pdf_text(f)
            pdf_parts.append(f"=== PDF：{f.name} ===\n{text}")

    pdf_text = "\n\n".join(pdf_parts)
    return image_blocks, pdf_text, files

# ─────────────────────────────────────────────
# 初始化模型
# ─────────────────────────────────────────────
def create_model(model_name: str = "gemini-2.5-flash", temperature: float = 0.7):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("找不到 GOOGLE_API_KEY，請確認 .env 檔案已正確設定。")
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key,
    )

# ─────────────────────────────────────────────
# 對話管理
# ─────────────────────────────────────────────
class GeminiChatbot:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.llm = create_model(model_name)
        self.chat_history: list = []
        self.system_prompt = (
            "你是一個友善、博學的 AI 助手，名叫「小智」。"
            "請用繁體中文回答所有問題，回答要簡潔清晰。"
            "若資料夾中有圖片或 PDF，你可以直接參考其內容來回答問題。"
            "若遇到不確定的問題，請誠實告知。"
        )

    def chat(self, user_input: str) -> str:
        """
        自動掃描資料夾，將圖片與 PDF 一起送給 AI，
        使用者只需直接輸入問題。
        """
        image_blocks, pdf_text, files = build_file_context()

        # 組合 HumanMessage content
        content = []

        # 附上圖片（多模態）
        content.extend(image_blocks)

        # 組合文字部分（PDF 文字 + 使用者輸入）
        text_parts = []
        if pdf_text:
            text_parts.append(f"以下是資料夾中的 PDF 內容：\n\n{pdf_text}\n\n---")
        text_parts.append(user_input)
        content.append({"type": "text", "text": "\n\n".join(text_parts)})

        human_msg = HumanMessage(content=content if image_blocks else "\n\n".join(text_parts))

        # 組合完整訊息
        messages = [SystemMessage(content=self.system_prompt)]
        messages.extend(self.chat_history)
        messages.append(human_msg)

        response = self.llm.invoke(messages)
        ai_reply = response.content

        # 歷史只存純文字
        self.chat_history.append(HumanMessage(content=user_input))
        self.chat_history.append(AIMessage(content=ai_reply))

        return ai_reply

    def clear_history(self):
        self.chat_history = []
        print("[清除] 對話歷史已清除。\n")

    def show_history(self):
        if not self.chat_history:
            print("（尚無對話記錄）\n")
            return
        print("\n" + "="*55 + " 對話歷史 " + "="*55)
        for msg in self.chat_history:
            role = "[你]" if isinstance(msg, HumanMessage) else "[AI]"
            content = msg.content
            if isinstance(content, list):
                content = next((c["text"] for c in content if c.get("type") == "text"), "[圖片]")
            print(f"{role}：{content}\n")
        print("="*120 + "\n")

# ─────────────────────────────────────────────
# 主程式
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  LangChain + Gemini 對話機器人")
    print("=" * 60)

    # 啟動時掃描資料夾，顯示已偵測到的檔案
    files = list_files()
    if files:
        print(f"[偵測] 已找到 {len(files)} 個檔案，AI 可直接讀取：")
        for f in files:
            print(f"       - {f.name}")
    else:
        print(f"[偵測] 資料夾中目前沒有支援的檔案。")
        print(f"       路徑：{FILES_DIR}")

    print("\n指令：/clear 清除歷史 | /history 查看歷史 | /quit 離開")
    print("=" * 60 + "\n")

    bot = GeminiChatbot()

    while True:
        try:
            user_input = input("你：").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n已離開程式，再見！")
            break

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("已離開程式，再見！")
            break
        elif user_input.lower() == "/clear":
            bot.clear_history()
            continue
        elif user_input.lower() == "/history":
            bot.show_history()
            continue

        try:
            print("AI：", end="", flush=True)
            reply = bot.chat(user_input)
            print(reply)
            print()
        except Exception as e:
            print(f"\n[錯誤] {e}\n")

if __name__ == "__main__":
    main()
