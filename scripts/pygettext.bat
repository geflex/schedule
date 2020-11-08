@echo off
call scripts/_setup_i18n.bat
python %PY_I18N_PATH%/pygettext.py -d schedule -o %LOCALES_PATH%/schedule.pot schedule
python %PY_I18N_PATH%/pygettext.py -d reversible -o %LOCALES_PATH%/reversible.pot --no-default-keywords --keyword=_c schedule
