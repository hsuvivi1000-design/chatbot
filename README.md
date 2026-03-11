# AI Chatbot 專案名稱

## 小組：第六組

### 組員：

* 姚谷伝
* 組員2

## 專案簡介

請簡要說明本專案的用途。
例如：本專案是一個使用 LangChain 與 Gemini API 製作的 AI 聊天機器人，具備基本的對話與記憶功能。

## 目前功能

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

問題：
解法：

---

## 學習心得

姚谷伝

在本次專案開發中，我深入實踐了如何整合 **LangChain** 框架與 **Gemini API** 來建立一個具備多模態感知能力的 AI 助手。透過實作檔案掃描與文字提取功能，我學習到大型語言模型如何處理結構化與非結構化數據（如 PDF 與圖片），並體認到提示詞工程 (Prompt Engineering) 在導引 AI 進行精準回答上的重要性。此外，使用 **Gradio** 快速構建網頁介面，讓我理解到良好的使用者互動設計能大幅提升工具的實用價值。這次作業不僅強化了我的 Python 實作能力，更讓我對後端邏輯與多模態技術的結合有了更全面的認識。

---

## GitHub 專案連結

姚谷伝 
https://github.com/ommi0705/chatbox