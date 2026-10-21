@echo off
echo ========================================================
echo       Starting CodeAlpha E-Commerce Development Server
echo ========================================================
echo.
echo Application will be available at: http://127.0.0.1:8000/
echo Admin Dashboard at:             http://127.0.0.1:8000/admin/
echo.
echo Demo User:     johndoe / password123
echo Admin User:    admin / admin123
echo.
echo Press Ctrl+C in this terminal window to stop the server.
echo.

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
) else (
    python manage.py runserver 127.0.0.1:8000
)
pause
