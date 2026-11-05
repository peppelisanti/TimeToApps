#!/usr/bin/env python3
"""Time to Apps – static site generator. Usage: python3 build.py  → writes docs/ (GitHub Pages)."""
import html, os, re, shutil
from pathlib import Path
from strings import *

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
DOMAIN = os.environ.get("SITE_URL", "https://timetoapps.app").rstrip("/")   # e.g. https://timetoapps.app (optional, for hreflang/canonical)
EMAIL = "support.timetoapps@gmail.com"

# Store links: fill in when the apps are live. None → "coming soon" badge.
APPS = {
 "payday": dict(name="Time to Payday", ios=None, android=None, bg="#0F3A2E", fg="#fff", fg2="#C9DDD2", accent="#A6E08A", on_accent="#0F3A2E", action="#136B4A", letter="P"),
 "sub": dict(name="Time to Sub", ios=None, android=None, bg="#0D2E3F", fg="#fff", fg2="#C3D6DD", accent="#F2986E", on_accent="#0D2E3F", action="#17668A", letter="S"),
 "restructure": dict(name="Time to Restructure", ios=None, android=None, bg="#241C42", fg="#fff", fg2="#CFC8E8", accent="#F5C451", on_accent="#241C42", action="#4B3BA6", letter="R"),
}
E = html.escape

def rel(depth): return "../" * depth if depth else "./"

def fmt_date(en, lang):
    m = re.match(r"(\d+) (\w+) (\d{4})", en)
    d, mon, y = m.groups()
    return DATEFMT[lang].format(d=d, m=MONTHS[lang][MONTHS["en"].index(mon)], y=y)

def lang_switcher(lang, tail, depth):
    items = ""
    for l in LANGS:
        cur = ' aria-current="true"' if l == lang else ""
        items += '<a href="%s%s/%s" hreflang="%s" lang="%s"%s>%s</a>' % (rel(depth), l, tail, l, l, cur, LANG_NAMES[l])
    return '<details class="langs"><summary aria-label="%s">%s</summary><div>%s</div></details>' % (E(UI[lang]["lang_label"]), LANG_NAMES[lang], items)

def page(lang, tail, depth, title, body, theme=None, desc=None):
    u = UI[lang]
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{DOMAIN}/{l}/{tail}">' for l in LANGS) if DOMAIN else ""
    if DOMAIN: alts += f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}/en/{tail}"><link rel="canonical" href="{DOMAIN}/{lang}/{tail}">'
    r = rel(depth)
    theme_attr = f' data-app="{theme}"' if theme else ""
    return f'''<!DOCTYPE html>
<html lang="{lang}"{theme_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{E(title)}</title>
<meta name="description" content="{E(desc or u["desc_meta"])}">
{alts}
<link rel="icon" href="{r}assets/img/payday-icon.png">
<link rel="stylesheet" href="{r}assets/legal.css">
<link rel="stylesheet" href="{r}assets/site.css">
</head>
<body>
<div class="site">
<header class="top">
  <a class="brand" href="{r}{lang}/"><span class="mark" aria-hidden="true">T</span>Time to Apps</a>
  <nav>
    <a href="{r}{lang}/#apps">{E(u["nav_apps"])}</a>
    <a href="{r}{lang}/#legal">{E(u["nav_legal"])}</a>
    <a href="{r}{lang}/#contact">{E(u["nav_contact"])}</a>
    {lang_switcher(lang, tail, depth)}
  </nav>
</header>
{body}
<footer id="contact" class="foot">
  <span>© Giuseppe Lisanti</span>
  <a href="mailto:{EMAIL}">{EMAIL}</a>
</footer>
</div>
</body>
</html>
'''

def store_buttons(lang, key):
    a, u = APPS[key], UI[lang]
    out = []
    if a["ios"]: out.append(f'<a class="btn solid" href="{a["ios"]}">{E(u["app_store"])}</a>')
    if a["android"]: out.append(f'<a class="btn ghost" href="{a["android"]}">{E(u["google_play"])}</a>')
    if not out: out.append(f'<span class="btn ghost soon">{E(u["soon"])}</span>')
    return "".join(out)

def home(lang):
    u, depth, r = UI[lang], 1, "../"
    cards = ""
    for k, a in APPS.items():
        tag, desc, _ = APPCOPY[k][lang]
        cards += f'''<a class="appcard" href="{k}/" style="--bg:{a["bg"]};--fg:{a["fg"]};--fg2:{a["fg2"]}">
  <div class="apphead"><img src="{r}assets/img/{k}-icon.png" alt="" width="64" height="64"><div><div class="appname">{a["name"]}</div><div class="apptag">{E(tag)}</div></div></div>
  <p>{E(desc)}</p>
  <img class="shot" src="{r}assets/img/{lang}/{k}-s01.jpg" alt="" loading="lazy">
</a>'''
    legal = ""
    for k, a in APPS.items():
        legal += f'<div><strong>{a["name"]}</strong><a href="{k}/privacy/" style="color:{a["action"]}">{E(u["privacy"])}</a><a href="{k}/terms/" style="color:{a["action"]}">{E(u["terms"])}</a></div>'
    body = f'''<main>
<section class="hero-home"><p class="eyebrow">{E(u["eyebrow"])}</p><h1>{E(u["h1"])}</h1><p class="lead">{E(u["lead"])}</p>
<div class="cta"><a class="btn solid dark" href="#apps">{E(u["cta_apps"])}</a><a class="btn ghost dark" href="#contact">{E(u["cta_contact"])}</a></div></section>
<section id="apps" class="grid3">{cards}</section>
<section class="feats"><div><h3>{E(u["f1t"])}</h3><p>{E(u["f1d"])}</p></div><div><h3>{E(u["f2t"])}</h3><p>{E(u["f2d"])}</p></div><div><h3>{E(u["f3t"])}</h3><p>{E(u["f3d"])}</p></div></section>
<section id="legal" class="legalbox"><h2>{E(u["legal_h"])}</h2><p>{E(u["legal_p"])}</p><div class="grid3 legalgrid">{legal}</div></section>
</main>'''
    return page(lang, "", 1, "Time to Apps", body)

def app_page(lang, k):
    u, a, r = UI[lang], APPS[k], "../../"
    tag, desc, feats = APPCOPY[k][lang]
    hl = APPHIGHLIGHT.get(k, {}).get(lang)
    highlight = f'<p class="highlight">{E(hl)}</p>' if hl else ""
    f = "".join(f"<div><h3>{E(t)}</h3><p>{E(d)}</p></div>" for t, d in feats)
    body = f'''<main>
<p class="back"><a href="../">{E(u["back_all"])}</a></p>
<section class="apphero" style="--bg:{a["bg"]};--fg:{a["fg"]};--fg2:{a["fg2"]};--accent:{a["accent"]}">
  <div class="apphero-text">
    <img src="{r}assets/img/{k}-icon.png" alt="" width="88" height="88">
    <h1>{a["name"]}</h1><p class="lead">{E(tag)}. {E(desc)}</p>{highlight}
    <div class="cta">{store_buttons(lang, k)}</div>
  </div>
  <div class="shots"><img src="{r}assets/img/{lang}/{k}-s01.jpg" alt="" loading="lazy"><img src="{r}assets/img/{lang}/{k}-s03.jpg" alt="" loading="lazy"></div>
</section>
<section class="feats cards">{f}</section>
<section class="legalbox row"><div><h2>{E(u["legal_h"])}</h2><p>{E(u["legal_p"])}</p></div>
<div class="cta"><a class="btn action" style="--action:{a["action"]}" href="privacy/">{E(u["privacy"])}</a><a class="btn outline" style="--action:{a["action"]}" href="terms/">{E(u["terms"])}</a></div></section>
</main>'''
    return page(lang, f"{k}/", 2, f'{a["name"]} – {tag}', body, desc=desc)

def legal_page(lang, k, doc):
    u, a = UI[lang], APPS[k]
    src = ROOT / "content" / "legal" / k
    fp = src / ("%s.%s.html" % (doc, lang))
    translated = fp.exists()
    en = (src / ("%s.en.html" % doc)).read_text(encoding="utf-8")
    text = fp.read_text(encoding="utf-8") if translated else en
    date_en = re.match(r"<!-- updated: (.+?) -->", en).group(1)
    text = re.sub(r"^<!-- updated: .+? -->\n", "", text)
    title = u["privacy"] if doc == "privacy" else u["terms"]
    note = ""
    if lang != "en":
        if translated:
            note = '<p class="note">%s <a href="../../../en/%s/%s/" hreflang="en">%s</a></p>' % (E(u["tr_note"]), k, doc, E(u["view_en"]))
        else:
            note = '<p class="note">%s <a href="../../../en/%s/%s/" hreflang="en">%s</a></p>' % (E(u["tr_missing"]), k, doc, E(u["view_en"]))
    cp = ' aria-current="page"' if doc == "privacy" else ""
    ct = ' aria-current="page"' if doc == "terms" else ""
    body = """<main class="legalpage">
<p class="back"><a href="../">&larr; %s</a></p>
<div class="tabs"><a href="../privacy/"%s>%s</a><a href="../terms/"%s>%s</a></div>
<header class="hero"><h1>%s</h1><p>%s &middot; %s: %s</p></header>
%s
<article class="card">
%s
</article>
</main>""" % (a["name"], cp, E(u["privacy"]), ct, E(u["terms"]), E(title), a["name"], E(u["last_updated"]), fmt_date(date_en, lang), note, text)
    return page(lang, "%s/%s/" % (k, doc), 3, "%s — %s" % (title, a["name"]), body, theme=k)

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    n = 0
    for lang in LANGS:
        write(OUT / lang / "index.html", home(lang)); n += 1
        for k in APPS:
            write(OUT / lang / k / "index.html", app_page(lang, k)); n += 1
            for doc in ("privacy", "terms"):
                write(OUT / lang / k / doc / "index.html", legal_page(lang, k, doc)); n += 1
    langs_js = str(LANGS).replace("'", '"')
    write(OUT / "index.html", f'''<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Time to Apps</title><meta http-equiv="refresh" content="1;url=en/">
<script>(function(){{var L={langs_js},p=(navigator.languages||[navigator.language||"en"]);
for(var i=0;i<p.length;i++){{var c=p[i],f=null;
for(var j=0;j<L.length;j++){{if(L[j].toLowerCase()===c.toLowerCase())f=L[j];}}
if(!f){{var b=c.slice(0,2).toLowerCase();if(b==="pt")f=(c.toLowerCase()==="pt-br")?"pt-BR":"pt-PT";else for(var k=0;k<L.length;k++)if(L[k]===b)f=b;}}
if(f){{location.replace(f+"/");return;}}}}location.replace("en/");}})();</script></head>
<body><p><a href="en/">Time to Apps</a></p></body></html>''')
    write(OUT / ".nojekyll", "")
    write(OUT / "CNAME", os.environ.get("CNAME", "timetoapps.app"))
    print(f"Generated {n} pages in {OUT}")

if __name__ == "__main__":
    main()
