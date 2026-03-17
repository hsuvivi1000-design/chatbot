# AI Chatbot 專案名稱

## 小組：第六組

### 組員：

* 姚谷伝
* 許瀞云
* 林湘紜

## 專案簡介

請簡要說明本專案的用途。
例如：本專案是一個使用 LangChain 與 Gemini API 製作的 AI 聊天機器人，具備基本的對話與記憶功能。

## 目前功能
PDF 文件與圖片上傳、儲存與讀取歷史紀錄

## 執行方式

1. 下載專案

範例指令：

```bash
https://github.com/hsuvivi1000-design/chatbot.git
```

---

## 環境變數說明

請自行建立 `.env` 檔案，並填入自己的 API key。

範例：

```env
GEMINI_API_KEY=your_api_key_here
```

## 遇到的問題與解法

### 問題 1 

姚谷伝

問題：Gemini API 在處理大量 PDF 文字與多張圖片時，Token 消耗較快且有時會遺失上下文。
解法：在 `chatbot.py` 中最佳化了 `build_file_context` 邏輯，僅在使用者輸入時動態載入最新檔案內容，並限制 PDF 提取文字的格式，確保 Payload 結構清晰。

### 問題 2

問題：同時在git hyb 上編輯和pull到antigravity編輯內容不會同步，或是內容被覆蓋掉
解法：不要同時編輯，若有覆蓋的狀況可以在antigravity的歷史紀錄中找回。

---

## 學習心得

姚谷伝

在本次專案開發中，我深入實踐了如何整合 **LangChain** 框架與 **Gemini API** 來建立一個具備多模態感知能力的 AI 助手。透過實作檔案掃描與文字提取功能，我學習到大型語言模型如何處理結構化與非結構化數據（如 PDF 與圖片），並體認到提示詞工程 (Prompt Engineering) 在導引 AI 進行精準回答上的重要性。此外，使用 **Gradio** 快速構建網頁介面，讓我理解到良好的使用者互動設計能大幅提升工具的實用價值。這次作業不僅強化了我的 Python 實作能力，更讓我對後端邏輯與多模態技術的結合有了更全面的認識。

林湘紜

許瀞云

在本次課程中我認識了一個團隊協作便捷的路徑-**git hub**。使用這個方法可以讓同一份專案及時同步到其他人手上，但這個方法也有其風險，例如課上多次強調的**api**的不可公開。在使用GitHub同步的同時，更要注意是否安全開發。

---

## GitHub 專案連結

姚谷伝 
https://github.com/ommi0705/chatbox
林湘紜
https://github.com/piyan-lab/work2
許瀞云
https://github.com/hsuvivi1000-design/chatbot.git
