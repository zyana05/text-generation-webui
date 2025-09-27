@echo off
echo Activating mamba environment 'textgen'...
call mamba activate textgen

echo Starting FastAPI server...
python ../fastapi/server_fastapi.py

pause