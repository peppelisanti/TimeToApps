# Time to Apps – sito sviluppatore (timetoapps.app)

Sito statico in 7 lingue (en, it, de, fr, es, pt-BR, pt-PT), generato da `build.py` in `docs/` per GitHub Pages.
Leggi README.md per la struttura. Rigenera sempre con `python3 build.py` dopo ogni modifica a strings/content/assets.

## Stato
- Fatto: home, pagine app (Payday, Sub, Restructure), Privacy/Termini per app, selettore lingua, CNAME timetoapps.app, canonical/hreflang.
- Dominio timetoapps.app comprato su Cloudflare. Repo pubblico github.com/peppelisanti/TimeToApps (main), Pages da main /docs con dominio timetoapps.app (2026-11-05). DNS Cloudflare (solo DNS, nuvola grigia) e HTTPS forzato: il sito è online su https://timetoapps.app (www → apex).
- Traduzioni legali: SOLO `content/legal/payday/privacy.it.html` (pilota, in attesa di approvazione dell'utente su tono e termini).
  Mancano: 6 documenti (payday/sub/restructure × privacy/terms) × 6 lingue (it, de, fr, es, pt-BR, pt-PT), tranne il pilota.
  Sorgenti inglesi in content/legal/<app>/<doc>.en.html (prima riga: <!-- updated: ... -->). Ogni traduzione mantiene struttura h2/p,
  email e Bundle ID invariati, e la prima riga commento non va copiata. Dove manca una lingua la pagina mostra l'inglese con avviso.
- Descrizioni di Sub e Restructure in strings.py (APPCOPY) scritte da Claude: da far verificare all'utente.
- Link App Store / Google Play: vuoti in build.py (APPS) → "In arrivo".

## Decisioni
- Gli URL legali già inviati agli store (peppelisanti.github.io/<App>-legal) restano online e invariati.
- I link store/app verso il nuovo sito si cambiano solo con la nuova build di ogni app.
- Email di supporto per ora support.timetoapps@gmail.com (eventuale alias sul dominio con Cloudflare Email Routing, poi).

## Da fare (richiede account dell'utente)
1. Fatto: repo e push.
2. Fatto: Pages (main, /docs, timetoapps.app), certificato per timetoapps.app e www, Enforce HTTPS.
3. Fatto: Cloudflare DNS (nuvola grigia): 4 record A @ → 185.199.108.153/109.153/110.153/111.153; CNAME www → peppelisanti.github.io.
4. Completare le traduzioni legali e rigenerare.
