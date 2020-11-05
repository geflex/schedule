@echo off
call scripts/_setup_i18n.bat
msgmerge --update %EN_LOCALES_PATH%/schedule.po %LOCALES_PATH%/schedule.pot
