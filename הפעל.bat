@echo off
chcp 65001 > nul
echo מתקין תלויות...
pip install flask yt-dlp
echo.
echo פותח את האתר בדפדפן...
start http://localhost:5000
python app.py
pause
