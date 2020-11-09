@echo off
call scripts\_setup_i18n.bat

python %PY_I18N_PATH%\pygettext.py -d schedule -o %LOCALES_PATH%\schedule.pot schedule
python %PY_I18N_PATH%\pygettext.py -d reversible -o %LOCALES_PATH%\reversible.pot --no-default-keywords --keyword=_c schedule

for %%d in (schedule, reversible) do (
    for /f %%l in ('dir /b /d /a:d %LOCALES_PATH%') do (
        msgmerge --update %LOCALES_PATH%\%%l\LC_MESSAGES\%%d.po %LOCALES_PATH%\%%d.pot
    )
)
