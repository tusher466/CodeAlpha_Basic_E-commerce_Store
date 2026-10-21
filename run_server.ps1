Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      Starting CodeAlpha E-Commerce Development Server" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application URL:     http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "Admin Dashboard URL: http://127.0.0.1:8000/admin/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Demo Customer: johndoe / password123" -ForegroundColor White
Write-Host "Admin Super:   admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor DarkGray
Write-Host ""

if (Test-Path ".\.venv\Scripts\python.exe") {
    & ".\.venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
} else {
    python manage.py runserver 127.0.0.1:8000
}
