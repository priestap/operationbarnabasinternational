"""Build the static site into docs/ from a local WordPress export; never publish the export itself."""
import sys, re, html, json, shutil
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'docs'
ns={'wp':'http://wordpress.org/export/1.2/','content':'http://purl.org/rss/1.0/modules/content/'}
source=Path(sys.argv[1]) if len(sys.argv)>1 else None
if not source: raise SystemExit('Usage: python3 scripts/build.py /path/to/export.xml')

SITE='Operation Barnabas International'
DOMAIN='https://operationbarnabasinternational.com'
FACEBOOK='https://www.facebook.com/operation.barnabas.international/'
DONATE='https://advancingnativemissions.com/your-part/donate/'
# Jerry's existing Mailchimp list (the same one the WordPress site used).
MAILCHIMP='https://facebook.us14.list-manage.com/subscribe/post?u=92c342cbb799c4a03fe7f8831&amp;id=76f34ed275'
MAILCHIMP_HONEYPOT='b_92c342cbb799c4a03fe7f8831_76f34ed275'
def subscribe_form(key):
 return f'''<form class="subscribe-form" action="{MAILCHIMP}" method="post" target="_blank"><label class="visually-hidden" for="subscribe-{key}">Email address</label><div class="subscribe-row"><input id="subscribe-{key}" type="email" name="EMAIL" autocomplete="email" placeholder="Your email address" required><button class="button" type="submit">Subscribe</button></div><div class="form-honeypot" aria-hidden="true"><input type="text" name="{MAILCHIMP_HONEYPOT}" tabindex="-1" value="" autocomplete="off"></div><p class="subscribe-status" role="status" aria-live="polite"></p></form>'''
def subscribe_band(key):
 return f'<section class="subscribe" id="subscribe" aria-labelledby="subscribe-title-{key}"><div><p class="eyebrow">Stay connected</p><h2 id="subscribe-title-{key}">Get Jerry’s devotionals &amp; news</h2><p>Encouragement and reports from the field, sent to your inbox. Unsubscribe anytime.</p></div>{subscribe_form(key)}</section>'
# Paste a Formspree endpoint (https://formspree.io/f/…) here to turn on the contact form.
FORM_ENDPOINT=''

# Rebuild from scratch, keeping the CNAME GitHub Pages writes for the custom domain.
OUT.mkdir(exist_ok=True)
for p in OUT.iterdir():
 if p.name!='CNAME': shutil.rmtree(p) if p.is_dir() else p.unlink()
# Only resized photos with kebab-case names (village-visit.jpg) are published; raw downloads in assets/photos/ are skipped.
WEB_PHOTO=re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)+\.(?:jpg|jpeg|png|webp)$')
def skip_raw(folder,names): return [n for n in names if not WEB_PHOTO.match(n)] if Path(folder).name=='photos' else []
shutil.copytree(ROOT/'assets', OUT/'assets', ignore=skip_raw)
(OUT/'style.css').write_text((ROOT/'style.css').read_text())
(OUT/'.nojekyll').write_text('')

items=ET.parse(source).findall('./channel/item')
def val(i,n): return i.findtext(n,default='',namespaces=ns)
posts=[i for i in items if val(i,'wp:post_type')=='post' and val(i,'wp:status')=='publish']
pages={val(i,'wp:post_name'):i for i in items if val(i,'wp:post_type')=='page' and val(i,'wp:status')=='publish'}

def autop(s):
 # Mirror WordPress's paragraph handling: blank lines separate paragraphs, single newlines become <br>.
 out=[]
 for block in re.split(r'\n\s*\n',s.strip()):
  buf=[]
  for line in block.split('\n'):
   if re.match(r'\s*</?(?:h[1-6]|ul|ol|li|div|blockquote|figure|section|p)\b',line):
    if buf: out.append('<p>'+'<br>'.join(buf)+'</p>'); buf=[]
    out.append(line.strip())
   elif line.strip(): buf.append(line.strip())
  if buf: out.append('<p>'+'<br>'.join(buf)+'</p>')
 return '\n'.join(out)
# Jerry's letters used all caps for headings and emphasis; show them in normal case.
NORMAL_CASE=[
 ('WITH SO MUCH RELIGIOUS NOISE OUT THERE, I HESITATE TO ADD ANOTHER VOICE; HOWEVER,...','With so much religious noise out there, I hesitate to add another voice; however,...'),
 ('HAS HOPE BECOME A RARE COMMODITY?','<strong>Has hope become a rare commodity?</strong>'),
 ('HE IS THE GOD OF HOPE!','<strong>He is the God of hope!</strong>'),
 ('It is THE anchor','It is <em>the</em> anchor'),
 ('all JOY and PEACE','all <em>joy</em> and <em>peace</em>'),
 ('WHAT CAN WE DO?','<strong>What can we do?</strong>'),
 ('THE RESULT OF PLACING OUR FAITH IN THIS GOD????','<strong>The result of placing our faith in this God?</strong>'),
 ('THE ANSWER TO THE “HOW”.....THE AGENT OF CHANGE!','<strong>The answer to the “how”…the agent of change!</strong>'),
 ('IT BEGINS WITHIN...','<strong>It begins within...</strong>'),
 ('HOPE WILL RISE...','<strong>Hope will rise...</strong>'),
 ('TO GOD BE THE GLORY!','<strong>To God be the glory!</strong>'),
 ('lose HOPE!','lose <em>hope</em>!'),
 ('our HOPE without','our <em>hope</em> without'),
 ('PERSONALLY SPEAKING...','Personally speaking...'),
 ('AUGUST 16, 2012...','August 16, 2012...'),
 ('HELPING OVERSEAS PASTORS...','Helping overseas pastors...'),
 ('HOW ARE YOU DOING? LET ME KNOW...','How are you doing? Let me know...'),
 ('HANG ON...DON’T GIVE UP...YOU ARE OF GREAT VALUE TO GOD...HE LOVES YOU UNCONDITIONALLY...HIS MERCY IS NEW THIS MORNING...YOU CAN MAKE IT! HALLELUJAH!!!','<strong>Hang on...don’t give up...you are of great value to God...He loves you unconditionally...His mercy is new this morning...you can make it! Hallelujah!!!</strong>'),
]
NORMAL_CASE=[(re.compile(r'\s+'.join(map(re.escape,old.split(' ')))),new) for old,new in NORMAL_CASE]
# Drop WordPress classes, keeping the few this stylesheet uses.
KEEP_CLASSES={'alignright','wide-photo'}
def keep_classes(m):
 kept=[c for c in m.group(1).split() if c in KEEP_CLASSES]
 return f' class="{" ".join(kept)}"' if kept else ''
def clean(s):
 s=re.sub(r'https?://operationbarnabasinternational\.com/wp-content/uploads/2020/12/obi-painting(?:-\d+x\d+)?\.jpg','__ROOT__assets/faithful-shepherd.jpg',s)
 s=s.replace('faithful-shepherd.jpg" alt=""','faithful-shepherd.jpg" alt="The Faithful Shepherd painting"')
 s=re.sub(r'<script\b[^>]*>.*?</script>','',s,flags=re.S|re.I)
 s=re.sub(r'\s+on\w+\s*=\s*(["\']).*?\1','',s,flags=re.I|re.S)
 s=re.sub(r'\s+style="[^"]*"','',s)
 s=re.sub(r'\s+class="([^"]*)"',keep_classes,s)
 s=re.sub(r'<div>\s*</div>','',s).replace('&nbsp;',' ')
 for pattern,new in NORMAL_CASE: s=pattern.sub(new,s)
 # Hand-typed "- item" lines become a real list.
 s=re.sub(r'(?m)^[ \t]*-[ \t]*(\S.*)$',r'<li>\1</li>',s)
 s=re.sub(r'(?:<li>.*</li>\s*)+',lambda m:'<ul>'+re.sub(r'\s*\n\s*','',m.group(0).strip())+'</ul>\n\n',s)
 return autop(s)
def excerpt(s,words=30):
 text=' '.join(html.unescape(re.sub(r'<[^>]+>',' ',s)).split()).split(' ')
 cut=' '.join(text[:words])
 return html.escape(cut.rstrip('.,;:…')+'…' if len(text)>words else cut)

BRAND='<svg class="brand-mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40" aria-hidden="true" focusable="false"><circle cx="20" cy="20" r="18.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M16 32V15a5.5 5.5 0 0 1 11 0v2.5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'
NAV=[('About','about/'),('Conferences','conferences/'),('Updates','updates/'),('Photos',FACEBOOK),('Contact','contact/')]
def navlinks(current):
 links=[]
 for label,target in NAV:
  if target.startswith('http'): links.append(f'<a href="{target}" rel="noopener">{label}<span class="ext" aria-hidden="true">↗</span><span class="visually-hidden"> (Facebook)</span></a>')
  else:
   active=' aria-current="page"' if current.startswith(target) else ''
   links.append(f'<a href="__ROOT__{target}"{active}>{label}</a>')
 return ''.join(links)
def shell(path,title,body,description,head=''):
 current=path.as_posix().strip('.')+'/' if path.parts else ''
 full=SITE if title=='Home' else f'{title} | {SITE}'
 canonical=DOMAIN+'/'+(current if current!='/' else '')
 doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><script src="__ROOT__assets/theme.js"></script><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(full)}</title><meta name="description" content="{html.escape(description)}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:site_name" content="{SITE}"><meta property="og:title" content="{html.escape(full)}"><meta property="og:description" content="{html.escape(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{DOMAIN}/assets/obi-share.jpg"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="__ROOT__assets/favicon.svg" type="image/svg+xml"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400&amp;family=Source+Sans+3:wght@400;600;700&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="__ROOT__style.css?v=1">{head}</head><body class="{'home-page' if title=='Home' else 'interior-page'}"><a class="skip" href="#main">Skip to content</a><header class="site-header"><a class="brand" href="__ROOT__">{BRAND}<span class="brand-copy">Operation Barnabas<span class="brand-sub">International</span></span></a><nav class="main-nav" aria-label="Main navigation">{navlinks(current)}<a class="button small donate" href="__ROOT__donate/">Donate</a></nav><button class="menu-toggle" type="button" aria-label="Open menu" aria-controls="mobile-menu" aria-expanded="false"><svg width="26" height="26" viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h20M3 13h20M3 20h20"/></svg></button></header><dialog id="mobile-menu" class="mobile-menu" aria-label="Menu"><div class="mobile-menu-top"><span class="brand" aria-hidden="true">{BRAND}</span><button class="menu-close" type="button" aria-label="Close menu"><svg width="28" height="28" viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 6 16 16M22 6 6 22"/></svg></button></div><nav aria-label="Mobile navigation"><a href="__ROOT__">Home</a>{navlinks(current)}<a class="button donate" href="__ROOT__donate/">Donate</a></nav></dialog><script src="__ROOT__assets/mobile-menu.js" defer></script><script src="__ROOT__assets/subscribe.js" defer></script><main id="main">{body}</main><footer class="site-footer"><div class="footer-subscribe"><div><p class="footer-subscribe-label">Get Jerry’s devotionals &amp; news</p><p class="footer-subscribe-note">Encouragement and reports from the field.</p></div>{subscribe_form("footer")}</div><div class="footer-identity"><a class="brand" href="__ROOT__">{BRAND}<span class="brand-copy">Operation Barnabas<span class="brand-sub">International</span></span></a><p class="footer-tagline">Refreshing tired feet…<br>fitting them with sandals.</p><a class="footer-anm" href="https://advancingnativemissions.com/" rel="noopener"><span>A partner ministry of</span><img src="__ROOT__assets/anm-logo-reversed.svg" alt="Advancing Native Missions" width="150" height="40" loading="lazy"></a></div><nav class="footer-links" aria-label="The ministry"><h2>The ministry</h2><a href="__ROOT__about/">About OBI</a><a href="__ROOT__conferences/">Conferences</a><a href="__ROOT__updates/">Updates</a><a href="{FACEBOOK}" rel="noopener">Photos on Facebook</a></nav><div class="footer-links"><h2>Get in touch</h2><p>Operation Barnabas Intl.<br>PO Box 29<br>Afton, VA 22904 USA</p><a href="__ROOT__contact/">Contact us</a><a href="__ROOT__donate/">Donate</a></div><div class="footer-bottom"><p>© {datetime.now().year} {SITE}</p><button class="theme-toggle" type="button" aria-pressed="false" aria-label="Switch to dark mode" title="Switch to dark mode" hidden><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10Z"/></svg></button></div></footer></body></html>'''
 # Relative links keep the site working both on the github.io preview URL and the custom domain.
 return doc.replace('__ROOT__','../'*len(path.parts) or './')
def write(path,title,body,description='Encouraging and equipping indigenous pastors and their families around the world. A partner ministry of Advancing Native Missions.',head=''):
 p=OUT/path/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(shell(path,title,body,description,head))
def article(title,body,kicker=SITE):
 return f'<section class="pagehead"><p class="eyebrow">{kicker}</p><h1>{title}</h1></section><article class="prose">{body}</article>'

# Posts keep their original root-level WordPress permalinks.
TITLE_FIXES={'an-anniversary-of-sorts':'An Anniversary of Sorts'}
entries=[]
for i in posts:
 slug=val(i,'wp:post_name');title=TITLE_FIXES.get(slug,html.unescape(val(i,'title')).rstrip(':'))
 cat=next((c.text for c in i.findall('category') if c.get('domain')=='category'),'News')
 date=datetime.strptime(val(i,'wp:post_date')[:10],'%Y-%m-%d')
 entries.append(dict(id=val(i,'wp:post_id'),slug=slug,title=title,cat=cat,date=date,body=clean(val(i,'content:encoded'))))
# Posts written after the WordPress era: posts/<slug>.txt with title/date/category lines, "---", then the body.
for f in sorted((ROOT/'posts').glob('*.txt')):
 head,body=f.read_text().split('\n---\n',1)
 meta=dict(line.split(':',1) for line in head.strip().splitlines())
 meta={k.strip():v.strip() for k,v in meta.items()}
 entries.append(dict(id=None,slug=f.stem,title=meta['title'],cat=meta.get('category','News'),date=datetime.strptime(meta['date'],'%Y-%m-%d'),body=clean(body)))
entries.sort(key=lambda e:e['date'],reverse=True)
for e in entries:
 meta=f'<p class="postmeta"><span class="chip">{e["cat"]}</span> <time datetime="{e["date"]:%Y-%m-%d}">{e["date"]:%B %Y}</time></p>'
 write(Path(e['slug']),e['title'],article(html.escape(e['title']),meta+e['body']+'<p class="back"><a href="__ROOT__updates/">← All updates</a></p>',e['cat']),excerpt(e['body'],25))
def card(e):
 return f'<li class="card"><p class="postmeta"><span class="chip">{e["cat"]}</span> <time datetime="{e["date"]:%Y-%m-%d}">{e["date"]:%B %Y}</time></p><h3><a href="__ROOT__{e["slug"]}/">{html.escape(e["title"])}</a></h3><p>{excerpt(e["body"])}</p></li>'
write(Path('updates'),'Updates',article('News &amp; devotionals','<p class="intro">Letters, devotionals, and reports from the field.</p>'+subscribe_band('updates')+'<ul class="cards">'+''.join(card(e) for e in entries)+'</ul>','From the field'),'Letters, devotionals, and reports from Operation Barnabas International.')

shepherd=next(e for e in entries if e['slug']=='the-faithful-shepherd')
symbols=re.search(r'<ul>.*?</ul>',shepherd['body'],re.S).group(0)
SHEPHERD=f'<section class="shepherd" aria-labelledby="shepherd-title"><figure><img src="__ROOT__assets/faithful-shepherd.jpg" alt="Painting of a young shepherd holding a staff and a Bible, a dove above and sheep behind him" width="520" height="693" loading="lazy"><figcaption>Original painting by Robin Harding Smith, 2017</figcaption></figure><div><p class="eyebrow">The message of the painting</p><h2 id="shepherd-title">The Faithful Shepherd</h2>{symbols}<p>The Christian shepherds of the world are the reason for… and responsibility of… the ministry we call OBI.</p></div></section>'

# About: the original presentation text, minus the dated 2017 plans and the closing painting section shown above.
about=val(pages['about'],'content:encoded').split('2017 has already')[0]
about=re.sub(r'<img[^>]*>','',about)
write(Path('about'),'About',article('Coming alongside the faceless and forgotten.','<figure class="portrait"><img src="__ROOT__assets/jerry-harding.jpg" alt="Jerry Harding" width="213" height="320"><figcaption>Jerry Harding</figcaption></figure>'+clean(about)+'<figure class="wide-photo"><img src="__ROOT__assets/photos/conference-group.jpg" alt="A large conference group gathered in front of a green, flower-draped stage" width="1000" height="750" loading="lazy"><figcaption>Gathered together at an OBI conference</figcaption></figure>'+SHEPHERD,'About OBI'),'Since 1996, Operation Barnabas International has encouraged indigenous pastors and their wives through conferences, encounters, and advocacy.')

conferences=re.sub(r'<!--.*?-->','',(ROOT/'conferences.html').read_text(),flags=re.S)
# Mark a section <section class="year upcoming"> when it lists future dates; otherwise the page presents recent work.
UPCOMING='class="year upcoming"' in conferences
CONF_TITLE,CONF_KICKER,CONF_LINK=('Conferences','Schedule','See upcoming conferences') if UPCOMING else ('Recent Conferences','Where OBI has served','See recent conferences')
write(Path('conferences'),CONF_TITLE,article(CONF_TITLE,'<p class="intro">OBI teams gather pastors and their wives for days of sound Biblical preaching, spirited worship, warm fellowship—and good food, clean bedding, and soap and water.</p><figure class="wide-photo"><img src="__ROOT__assets/photos/pastors-praying.jpg" alt="Pastors and their wives kneel and bow in prayer in a simple meeting hall" width="1000" height="750"><figcaption>Pastors in prayer during an OBI conference</figcaption></figure><div class="schedule">'+conferences+'</div><p>Interested in joining a ministry team? <a href="__ROOT__contact/">Get in touch →</a></p>',CONF_KICKER),'Upcoming Operation Barnabas International conferences for pastors and their wives.')

form=f'''<form class="contact-form" action="{FORM_ENDPOINT}" method="POST" aria-describedby="form-status"><input type="hidden" name="_subject" value="Operation Barnabas website inquiry"><div class="form-honeypot" aria-hidden="true"><label for="contact-website">Leave this field empty</label><input id="contact-website" name="_gotcha" tabindex="-1" autocomplete="off"></div><div class="contact-fields"><div><label for="contact-name">Name <span>(required)</span></label><input id="contact-name" name="name" autocomplete="name" required maxlength="150"></div><div><label for="contact-email">Email <span>(required)</span></label><input id="contact-email" name="email" type="email" autocomplete="email" required maxlength="254"></div></div><label for="contact-subject">Subject</label><input id="contact-subject" name="subject" maxlength="200"><label for="contact-message">Message <span>(required)</span></label><textarea id="contact-message" name="message" rows="7" required maxlength="10000"></textarea><p id="form-status" class="form-note" role="status" aria-live="polite" tabindex="-1"></p><button class="button" type="submit">Send message</button></form><script src="__ROOT__assets/contact-form.js" defer></script>''' if FORM_ENDPOINT else ''
write(Path('contact'),'Contact',article('Get in touch.',f'''<p class="intro">We would love to hear from you—whether you have a question about the ministry, want to join a team, or would like to pray with us.</p><div class="contact-grid"><div class="contact-card"><h2>Mailing address</h2><p>Operation Barnabas Intl.<br>PO Box 29<br>Afton, VA 22904 USA</p></div><div class="contact-card"><h2>Phone</h2><p><a href="tel:+15408301625">(540) 830-1625</a> <span class="muted">Jerry Harding</span><br><a href="tel:+15404567111">(540) 456-7111</a> <span class="muted">ANM</span><br>Fax (540) 456-7222</p></div></div>{form}''','Contact'),'Contact Operation Barnabas International.')

write(Path('donate'),'Donate',article('Fit a pastor with sandals.',f'<p class="intro">Thank you for your interest in giving to OBI! Gifts help pastors and their families attend conferences and meet urgent needs in the field.</p><p>All donations to OBI are received through our partner, Advancing Native Missions (ANM).</p><figure class="wide-photo"><img src="__ROOT__assets/photos/obi-banner-group.jpg" alt="Conference participants and the OBI team gathered beneath an Operation Barnabas International banner" width="1200" height="900"><figcaption>Pastors, wives, and the OBI team at a conference</figcaption></figure><p><a class="button" href="{DONATE}" rel="noopener">Give through ANM ↗</a></p><blockquote class="pull">“Give, and it will be given to you. A good measure, pressed down, shaken together and running over.” <cite>Luke 6:38</cite></blockquote>','Support OBI'),'Support Operation Barnabas International through Advancing Native Missions.')

latest=''.join(card(e) for e in entries[:3])
# Old numeric WordPress links (?p=42, ?page_id=7) land on the homepage; send them on.
legacy={e['id']:f'./{e["slug"]}/' for e in entries if e['id']}
PAGE_ROUTES={'about':'about/','home':'','donate':'donate/','conferences':'conferences/','contact':'contact/','photos':FACEBOOK,'devotionals-test':'updates/','sample-page':''}
for slug,i in pages.items():
 if slug not in PAGE_ROUTES: raise ValueError(f'Unmapped published page: {slug}')
 legacy[val(i,'wp:post_id')]=PAGE_ROUTES[slug] if PAGE_ROUTES[slug].startswith('http') else './'+PAGE_ROUTES[slug]
legacy_js=f'<script>(()=>{{const m=location.search.match(/[?&](?:p|page_id)=(\\d+)/),r={json.dumps(legacy)};if(m&&m[1] in r)location.replace(r[m[1]])}})()</script>'
write(Path('.'),'Home',f'''<section class="hero"><div class="hero-copy"><p class="eyebrow">A partner ministry of Advancing Native Missions</p><h1><span>Refreshing tired feet.</span> <span class="sandals-line"><em>Fitting them<br>with sandals.</em><svg class="hero-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="104" height="104" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><g id="flipflop" transform="rotate(5 45 32)"><path d="M45 4C51 4 55 8.5 55 15.5 55 22 52 26.5 51 32 50.2 37 52.5 41 52.5 48 52.5 55 49 59 45 59 41 59 37.5 55.5 37.5 49 37.5 42 39.5 38 39 32 38.5 26 35 22 35 15.5 35 8.5 39 4 45 4Z"/><path d="M44 9.5v5"/><path d="M40.3 28C39.3 21.5 41 16.5 44 14.5 47.2 16.5 51 21.5 50.4 28"/></g><use href="#flipflop" transform="matrix(-1 0 0 1 64 0) translate(0 -2)"/></svg></span></h1><p class="intro">Operation Barnabas International comes alongside indigenous pastors and their wives around the world&#8288;—affirming their value, renewing their vision, and deepening their spiritual lives.</p><div class="actions"><a class="button" href="#subscribe">Get email updates</a><a class="button outline" href="__ROOT__about/">Our story</a></div></div><figure class="hero-art"><img src="__ROOT__assets/faithful-shepherd.jpg" alt="Painting of a young shepherd holding a staff and a Bible, a dove above and sheep behind him" width="520" height="693" fetchpriority="high"><figcaption>The Faithful Shepherd · Robin Harding Smith</figcaption></figure></section><section class="calling"><p class="eyebrow">Our calling</p><h2>The unknown, the unheralded, the faceless and forgotten.</h2><p>Discouragement is a scourge on Christian leaders—pastors, evangelists, and missionaries—because it renders them ineffective. Since 1996, OBI has met that need with encouragement and advocacy for the shepherds of God’s flock overseas.</p><figure class="calling-photo"><img src="__ROOT__assets/photos/refreshing-tired-feet-conference.jpg" alt="Pastors and their wives gathered for a group photo beneath an Operation Barnabas International “Refreshing Tired Feet” banner" width="1400" height="1050" loading="lazy"><figcaption>An OBI “Refreshing Tired Feet” conference</figcaption></figure></section><section class="pillars"><article><img class="pillar-photo" src="__ROOT__assets/photos/village-church.jpg" alt="An OBI team and local believers gather outside a tin-roofed village church" width="960" height="720" loading="lazy"><p class="eyebrow">Encouragement</p><h3>Refreshing tired feet</h3><p>Conferences and informal village encounters bring together sound Biblical preaching, spirited worship, and warm fellowship—with good food, clean bedding, and soap and water for those who struggle in ministry.</p><a href="__ROOT__conferences/">{CONF_LINK} →</a></article><article><img class="pillar-photo" src="__ROOT__assets/photos/village-visit.jpg" alt="A local ministry partner stands with a woman in a beaded collar and a man in a bright patterned shirt outside a village home" width="960" height="720" loading="lazy"><p class="eyebrow">Advocacy</p><h3>Fitting them with sandals</h3><p>Ministry team members often “catch the vision” and return home to advocate for their fellow laborers overseas, supplying resources so shepherds can fulfill their divine calling.</p><a href="__ROOT__donate/">Give through ANM →</a></article></section>{subscribe_band('home')}<section class="gallery" aria-labelledby="gallery-title"><div class="section-head"><div><p class="eyebrow">Conferences &amp; encounters</p><h2 id="gallery-title">Days of refreshing</h2></div><a href="{FACEBOOK}" rel="noopener">More photos on Facebook ↗</a></div><div class="photo-grid"><figure class="tall"><img src="__ROOT__assets/photos/worship-hands-raised.jpg" alt="Women at a conference lift their hands in worship, eyes closed" width="800" height="1000" loading="lazy"></figure><figure><img src="__ROOT__assets/photos/pastors-praying.jpg" alt="Pastors and their wives kneel and bow in prayer in a simple meeting hall" width="1000" height="750" loading="lazy"></figure><figure class="tall"><img src="__ROOT__assets/photos/pastor-smiling.jpg" alt="An elderly pastor in a patterned cap smiles while seated on the floor with other men" width="800" height="1000" loading="lazy"></figure><figure><img src="__ROOT__assets/photos/congregation-worship.jpg" alt="A congregation stands in worship, some with hands raised" width="960" height="720" loading="lazy"></figure></div></section><section class="triage"><blockquote>“OBI is triage! …the place where God brings His church together to send His love and assurance, His strength and anointing, to those who are the weakest, the most frail, and to those who are most likely to ‘not make it.’”</blockquote><p class="cite">Dan, writing from a conference in Liberia</p></section><section class="voices" aria-labelledby="voices-title"><p class="eyebrow">From the field</p><h2 id="voices-title">What pastors are saying</h2><ul><li><blockquote>“God spoke to us during the conference. We received in three days what we had not received after many years of fasting and praying.”</blockquote><p>A pastor and his wife · Togo</p></li><li><blockquote>“I have spent seven years giving out. At the OBI conference, I was able to take in… OBI spoke to my heart.”</blockquote><p>A pastor · Indonesia</p></li><li><blockquote>“This conference stirred up the calling and vision of the leaders in this part of Nepal. Thank you for igniting the servants of the Lord.”</blockquote><p>A ministry leader · Nepal</p></li></ul></section><section class="latest" aria-labelledby="latest-title"><div class="section-head"><div><p class="eyebrow">News &amp; devotionals</p><h2 id="latest-title">Latest updates</h2></div><a href="__ROOT__updates/">All updates →</a></div><ul class="cards">{latest}</ul></section><section class="scripture"><blockquote>“…encouraging one another; and all the more as you see the day drawing near.”</blockquote><p>Hebrews 10:25</p></section>''',head=legacy_js)

# GitHub Pages serves this for any missing path; root-absolute links assume the custom domain.
(OUT/'404.html').write_text(shell(Path('.'),'Page not found',article('Page not found.','<p class="intro">Sorry, we couldn’t find that page.</p><p><a class="button" href="__ROOT__">Go to the homepage</a></p>','404'),'Page not found.').replace('href="./','href="/').replace('src="./','src="/'))

# Old WordPress paths that moved get small redirect pages (GitHub Pages has no server redirects).
MOVED={'about/contact':'contact/','about/donate':'donate/','home':'','photos':FACEBOOK,'category/devotionals':'updates/','category/news':'updates/','devotionals-test':'updates/','sample-page':''}
for old,target in MOVED.items():
 depth=len(Path(old).parts); href=target if target.startswith('http') else '../'*depth+target
 p=OUT/old/'index.html';p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Redirecting…</title><meta name="robots" content="noindex"><link rel="canonical" href="{target if target.startswith("http") else DOMAIN+"/"+target}"><meta http-equiv="refresh" content="0; url={href}"></head><body><p>This page has moved: <a href="{href}">continue</a>.</p></body></html>')
unmatched=[pat.pattern for pat,_ in NORMAL_CASE if not any(pat.search(val(i,'content:encoded')) for i in posts)]
if unmatched: raise ValueError(f'All-caps phrases not found in the export: {unmatched}')
print(f'Built {len(entries)} posts, {len(MOVED)} legacy redirects, and supporting pages in {OUT}')
