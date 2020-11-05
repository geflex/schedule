@echo off
call scripts/_setup_i18n.bat
python %I18N_PATH%/msgfmt.py -o %LOCALES_PATH%/schedule.mo %LOCALES_PATH%/schedule
