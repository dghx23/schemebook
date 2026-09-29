# SchemeBook

Independent South African medical-scheme directory and plain-language guide in
the RiskAtlas family. The public app serves `schemebook.riskatlas.co.za` at `/`.

The product history was extracted from `dghx23/SentrixDigital`; CMS data,
procedure vocabulary, templates and browser assets remain in this repository.
The indexed PMB DTP set is incomplete against the 271 conditions described by
CMS, and the site discloses that difference.

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

Production: `gunicorn --bind 0.0.0.0:$PORT app:app`.

Keep the existing shared Railway service as rollback until the dedicated
service and custom-domain cutover have passed smoke tests.
