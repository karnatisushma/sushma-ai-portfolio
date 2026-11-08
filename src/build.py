"""Build the static site from the design canvas source.

Usage: python3 src/build.py src/Main.dc.html index.html
The canvas file keeps its interactivity in an `init(root)` function between
/*INIT-START*/ and /*INIT-END*/ markers; this script lifts the markup and that
function into a plain HTML page with SEO metadata.
"""
import re, sys, pathlib, json

src = pathlib.Path(sys.argv[1]).read_text()
out = pathlib.Path(sys.argv[2])
SITE = 'https://sushma-ai.vercel.app/'

helmet = re.search(r'<helmet>(.*?)</helmet>', src, re.S).group(1).strip()
body = re.search(r'</helmet>(.*?)</x-dc>', src, re.S).group(1).strip()
body = body.replace(' ref="{{setRoot}}"', '')
left = re.findall(r'\{\{[^}]*\}\}|<sc-|<dc-import', body)
if left:
    raise SystemExit('unconverted template syntax: %r' % left[:5])
js = re.search(r'/\*INIT-START\*/(.*?)/\*INIT-END\*/', src, re.S).group(1).strip()

title = 'Sushma Karnati — AI Engineer | RAG, Multi-Agent Systems & LLM Validation'
desc = ('Portfolio of Sushma Karnati, AI engineer in Hyderabad building production RAG pipelines, '
        'multi-agent systems and multimodal AI products like PocketPins Smart Collections with structured outputs, validation and observability.')
ld = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Sushma Karnati",
    "jobTitle": "AI Engineer",
    "url": SITE,
    "image": SITE + "og.png",
    "email": "mailto:sushmakarnati14@gmail.com",
    "address": {"@type": "PostalAddress", "addressLocality": "Hyderabad", "addressCountry": "IN"},
    "worksFor": [{"@type": "Organization", "name": "Buntikki Technologies", "url": "https://www.buntikki.com/"}, {"@type": "Organization", "name": "Arna Intelligence"}],
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "JNTU Hyderabad"},
    "knowsAbout": ["Retrieval-Augmented Generation", "Multi-agent systems", "LLM evaluation", "LangChain",
                   "Gemini", "Multimodal AI", "FastAPI", "pgvector", "Computer vision"],
    "sameAs": ["https://github.com/karnatisushma", "https://linkedin.com/in/sushmakarnati"]
}
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Sushma Karnati">
<meta name="keywords" content="Sushma Karnati, AI engineer, RAG, retrieval-augmented generation, multi-agent systems, LLM, LangChain, Gemini, FastAPI, Hyderabad">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{SITE}">
<meta name="theme-color" content="#0B0D0C">
<meta name="color-scheme" content="dark light">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="Sushma Karnati">
<meta property="og:url" content="{SITE}">
<meta property="og:title" content="Sushma Karnati — AI Engineer">
<meta property="og:description" content="I build LLM systems that hold up in production — RAG, agents and guardrails, measured in outcomes.">
<meta property="og:image" content="{SITE}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Sushma Karnati — I build LLM systems that hold up in production.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Sushma Karnati — AI Engineer">
<meta name="twitter:description" content="I build LLM systems that hold up in production — RAG, agents and guardrails.">
<meta name="twitter:image" content="{SITE}og.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script>try{{var t=localStorage.getItem('sk-theme')||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');document.documentElement.setAttribute('data-pre',t)}}catch(e){{}}</script>
{helmet}
<style>html[data-pre=light] body{{background:#F4F3EE}}html[data-pre=dark] body{{background:#0B0D0C}}</style>
</head>
<body>
{body}
<script>
{js}
init(document.getElementById('root'));
</script>
</body>
</html>
'''
out.write_text(html)
print('built', out, len(html))
