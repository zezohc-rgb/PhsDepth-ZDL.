@echo off
setlocal
title Filter Delay Boost - instalador USB local
echo Abrindo o instalador local do Filter Delay Boost...
echo Mantenha esta janela aberta enquanto usar a ferramenta.
echo.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0SERVIDOR_LOCAL.ps1"
if errorlevel 1 (
  echo.
  echo Nao foi possivel iniciar. Consulte MANUAL.html ou MANUAL.txt.
  pause
)
endlocal
