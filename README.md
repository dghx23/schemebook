# SchemeBook

Independent South African medical-scheme directory and plain-language guide in
the RiskAtlas family. The public app serves `schemebook.riskatlas.co.za` at `/`.

The product history was extracted from `dghx23/SentrixDigital`; CMS data,
procedure vocabulary, templates and browser assets remain in this repository.
The indexed PMB DTP set is incomplete against the 271 conditions described by
CMS, and the site discloses that difference.

## Source and history dependencies

- `cms_authority.py` reads the committed CMS scheme, PMB and DTP files in
  `data/`; `term_slugs.py` supports its lookup paths.
- `core_common_procedures.py` supplies the shared procedure vocabulary for
  Explore. `coreza_upfs.py` reads `data/coreza/upfs_source_index.json` for the
  public cost guide.
- The original `schemebook_sync.py` materialisation, `ingest_log.py` audit
  trail, command line sync script, and scheduled GitHub workflow are included.
  They refresh and commit the versioned snapshot in this repository. Other
  products do not yet consume that snapshot directly.
- The browser client loads all five files in `static/schemebook/`; all eight
  public templates and their shared base are included.

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
