@echo off
echo Iniciando FastAPI (uvicorn)...
cd /d C:\Users\central\Desktop\streamlit\DASH CRD
call C:\Python39\Scripts\activate

start uvicorn auth_api:app --reload --port 8002

timeout /t 5 /nobreak > nul

echo Iniciando Streamlit...
streamlit run src/dashboard/app.py --server.port 9000