@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

echo [ATS] Initialisation...

if not exist ".venv\Scripts\python.exe" (
  echo [ATS] Creation de l'environnement virtuel...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo [ERREUR] Impossible de creer le venv.
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERREUR] Impossible d'activer le venv.
  pause
  exit /b 1
)

echo [ATS] Installation / mise a jour des dependances...
python -m pip install --upgrade pip
pip install -e .
if errorlevel 1 (
  echo [ERREUR] Installation echouee.
  pause
  exit /b 1
)

echo [ATS] Demarrage de l'application...
echo [ATS] Ouvrez ce lien: http://localhost:8501
streamlit run app.py

endlocal
