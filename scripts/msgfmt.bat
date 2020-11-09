@echo off
call scripts/_setup_i18n.bat

for /f %%l in ('dir /b /d /a:d %LOCALES_PATH%') do (
    python scripts/msgfmt.py %LOCALES_PATH%\%%l\LC_MESSAGES\schedule.po
    python scripts/msgfmt.py --reversed %LOCALES_PATH%\%%l\LC_MESSAGES\reversible.po
)

