import re, sys, pathlib

src = pathlib.Path(sys.argv[1]).read_text()
out = pathlib.Path(sys.argv[2])
ACC = '#D4F25A'

helmet = re.search(r'<helmet>(.*?)</helmet>', src, re.S).group(1)
body = re.search(r'</helmet>(.*?)</x-dc>', src, re.S).group(1)

def rep(s, a, b, count=None):
    if a not in s:
        raise SystemExit('missing: ' + a[:80])
    return s.replace(a, b) if count is None else s.replace(a, b, count)

b = body
# root
b = re.sub(r'<div ref="\{\{setRoot\}\}" class="\{\{rootClass\}\}"', '<div id="root"', b)
b = re.sub(r' on(MouseMove|MouseOver|MouseDown|MouseUp|MouseLeave|MouseEnter)="\{\{(onMove|onOver|onDown|onUp|onLeave|onEnter)\}\}"', '', b)
b = rep(b, 'ref="{{setRing}}" class="{{ringClass}}"', 'id="ring" class="cur-ring"')
b = rep(b, 'ref="{{setDot}}"', 'id="dot"')
b = rep(b, '<span>{{hoverLabel}}</span>', '<span id="hl"></span>')
b = rep(b, 'ref="{{setBar}}"', 'id="bar"')
b = rep(b, 'ref="{{setTl}}"', 'id="tl"')
b = rep(b, 'ref="{{setTlFill}}"', 'id="tlfill"')
b = rep(b, 'ref="{{setMetrics}}"', 'id="metrics"')
b = rep(b, 'onClick="{{toggleSound}}" aria-pressed="{{soundPressed}}"', 'id="snd" aria-pressed="false"')
b = rep(b, 'data-cursor="{{soundCursor}}"', 'data-cursor="Sound"')
b = rep(b, '<sc-if value="{{soundOn}}" hint-placeholder-val="{{ false }}">', '<span id="sndOn" hidden>')
b = rep(b, '<sc-if value="{{soundOff}}" hint-placeholder-val="{{ true }}">', '<span id="sndOff" style="display:flex">')
b = b.replace('</sc-if>', '</span>', 2)
b = rep(b, 'onClick="{{copy}}"', 'id="copy"')
b = rep(b, '<span>{{copyLabel}}</span>', '<span id="copyl">Copy email</span>')
b = rep(b, 'onMouseMove="{{mag}}" onMouseLeave="{{magOut}}"', 'data-mag')
b = rep(b, ' onMouseMove="{{spot}}"', '')
b = rep(b, 'transform: translateY({{wordY}})"', 'transform: translateY(0em)" id="words"')
for k, v in (('a', 97), ('b', 10), ('c', 5), ('d', 15)):
    b = rep(b, '{{c.%s}}' % k, '<span data-count="%d">%d</span>' % (v, v))

# stage loop -> static buttons
loop = re.search(r'<sc-for list="\{\{stages\}\}".*?</sc-for>', b, re.S).group(0)
labels = ['Ingest', 'Embed', 'Retrieve', 'Reason', 'Verify', 'Deliver']
arrow = '<svg aria-hidden="true" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="#4A504C" stroke-width="1.5"><path d="M3 8h10M9 4l4 4-4 4"></path></svg>'
parts = []
for i, l in enumerate(labels):
    on = ' on' if i == 0 else ''
    parts.append('<button type="button" class="pnode%s" data-i="%d" data-cursor="Step" aria-pressed="%s"><b>0%d</b>%s</button>' % (on, i, 'true' if i == 0 else 'false', i + 1, l))
    if i < len(labels) - 1:
        parts.append(arrow)
b = b.replace(loop, '\n'.join(parts))
b = rep(b, '<div style="position: absolute; left: 0; top: 0; height: 2px; background: {{accent}}; opacity: .35; width: {{stage.pct}};', '<div id="spct" style="position: absolute; left: 0; top: 0; height: 2px; background: {{accent}}; opacity: .35; width: 17%;')
b = b.replace('{{stage.num}}', '<span class="snum">01</span>')
b = rep(b, '{{stage.title}}', '<span id="stitle">Ingest the standards</span>')
b = rep(b, '{{stage.body}}', '<span id="sbody">Python pipelines break NCERT and US Common Core into curriculum nodes — subject, grade band and learning objective — ready to embed.</span>')
b = b.replace('{{accent}}', ACC)

# résumé buttons
dl = '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M8 2v9M4 7l4 4 4-4M3 14h10"></path></svg>'
hero_anchor = 'Skip to the work\n<svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.75"><path d="M3 8h10M9 4l4 4-4 4"></path></svg>\n</a>'
b = rep(b, hero_anchor, hero_anchor + '\n<a class="btn-g" href="/Sushma-Karnati-Resume.pdf" download data-cursor="Save" style="display: flex; align-items: center; gap: 10px; padding: 16px 24px; border: 1px solid #3A3F3C; font-weight: 500; font-size: 15px">Résumé\n' + dl + '\n</a>', 1)
gh = '<a class="btn-g diag" href="https://github.com/karnatisushma"'
b = rep(b, gh, '<a class="btn-g" href="/Sushma-Karnati-Resume.pdf" download data-cursor="Save" style="display: flex; align-items: center; gap: 10px; padding: 20px 22px; border: 1px solid #3A3F3C; font-weight: 500; font-size: 16px">Résumé\n' + dl + '\n</a>\n' + gh, 1)

left = re.findall(r'\{\{[^}]*\}\}|<sc-|</sc-', b)
if left:
    raise SystemExit('unconverted: %r' % left[:10])

js = pathlib.Path(sys.argv[3]).read_text()
desc = 'Sushma Karnati — AI engineer building production RAG pipelines, multi-agent systems and generative-AI products with structured outputs, validation and observability.'
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sushma Karnati — AI Engineer</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0C0E0D">
<meta property="og:type" content="website">
<meta property="og:title" content="Sushma Karnati — AI Engineer">
<meta property="og:description" content="I build LLM systems that hold up in production. RAG, agents and generative AI — measured in outcomes.">
<meta property="og:image" content="/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Sushma Karnati — AI Engineer">
<meta name="twitter:image" content="/og.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{helmet.strip()}
</head>
<body>
{b.strip()}
<script>
{js}
</script>
</body>
</html>
'''
out.write_text(html)
print('ok', len(html))
