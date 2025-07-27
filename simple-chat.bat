@echo off
chcp 65001 >nul

echo ==========================================
echo   Agentic Teaching System - Simple Test
echo ==========================================
echo.

:start
echo Enter your question (or 'quit' to exit):
set /p question="Your question: "

if /i "%question%"=="quit" goto end
if /i "%question%"=="exit" goto end
if "%question%"=="" goto start

echo.
echo Processing your question...
echo ==========================================

docker exec agentic-app python -c "
from llm_engines.factory import LLMEngineFactory
try:
    engine = LLMEngineFactory.create_for_agent('english_teacher')
    response = engine.generate_response('%question%')
    print('AI Response:')
    print(response)
except Exception as e:
    print('Error:', str(e))
    print('Please check if the system is running properly.')
"

echo ==========================================
echo.
goto start

:end
echo.
echo Thank you for using the system!
pause
