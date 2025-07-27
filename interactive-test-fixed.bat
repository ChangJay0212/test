@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ===============================================
echo   Agentic Teaching System - Interactive Test
echo ===============================================
echo.
echo This script lets you test the system features
echo.

:menu
echo ==========================================
echo Please select a test option:
echo.
echo 1. Simple Chat Test
echo 2. English Teaching Test  
echo 3. Chinese Teaching Test
echo 4. System Status Check
echo 5. Quick Health Check
echo 6. Simple Interactive Mode
echo 0. Exit
echo.
set /p choice="Enter your choice (0-6): "

if "%choice%"=="1" goto chat_test
if "%choice%"=="2" goto english_test
if "%choice%"=="3" goto chinese_test
if "%choice%"=="4" goto system_status
if "%choice%"=="5" goto health_check
if "%choice%"=="6" goto simple_interactive
if "%choice%"=="0" goto end
goto menu

:chat_test
echo.
echo === Simple Chat Test ===
set /p question="Ask any question: "
echo.
echo AI is thinking...
docker exec agentic-app python -c "from llm_engines.factory import LLMEngineFactory; engine = LLMEngineFactory.create_for_agent('english_teacher'); response = engine.generate_response('%question%'); print('AI Response:'); print(response)"
echo.
pause
goto menu

:english_test
echo.
echo === English Teaching Test ===
echo Try questions like:
echo - What is the difference between their, there, and they're?
echo - How do I improve my writing skills?
echo - Explain the past perfect tense
echo.
set /p eng_question="Enter English question: "
echo.
echo English Teacher is responding...
docker exec agentic-app python -c "from llm_engines.factory import LLMEngineFactory; engine = LLMEngineFactory.create_for_agent('english_teacher'); response = engine.generate_response('english: %eng_question%'); print('English Teacher:'); print(response)"
echo.
pause
goto menu

:chinese_test
echo.
echo === Chinese Teaching Test ===
echo Try questions like:
echo - What are Chinese idioms?
echo - Explain Li Bai's poetry
echo - Chinese grammar rules
echo.
set /p chi_question="Enter Chinese question: "
echo.
echo Chinese Teacher is responding...
docker exec agentic-app python -c "from llm_engines.factory import LLMEngineFactory; engine = LLMEngineFactory.create_for_agent('chinese_teacher'); response = engine.generate_response('chinese: %chi_question%'); print('Chinese Teacher:'); print(response)"
echo.
pause
goto menu

:system_status
echo.
echo === System Status ===
echo.
echo Docker Containers:
docker ps --format "table {{.Names}}\t{{.Status}}"
echo.
echo LLM Engine Configuration:
docker exec agentic-app python -c "import os; print('Engine:', os.environ.get('DEFAULT_LLM_ENGINE', 'Not set')); print('Gemini API:', 'Set' if os.environ.get('GEMINI_API_KEY') else 'Not set'); print('Ollama URL:', os.environ.get('OLLAMA_BASE_URL', 'Not set'))"
echo.
pause
goto menu

:health_check
echo.
echo === Quick Health Check ===
call quick-test.bat
echo.
pause
goto menu

:simple_interactive
echo.
echo === Simple Interactive Mode ===
echo Type 'quit' to return to menu
echo.
:interactive_loop
set /p user_input="Your question: "
if /i "%user_input%"=="quit" goto menu
if /i "%user_input%"=="exit" goto menu
echo.
echo Processing...
docker exec agentic-app python -c "from llm_engines.factory import LLMEngineFactory; engine = LLMEngineFactory.create_for_agent('english_teacher'); response = engine.generate_response('%user_input%'); print('Response:'); print(response)"
echo.
goto interactive_loop

:end
echo.
echo Thank you for using Agentic Teaching System!
pause
exit /b 0
