@echo off
cd /d C:\Users\central\Desktop\streamlit\DASH CRD
call C:\Python39\Scripts\activate
echo Iniciando Streamlit...
streamlit run src/dashboard/app.py --server.port 9000