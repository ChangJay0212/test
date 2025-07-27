@echo off
title Agentic Teaching System - Interactive Test

echo ===========================================
echo   Agentic Teaching System - Interactive
echo ===========================================
echo.
echo Welcome! This is your AI teaching assistant.
echo You can ask questions in English or Chinese.
echo.
echo Examples:
echo - What is the difference between their, there, and they're?
echo - Explain Chinese idioms
echo - How can I improve my writing?
echo - Teach me about poetry
echo.
echo Commands:
echo - Type 'quit' or 'exit' to stop
echo - Type 'status' to check system health
echo.

:chat_loop
set /p question="Your question: "

if /i "%question%"=="quit" goto end
if /i "%question%"=="exit" goto end
if /i "%question%"=="q" goto end

if "%question%"=="" (
    echo Please enter a question.
    goto chat_loop
)

if /i "%question%"=="status" (
    echo.
    echo === System Status ===
    docker ps --format "table {{.Names}}\t{{.Status}}"
    echo.
    goto chat_loop
)

echo.
echo Processing your question...
echo -----------------------------------------

docker exec agentic-app python chat_helper.py "%question%"

echo -----------------------------------------
echo.
goto chat_loop

:end
echo.
echo Thank you for using Agentic Teaching System!
echo Have a great day!
pause
exit /b 0
