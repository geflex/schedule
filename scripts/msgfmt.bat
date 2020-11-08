@echo off
call scripts/_setup_i18n.bat
python %PY_I18N_PATH%/msgfmt.py -o %EN_LOCALES_PATH%/schedule.mo %EN_LOCALES_PATH%/schedule
python %PY_I18N_PATH%/msgfmt.py -o %EN_LOCALES_PATH%/reversible.mo %EN_LOCALES_PATH%/reversible
