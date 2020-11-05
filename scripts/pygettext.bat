@echo off
call scripts/_setup_i18n.bat
python %PY_I18N_PATH%/pygettext.py -d schedule -o schedule/locales/schedule.pot schedule
