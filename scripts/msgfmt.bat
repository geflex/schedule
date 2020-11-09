@echo off
call scripts/_setup_i18n.bat
python scripts/msgfmt.py -o %EN_LOCALES_PATH%/schedule.mo %EN_LOCALES_PATH%/schedule.po
python scripts/msgfmt.py -o %EN_LOCALES_PATH%/reversible.mo %EN_LOCALES_PATH%/reversible.po
python scripts/msgfmt.py -o %EN_LOCALES_PATH%/reversed.mo %EN_LOCALES_PATH%/reversed.po
