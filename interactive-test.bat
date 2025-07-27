@echo off
setlocal enabledelayedexpansion

echo 🎯 Agentic Teaching System - 互動式測試
echo.
echo 這個腳本將讓您親自體驗系統的各種功能
echo.

:menu
echo ==========================================
echo 請選擇要測試的功能：
echo.
echo 1. 💬 簡單對話測試
echo 2. 🔢 數學問題求解
echo 3. 📚 語言學習輔助
echo 4. 🤖 代理協作演示
echo 5. 📊 查看系統狀態
echo 6. 🧪 執行快速健康檢查
echo 0. 退出
echo.
set /p choice="請輸入您的選擇 (0-6): "

if "%choice%"=="1" goto chat_test
if "%choice%"=="2" goto math_test
if "%choice%"=="3" goto language_test
if "%choice%"=="4" goto agent_demo
if "%choice%"=="5" goto system_status
if "%choice%"=="6" goto health_check
if "%choice%"=="0" goto end
goto menu

:chat_test
echo.
echo 💬 簡單對話測試
echo ==========================================
set /p question="請輸入您想問的問題: "
echo.
echo 🤔 AI 正在思考...
docker exec agentic-app python -c "
from llm_engines.factory import LLMEngineFactory
engine = LLMEngineFactory.create_engine()
response = engine.generate_response('%question%')
print('🤖 AI 回答:')
print(response)
"
echo.
pause
goto menu

:math_test
echo.
echo 🔢 數學問題求解
echo ==========================================
echo 範例問題：
echo - 解方程式：2x + 5 = 15
echo - 計算 25 的平方根
echo - 三角形面積公式是什麼？
echo.
set /p math_problem="請輸入數學問題: "
echo.
echo 🧮 數學代理正在計算...
docker exec agentic-app python -c "
from agents.math_agent import MathAgent
agent = MathAgent()
response = agent.solve_problem('%math_problem%')
print('🔢 數學代理回答:')
print(response)
"
echo.
pause
goto menu

:language_test
echo.
echo 📚 語言學習輔助
echo ==========================================
echo 範例問題：
echo - 解釋英文的過去完成式
echo - "Hello" 這個單字的用法
echo - 中文的聲調規則
echo.
set /p lang_question="請輸入語言學習問題: "
echo.
echo 📖 語言代理正在分析...
docker exec agentic-app python -c "
from agents.language_agent import LanguageAgent
agent = LanguageAgent()
response = agent.explain_grammar('%lang_question%')
print('📚 語言代理回答:')
print(response)
"
echo.
pause
goto menu

:agent_demo
echo.
echo 🤖 代理協作演示
echo ==========================================
echo 這個演示將展示不同代理如何協作處理複雜問題
echo.
echo 問題：解釋畢達哥拉斯定理並計算一個例子
echo.
echo 🔄 啟動代理協作...
docker exec agentic-app python -c "
print('📋 步驟 1: 語言代理解釋概念')
from agents.language_agent import LanguageAgent
lang_agent = LanguageAgent()
explanation = lang_agent.explain_grammar('畢達哥拉斯定理的概念和意義')
print(explanation)
print()

print('📋 步驟 2: 數學代理計算實例')
from agents.math_agent import MathAgent
math_agent = MathAgent()
calculation = math_agent.solve_problem('直角三角形兩邊分別是 3 和 4，求斜邊長度')
print(calculation)
"
echo.
pause
goto menu

:system_status
echo.
echo 📊 系統狀態檢查
echo ==========================================
echo 🔍 Docker 容器狀態:
docker ps --format "table {{.Names}}\t{{.Status}}"
echo.
echo 🔍 LLM 引擎配置:
docker exec agentic-app python -c "
import os
print(f'引擎類型: {os.environ.get(\"DEFAULT_LLM_ENGINE\", \"未設定\")}')
print(f'Gemini API: {\"已設定\" if os.environ.get(\"GEMINI_API_KEY\") else \"未設定\"}')
print(f'Ollama URL: {os.environ.get(\"OLLAMA_BASE_URL\", \"未設定\")}')
"
echo.
echo 🔍 資源使用情況:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo.
pause
goto menu

:health_check
echo.
echo 🧪 快速健康檢查
echo ==========================================
call quick-test.bat
echo.
pause
goto menu

:end
echo.
echo 👋 感謝使用 Agentic Teaching System！
echo 🎉 希望您對系統功能滿意
pause
exit /b 0
