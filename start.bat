@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

echo [ATS] Initialisation...

set "FORCE_UPDATE=0"
if /I "%~1"=="--update" set "FORCE_UPDATE=1"

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

if "%FORCE_UPDATE%"=="1" (
  echo [ATS] Mise a jour forcee demandee (--update).
)

if not exist ".venv\.ats_ready" (
  echo [ATS] Premiere installation des dependances...
  python -m pip install --upgrade pip
  pip install -e .
  if errorlevel 1 (
    echo [ERREUR] Installation echouee.
    pause
    exit /b 1
  )
  echo ok>".venv\.ats_ready"
) else (
  if "%FORCE_UPDATE%"=="1" (
    echo [ATS] Reinstallation/mise a jour des dependances...
    python -m pip install --upgrade pip
    pip install -e .
    if errorlevel 1 (
      echo [ERREUR] Mise a jour echouee.
      pause
      exit /b 1
    )
  ) else (
    echo [ATS] Dependances deja installees. Aucun telechargement majeur attendu.
    echo [ATS] Utilisez start.bat --update pour forcer une mise a jour.
  )
)

echo [ATS] Demarrage de l'application...
echo [ATS] Ouvrez ce lien: http://localhost:8501
streamlit run app.py

endlocal
