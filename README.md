# AI Chatbot 專案名稱

## 小組：第六組

### 組員：

* 姚谷伝
* 許瀞云
* 林湘紜

## 專案簡介

本專案是一個使用 LangChain 與 Gemini API 製作的 AI 聊天機器人，使用 Gradio 作為網頁介面，具備基本的對話與記憶功能，並可上傳圖片與PDF檔進行分析，還可切換及新增不同的AI角色設定進行對話。此外，記憶功能以JSON檔案儲存，方便使用者查看與供AI進行回憶對話紀錄。

## 目前功能
PDF 文件與圖片上傳、儲存與讀取歷史紀錄

## 執行方式

1. 下載專案

範例指令：

```bash
https://github.com/hsuvivi1000-design/chatbot.git
```
2. 開啟Antigravity，點選clone repository貼上專案網址開啟

3. 呼喚AI Agent輸入文字執行專案

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

在開發聊天機器人時，了解到以前從來沒學過的框架**LangChain**，可以很好的供使用者於不同的AI模型間進行切換，以及讀取和生成內容。而且這次專案也嘗試了使用 **Gradio**來做網頁GUI，可以與以前用 **Streamlit**來做的頁面比較不同之處。除此之外，也發現AI雖是一個很好的工具，但學會如何正確且精準地問問題，這樣才能有最快、最好的結果產生，不然經常需要耗費許多時間要求AI除錯及修改程式。而且當**Claude Opus 4.6**額度用完時，用**gemini 3.1 pro**來做才發現，不同AI專精的項目真的不相同。

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
