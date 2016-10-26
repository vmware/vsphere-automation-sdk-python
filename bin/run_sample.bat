@echo off
setlocal ENABLEDELAYEDEXPANSION
:: Clear the command-prompt screen
cls
set SRCDIR=%cd%\..\samples\src
set LIBDIR=%cd%\..\lib
set PYTHONPATH=%PYTHONPATH%;%SRCDIR%
setlocal DisableDelayedExpansion
:: Run the sample
python %*
endlocal
