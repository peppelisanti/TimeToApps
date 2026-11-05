# Time to Apps – sito sviluppatore

Sito statico in 7 lingue (en, it, de, fr, es, pt-BR, pt-PT). Si rigenera con:

    python3 build.py            # scrive docs/ (GitHub Pages: branch main, cartella /docs)

- `strings.py`  testi dell'interfaccia e descrizioni delle app (7 lingue)
- `content/legal/<app>/<privacy|terms>.<lingua>.html`  testi legali; se manca una lingua la pagina mostra l'inglese con un avviso
- `assets/img/<lingua>/<app>-s01.jpg`, `-s03.jpg`  screenshot nella lingua della pagina: le slide 01 e 03 dell'App Store, rigenerate con `python3 shots.py` (serve Pillow e i checkout iOS in `~/Developer/iOS/<App>`)
- `build.py`  link App Store / Google Play in `APPS` (se vuoti compare "In arrivo")
- Dominio: timetoapps.app (default in build.py; sovrascrivibile con SITE_URL e CNAME)
