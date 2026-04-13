@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

echo [ATS] Initialisation...

set "FORCE_UPDATE=0"
if /I "%~1"=="--update" set "FORCE_UPDATE=1"

set "VENV_PY=.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
  echo [ATS] Creation de l'environnement virtuel...

  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -m venv .venv
  ) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
      python -m venv .venv
    ) else (
      echo [ERREUR] Python introuvable. Installez Python 3 puis relancez.
      pause
      exit /b 1
    )
  )

  if errorlevel 1 (
    echo [ERREUR] Impossible de creer le venv.
    pause
    exit /b 1
  )
)

if not exist "%VENV_PY%" (
  echo [ERREUR] Python du venv introuvable: %VENV_PY%
  pause
  exit /b 1
)

if "%FORCE_UPDATE%"=="1" (
  echo [ATS] Mise a jour forcee demandee (--update).
)

if not exist ".venv\.ats_ready" (
  echo [ATS] Premiere installation des dependances...
  "%VENV_PY%" -m pip install --upgrade pip
  "%VENV_PY%" -m pip install -e .
  if errorlevel 1 (
    echo [ERREUR] Installation echouee.
    pause
    exit /b 1
  )
  echo ok>".venv\.ats_ready"
) else (
  if "%FORCE_UPDATE%"=="1" (
    echo [ATS] Reinstallation/mise a jour des dependances...
    "%VENV_PY%" -m pip install --upgrade pip
    "%VENV_PY%" -m pip install -e .
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
"%VENV_PY%" -m streamlit run app.py

endlocal
