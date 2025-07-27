@echo off
chcp 65001 >nul
title Agentic AI Chat Test

echo =============================================
echo       Agentic Teaching System - Test
echo =============================================
echo.

echo Testing basic AI response...
echo Question: What is 2+2?
echo.

docker exec agentic-app python chat_helper.py "What is 2+2?"

echo.
echo =============================================
echo Test complete! Press any key to continue...
pause >nul
