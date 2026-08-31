# As Oy Saunavaraus

A small sauna booking application for a Finnish housing company (taloyhtiö). Residents register,
reserve weekly sauna shifts, browse a resident directory and manage their own bookings.

This is the first project for the University of Helsinki course Cyber Security Base. The application
deliberately contains five security flaws from the OWASP Top 10 (2021). The fix for each flaw is
included in the code as a commented-out block right next to the flaw, so the flaw and its fix can be
compared in a single version.

## Requirements

- Python 3.11 or newer
- The Python packages listed in `requirements.txt` (only Django)

## Setup

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed.py
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

`seed.py` creates the database and a few residents with sample reservations. Running it again does
not create duplicates.

## Sample accounts

| Username | Password        | Role     |
|----------|-----------------|----------|
| liisa    | kissa123        | resident |
| matti    | kissa123        | resident |
| admin    | Sauna2026admin  | admin    |

## Security flaws

The flaws follow the OWASP Top 10 2021 list. In the source they are marked with a comment that
starts with `FLAW`, and the fix is on the following lines starting with `FIX`, commented out.

| # | OWASP 2021 category                        | Where |
|---|--------------------------------------------|-------|
| 1 | A01 Broken Access Control                  | `bookings/views.py` (`reservation_detail`, `cancel_reservation`) |
| 2 | A02 Cryptographic Failures                 | `bookings/hashers.py`, `PASSWORD_HASHERS` in `saunavaraus/settings.py` |
| 3 | A03 Injection                              | `bookings/views.py` (`directory`) |
| 4 | A05 Security Misconfiguration              | `saunavaraus/settings.py` (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`) |
| 5 | A07 Identification and Authentication Failures | `saunavaraus/settings.py` (`AUTH_PASSWORD_VALIDATORS`) |

Screenshots demonstrating each flaw before and after its fix are in the `screenshots/` folder.
