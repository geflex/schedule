@echo off
call scripts/_setup_i18n.bat
python scripts/msgfmt.py %EN_LOCALES_PATH%/schedule.po
python scripts/msgfmt.py --reversed %EN_LOCALES_PATH%/reversible.po
