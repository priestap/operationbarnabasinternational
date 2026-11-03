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
DONATE='https://give.anm.onl/s/campaign/view?campaignId=Log0bGuWL2IJpi6'
# Jerry's existing Mailchimp list (the same one the WordPress site used).
MAILCHIMP='https://facebook.us14.list-manage.com/subscribe/post?u=92c342cbb799c4a03fe7f8831&amp;id=76f34ed275'
MAILCHIMP_HONEYPOT='b_92c342cbb799c4a03fe7f8831_76f34ed275'
def subscribe_form(key):
 return f'''<form class="subscribe-form" action="{MAILCHIMP}" method="post" target="_blank"><label class="visually-hidden" for="subscribe-{key}">Email address</label><div class="subscribe-row"><input id="subscribe-{key}" type="email" name="EMAIL" autocomplete="email" placeholder="Your email address" required><button class="button" type="submit">Subscribe</button></div><div class="form-honeypot" aria-hidden="true"><input type="text" name="{MAILCHIMP_HONEYPOT}" tabindex="-1" value="" autocomplete="off"></div><p class="subscribe-status" role="status" aria-live="polite"></p></form>'''
SUBSCRIBE_NOTE='<p>Devotionals, reports from the field, and prayer requests as conferences draw near—so you’ll know what to pray for, and when. Unsubscribe anytime.</p>'
def subscribe_band(key,note=SUBSCRIBE_NOTE):
 return f'<section class="subscribe" id="subscribe" aria-labelledby="subscribe-title-{key}"><div><p class="eyebrow subscribe-eyebrow"><span class="subscribe-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/></svg></span>Stay connected</p><h2 id="subscribe-title-{key}">Sign up for Jerry’s devotionals &amp; news</h2>{note}</div>{subscribe_form(key)}</section>'
# Paste a Formspree endpoint (https://formspree.io/f/…) here to turn on the contact form.
FORM_ENDPOINT='https://formspree.io/f/xzeekoyq'

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

# The crook is cut out of the doorway (the background shows through) and runs off its bottom edge.
# Each copy of the mark gets its own mask/clip ids.
BRAND='<svg class="brand-mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 64" width="36" height="44" aria-hidden="true" focusable="false"><mask id="__CROOK__-m"><rect width="52" height="64" fill="#fff"/><path transform="translate(26 17) scale(1.15) translate(-31.75 -7)" d="M28 55V26.5C28 22.5 26 20 26 15.5 26 10.5 28.5 7 32 7 35.5 7 37.5 10 37.2 14 36.9 17.5 35.5 19.5 36.7 22.5" fill="none" stroke="#000" stroke-width="3.9" stroke-linecap="round" stroke-linejoin="round"/></mask><path d="M0 53V26A26 26 0 0 1 52 26V53A11 11 0 0 1 41 64H11A11 11 0 0 1 0 53Z" fill="currentColor" mask="url(#__CROOK__-m)"/></svg>'
NAV=[('About','about/'),('Conferences','conferences/'),('Updates','updates/'),('Photos',FACEBOOK),('Contact','contact/')]
def navlinks(current):
 links=[]
 for label,target in NAV:
  if target.startswith('http'): links.append(f'<a href="{target}" rel="noopener">{label}<span class="ext" aria-hidden="true">↗\ufe0e</span><span class="visually-hidden"> (Facebook)</span></a>')
  else:
   active=' aria-current="page"' if current.startswith(target) else ''
   links.append(f'<a href="__ROOT__{target}"{active}>{label}</a>')
 return ''.join(links)
def shell(path,title,body,description,head=''):
 current=path.as_posix().strip('.')+'/' if path.parts else ''
 full=SITE if title=='Home' else f'{title} | {SITE}'
 canonical=DOMAIN+'/'+(current if current!='/' else '')
 doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><script src="__ROOT__assets/theme.js"></script><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(full)}</title><meta name="description" content="{html.escape(description)}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:site_name" content="{SITE}"><meta property="og:title" content="{html.escape(full)}"><meta property="og:description" content="{html.escape(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{DOMAIN}/assets/obi-share.jpg"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="__ROOT__assets/favicon.svg" type="image/svg+xml"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400&amp;family=Source+Sans+3:wght@400;600;700&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="__ROOT__style.css?v=16">{head}</head><body class="{'home-page' if title=='Home' else 'interior-page'}"><a class="skip" href="#main">Skip to content</a><header class="site-header"><a class="brand" href="__ROOT__">{BRAND}<span class="brand-copy">Operation Barnabas<span class="brand-sub">International</span></span></a><nav class="main-nav" aria-label="Main navigation">{navlinks(current)}<a class="button small donate" href="__ROOT__donate/">Donate</a></nav><button class="menu-toggle" type="button" aria-label="Open menu" aria-controls="mobile-menu" aria-expanded="false"><svg width="26" height="26" viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h20M3 13h20M3 20h20"/></svg></button></header><dialog id="mobile-menu" class="mobile-menu" aria-label="Menu"><div class="mobile-menu-top"><span class="brand" aria-hidden="true">{BRAND}</span><button class="menu-close" type="button" aria-label="Close menu"><svg width="28" height="28" viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 6 16 16M22 6 6 22"/></svg></button></div><nav aria-label="Mobile navigation"><a href="__ROOT__">Home</a>{navlinks(current)}<a class="button donate" href="__ROOT__donate/">Donate</a></nav></dialog><script src="__ROOT__assets/mobile-menu.js" defer></script><script src="__ROOT__assets/subscribe.js" defer></script><main id="main">{body}</main><footer class="site-footer"><div class="footer-subscribe"><div><p class="footer-subscribe-label">Sign up for Jerry’s devotionals &amp; news</p><p class="footer-subscribe-note">Encouragement and reports from the field.</p></div>{subscribe_form("footer")}</div><div class="footer-identity"><a class="brand" href="__ROOT__">{BRAND}<span class="brand-copy">Operation Barnabas<span class="brand-sub">International</span></span></a><p class="footer-tagline">Refreshing tired feet…<br>fitting them with sandals.</p><a class="footer-anm" href="https://advancingnativemissions.com/" rel="noopener"><span>A partner ministry of</span><img src="__ROOT__assets/anm-logo-reversed.svg" alt="Advancing Native Missions" width="150" height="40" loading="lazy"></a></div><nav class="footer-links" aria-label="The ministry"><h2>The ministry</h2><a href="__ROOT__about/">About OBI</a><a href="__ROOT__conferences/">Conferences</a><a href="__ROOT__updates/">Updates</a><a href="{FACEBOOK}" rel="noopener">Photos on Facebook</a></nav><div class="footer-links"><h2>Get in touch</h2><p>Operation Barnabas Intl.<br>PO Box 29<br>Afton, VA 22904 USA</p><a href="__ROOT__contact/">Contact us</a><a href="__ROOT__donate/">Donate</a></div><div class="footer-bottom"><p>© {datetime.now().year} {SITE}<span class="footer-sep" aria-hidden="true"> · </span><a class="footer-credit" href="https://markpriestap.com/" rel="noopener">Site by Mark Priestap</a></p><div class="footer-actions"><a class="footer-social" href="{FACEBOOK}" rel="noopener" aria-label="Operation Barnabas International on Facebook" title="Facebook"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.4 1.5-1.4h1.5V4.5c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.3H8.1v3h2.5V21z"/></svg></a><button class="theme-toggle" type="button" aria-pressed="false" aria-label="Switch to dark mode" title="Switch to dark mode" hidden><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10Z"/></svg></button></div></div></footer></body></html>'''
 # Relative links keep the site working both on the github.io preview URL and the custom domain.
 n=iter(range(1,100))
 doc=re.sub(r'<svg class="brand-mark".*?</svg>',lambda m:m.group(0).replace('__CROOK__',f'crook-{next(n)}'),doc,flags=re.S)
 return doc.replace('__ROOT__','../'*len(path.parts) or './')
def write(path,title,body,description='Encouraging and equipping indigenous pastors and their families around the world. A partner ministry of Advancing Native Missions.',head=''):
 p=OUT/path/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(shell(path,title,body,description,head))
def article(title,body,kicker=SITE):
 return f'<section class="pagehead"><p class="eyebrow">{kicker}</p><h1>{title}</h1></section><article class="prose">{body}</article>'
# Same as article(), plus a desktop sidebar linking to each section's h2, grouped into upcoming and past.
def toc_article(title,body,kicker=SITE):
 groups={'Upcoming Conferences':[],'Past Conferences':[]}
 def anchor(m):
  cls,gap,heading=m.groups();text=re.sub(r'<.*?>','',heading);slug=re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')
  groups['Upcoming Conferences' if 'upcoming' in cls else 'Past Conferences'].append(f'<li><a href="#{slug}">{text}</a></li>')
  return f'<section class="{cls}">{gap}<h2 id="{slug}">{heading}</h2>'
 body=re.sub(r'<section class="([^"]*)">(\s*)<h2>(.*?)</h2>',anchor,body)
 nav=''.join(f'<p class="toc-title">{label}</p><ul>{"".join(links)}</ul>' for label,links in groups.items() if links)
 return f'<div class="toc-layout"><section class="pagehead"><p class="eyebrow">{kicker}</p><h1>{title}</h1></section><nav class="toc" aria-label="On this page"><span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg></span>{nav}</nav><article class="prose">{body}</article></div>'

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
write(Path('updates'),'Updates',article('News &amp; devotionals','<p class="intro">Letters, devotionals, and reports from the field.</p>'+subscribe_band('updates','<p>Join the partners who carry OBI’s work in prayer. Jerry’s emails bring you:</p><ul class="subscribe-list"><li><strong>Prayer requests</strong> as each conference draws near: the pastors and wives who will gather, the teaching, and the team’s health and protection.</li><li><strong>Reports from the field</strong> afterward, so you can see how God answered and give thanks.</li><li><strong>Devotionals</strong> from God’s Word to encourage you in your own walk.</li></ul><p>Unsubscribe anytime.</p>')+'<ul class="cards">'+''.join(card(e) for e in entries)+'</ul>','From the field'),'Letters, devotionals, and reports from Operation Barnabas International.')

shepherd=next(e for e in entries if e['slug']=='the-faithful-shepherd')
symbols=re.search(r'<ul>.*?</ul>',shepherd['body'],re.S).group(0)
SHEPHERD=f'<section class="shepherd" aria-labelledby="shepherd-title"><div><p class="eyebrow">The message of the painting</p><h2 id="shepherd-title">The Faithful Shepherd</h2>{symbols}<p>The Christian shepherds of the world are the reason for… and responsibility of… the ministry we call OBI.</p></div></section>'

# About: the original presentation text, minus the dated 2017 plans and the closing painting section shown above.
about=val(pages['about'],'content:encoded').split('2017 has already')[0]
about=re.sub(r'<img[^>]*>','',about)
about=clean(about)
# Section headings and bold key phrases make Jerry's letter easier to scan; his wording is unchanged.
for start,heading in [('We have only seen glimpses','The scourge of discouragement'),('OBI became one of','How OBI began'),('Many times members','Encouragement and advocacy'),('Stories and testimonies','Lives changed'),('You see,','More than an event'),('Perhaps my friend Dan','From the field')]:
 assert about.count('<p>'+start)==1,start
 about=about.replace('<p>'+start,f'<h2>{heading}</h2>\n<p>'+start)
for phrase in ['discouragement will render them ineffective','in the fall of 1996','affirming their value, renewing their vision, and deepening their spiritual lives','"Refreshing tired feet ...fitting them with sandals"','200 overseas conferences and encounters','re-commitments were made for the long haul','OBI is not a "pep rally" nor a temporary "emotional fix"','OBI is triage!']:
 assert about.count(phrase)==1,phrase
 about=about.replace(phrase,f'<strong>{phrase}</strong>')
# The testimonies run to the end of the text. Only the quoted words go in a card: a "From X:" lead-in becomes its label,
# Jerry's own narration stays as plain text around it, and the (quote)/(end of quote) markers are dropped.
intro,field=about.split('<h2>From the field</h2>\n')
notes=[]
for para in re.findall(r'<p>(.*?)</p>',field,flags=re.S):
 m=re.match(r'(.*?)\s*(?:\((?:and I )?quote\))?\s*"(.*)"\s*(?:\(end of quote\))?\s*(.*)$',para,flags=re.S)
 assert m,para[:40]
 pre,quote,post=(g.strip() for g in m.groups())
 label=''
 if re.fullmatch(r'From [^:]+:',pre): label=f'<cite>{pre[:-1]}</cite>'
 elif pre: notes.append(f'<p>{re.sub(r",$",":",pre)}</p>')
 notes.append(f'<blockquote>{label}<p>{quote}</p></blockquote>')
 if post: notes.append(f'<p>{post}</p>')
about=intro+'<h2>From the field</h2>\n<div class="field-notes">'+'\n'.join(notes)+'</div>'
write(Path('about'),'About',article('Coming alongside the faceless and forgotten.','<div class="about-visual"><figure class="hero-art"><img src="__ROOT__assets/faithful-shepherd.jpg" alt="Painting of a young shepherd holding a staff and a Bible, a dove above and sheep behind him" width="520" height="693"><figcaption>The Faithful Shepherd<br>by Robin Harding Smith<br><a href="#shepherd-title">What the painting means ↓</a></figcaption></figure></div>'+about.replace('<h2>How OBI began</h2>\n','<h2>How OBI began</h2>\n<figure class="portrait"><img src="__ROOT__assets/jerry-harding.jpg" alt="Jerry Harding" width="213" height="320" loading="lazy"><figcaption>Jerry Harding</figcaption></figure>',1)+'<figure class="wide-photo"><img src="__ROOT__assets/photos/conference-group.jpg" alt="A large conference group gathered in front of a green, flower-draped stage" width="1000" height="750" loading="lazy"><figcaption>Gathered together at an OBI conference</figcaption></figure>'+SHEPHERD,'About OBI'),'Since 1996, Operation Barnabas International has encouraged indigenous pastors and their wives through conferences, encounters, and advocacy.')

conferences=re.sub(r'<!--.*?-->','',(ROOT/'conferences.html').read_text(),flags=re.S)
# Mark a section <section class="year upcoming"> when it lists future dates; otherwise the page presents recent work.
UPCOMING='class="year upcoming"' in conferences
CONF_TITLE,CONF_KICKER,CONF_LINK=('Conferences','Schedule','See upcoming conferences') if UPCOMING else ('Past Conferences','Where OBI has served','See past conferences')
write(Path('conferences'),CONF_TITLE,toc_article(CONF_TITLE,'<p class="intro">OBI teams gather pastors and their wives for days of sound Biblical preaching, spirited worship, warm fellowship—and good food, clean bedding, and soap and water.</p><figure class="wide-photo"><img src="__ROOT__assets/photos/pastors-praying.jpg" alt="Pastors and their wives kneel and bow in prayer in a simple meeting hall" width="1000" height="750"><figcaption>Pastors in prayer during an OBI conference</figcaption></figure><div class="schedule">'+conferences+'</div><p>Interested in joining a ministry team? <a href="__ROOT__contact/">Get in touch →</a></p>',CONF_KICKER),'Upcoming Operation Barnabas International conferences for pastors and their wives.')

form=f'''<h2 id="contact-form-heading">Send an Email</h2><form class="contact-form" action="{FORM_ENDPOINT}" method="POST" aria-labelledby="contact-form-heading" aria-describedby="form-status"><input type="hidden" name="_subject" value="Operation Barnabas website inquiry"><div class="form-honeypot" aria-hidden="true"><label for="contact-website">Leave this field empty</label><input id="contact-website" name="_gotcha" tabindex="-1" autocomplete="off"></div><div class="contact-fields"><div><label for="contact-name">Name <span>(required)</span></label><input id="contact-name" name="name" autocomplete="name" required maxlength="150"></div><div><label for="contact-email">Email <span>(required)</span></label><input id="contact-email" name="email" type="email" autocomplete="email" required maxlength="254"></div></div><label for="contact-subject">Subject</label><input id="contact-subject" name="subject" maxlength="200"><label for="contact-message">Message <span>(required)</span></label><textarea id="contact-message" name="message" rows="7" required maxlength="10000"></textarea><p id="form-status" class="form-note" role="status" aria-live="polite" tabindex="-1"></p><button class="button" type="submit">Send message</button></form><script src="__ROOT__assets/contact-form.js" defer></script>''' if FORM_ENDPOINT else ''
write(Path('contact'),'Contact','<div class="wide-page">'+article('Get in touch.',f'''<div class="contact-layout{' has-form' if form else ''}"><div class="contact-main"><p class="intro">Jerry reads every message himself. Write if you have a question about OBI’s work, would like to share a word of encouragement for the pastors and their wives, or want to let him know you are praying. He would be glad to hear from you.</p>{form}</div><div class="contact-grid"><div class="contact-card"><span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 17a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9.5C2 7 4 5 6.5 5H18c2.2 0 4 1.8 4 4v8Z"/><path d="M15 9h3v2"/><path d="M6.5 5C9 5 11 7 11 9.5V17a2 2 0 0 1-2 2"/><path d="M6 10h1"/></svg></span><h2>Mailing address</h2><address>Operation Barnabas Intl.<br>PO Box 29<br>Afton, VA 22904 USA</address></div><div class="contact-card"><span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3.5h3.2l1.6 4.3-2.1 1.4a11.5 11.5 0 0 0 7.1 7.1l1.4-2.1 4.3 1.6V19a1.5 1.5 0 0 1-1.6 1.5A16.5 16.5 0 0 1 3.5 5.1 1.5 1.5 0 0 1 5 3.5Z"/></svg></span><h2>Phone</h2><dl class="phone-list"><div><dt>Jerry Harding</dt><dd><a href="tel:+15408301625">(540) 830-1625</a></dd></div><div><dt>ANM</dt><dd><a href="tel:+15404567111">(540) 456-7111</a></dd></div><div><dt>Fax</dt><dd>(540) 456-7222</dd></div></dl></div></div></div>''','Contact')+'</div>','Contact Operation Barnabas International.')

write(Path('donate'),'Donate',article('Fit a pastor with sandals.',f'<div class="give-split"><p class="intro">Thank you for your interest in giving to OBI! Gifts help pastors and their families attend conferences and meet urgent needs in the field.</p><figure class="give-photo"><img src="__ROOT__assets/photos/obi-banner-group-tight.jpg" alt="Conference participants and the OBI team gathered beneath an Operation Barnabas International banner" width="800" height="610"><figcaption>Pastors, wives, and the OBI team at a conference</figcaption></figure><div class="give-how"><p>All donations to OBI are received through our partner, Advancing Native Missions (ANM). On ANM’s giving page, under “I’d like to support,” search for and choose <strong>095OBI1100 – Operation Barnabas International</strong>.</p><p><a class="button" href="{DONATE}" rel="noopener">Give through ANM ↗\ufe0e</a></p></div></div><blockquote class="pull">“Give, and it will be given to you. A good measure, pressed down, shaken together and running over.” <cite>Luke 6:38</cite></blockquote>','Support OBI'),'Support Operation Barnabas International through Advancing Native Missions.')

latest=''.join(card(e) for e in entries[:3])
# Old numeric WordPress links (?p=42, ?page_id=7) land on the homepage; send them on.
legacy={e['id']:f'./{e["slug"]}/' for e in entries if e['id']}
PAGE_ROUTES={'about':'about/','home':'','donate':'donate/','conferences':'conferences/','contact':'contact/','photos':FACEBOOK,'devotionals-test':'updates/','sample-page':''}
for slug,i in pages.items():
 if slug not in PAGE_ROUTES: raise ValueError(f'Unmapped published page: {slug}')
 legacy[val(i,'wp:post_id')]=PAGE_ROUTES[slug] if PAGE_ROUTES[slug].startswith('http') else './'+PAGE_ROUTES[slug]
legacy_js=f'<script>(()=>{{const m=location.search.match(/[?&](?:p|page_id)=(\\d+)/),r={json.dumps(legacy)};if(m&&m[1] in r)location.replace(r[m[1]])}})()</script>'
write(Path('.'),'Home',f'''<section class="hero"><div class="hero-copy"><p class="eyebrow">A partner ministry of Advancing Native Missions</p><h1><span>Refreshing tired feet.</span> <em>Fitting them with sandals.</em></h1><p class="intro">Operation Barnabas International comes alongside indigenous pastors and their wives around the world&#8288;—affirming their value, renewing their vision, and deepening their spiritual lives.</p><div class="actions"><a class="button" href="#subscribe">Get email updates</a><a class="button outline" href="__ROOT__about/">Our story</a></div><p class="hero-verse">“How beautiful are the feet of those who bring good news!” <cite>Romans 10:15</cite></p></div><div class="hero-visual"><figure class="hero-art"><img src="__ROOT__assets/photos/foot-washing-pitcher.jpg" alt="Hands pour water from a clay pitcher over a foot into a metal basin" width="500" height="695" fetchpriority="high"></figure></div></section><section class="calling"><p class="eyebrow">Our calling</p><h2>The unknown, the unheralded, the faceless and forgotten.</h2><p>Discouragement is a scourge on Christian leaders—pastors, evangelists, and missionaries—because it renders them ineffective. Since 1996, OBI has met that need with encouragement and advocacy for the shepherds of God’s flock overseas.</p><p class="calling-more"><a href="__ROOT__about/">Read our story →</a></p><figure class="calling-photo"><img src="__ROOT__assets/photos/refreshing-tired-feet-conference.jpg" alt="Pastors and their wives gathered for a group photo beneath an Operation Barnabas International “Refreshing Tired Feet” banner" width="1400" height="1050" loading="lazy"><figcaption>An OBI “Refreshing Tired Feet” conference</figcaption></figure></section><section class="pillars"><article><img class="pillar-photo" src="__ROOT__assets/photos/village-church.jpg" alt="An OBI team and local believers gather outside a tin-roofed village church" width="960" height="720" loading="lazy"><p class="eyebrow">Encouragement</p><h3>Refreshing tired feet</h3><p>Conferences and informal village encounters bring together sound Biblical preaching, spirited worship, and warm fellowship—with good food, clean bedding, and soap and water for those who struggle in ministry.</p><a href="__ROOT__conferences/">{CONF_LINK} →</a></article><article><img class="pillar-photo" src="__ROOT__assets/photos/village-visit.jpg" alt="A local ministry partner stands with a woman in a beaded collar and a man in a bright patterned shirt outside a village home" width="960" height="720" loading="lazy"><p class="eyebrow">Advocacy</p><h3>Fitting them with sandals</h3><p>Ministry team members often “catch the vision” and return home to advocate for their fellow laborers overseas, supplying resources so shepherds can fulfill their divine calling.</p><p class="pillar-links"><a href="#subscribe">Pray with us →</a><a href="__ROOT__donate/">Give through ANM →</a></p></article></section>{subscribe_band('home')}<section class="gallery" aria-labelledby="gallery-title"><div class="section-head"><div><p class="eyebrow">Conferences &amp; encounters</p><h2 id="gallery-title">Days of refreshing</h2></div><a href="{FACEBOOK}" rel="noopener">More photos on Facebook ↗\ufe0e</a></div><div class="photo-grid"><figure class="tall"><img src="__ROOT__assets/photos/worship-hands-raised.jpg" alt="Women at a conference lift their hands in worship, eyes closed" width="800" height="1000" loading="lazy"></figure><figure><img src="__ROOT__assets/photos/pastors-praying.jpg" alt="Pastors and their wives kneel and bow in prayer in a simple meeting hall" width="1000" height="750" loading="lazy"></figure><figure class="tall"><img src="__ROOT__assets/photos/pastor-smiling.jpg" alt="An elderly pastor in a patterned cap smiles while seated on the floor with other men" width="800" height="1000" loading="lazy"></figure><figure><img src="__ROOT__assets/photos/congregation-worship.jpg" alt="A congregation stands in worship, some with hands raised" width="960" height="720" loading="lazy"></figure></div></section><section class="triage"><blockquote>“OBI is triage! …the place where God brings His church together to send His love and assurance, His strength and anointing, to those who are the weakest, the most frail, and to those who are most likely to ‘not make it.’”</blockquote><p class="cite">Dan, writing from a conference in Liberia</p><p class="triage-link"><a href="__ROOT__conferences/">{CONF_LINK} <span aria-hidden="true">→</span></a></p></section><section class="voices" aria-labelledby="voices-title"><p class="eyebrow">From the field</p><h2 id="voices-title">In their own words</h2><ul><li><blockquote>“God spoke to us during the conference. We received in three days what we had not received after many years of fasting and praying.”</blockquote><p>A pastor and his wife · Togo</p></li><li><blockquote>“I have spent seven years giving out. At the OBI conference, I was able to take in… OBI spoke to my heart.”</blockquote><p>A pastor · Indonesia</p></li><li><blockquote>“This conference stirred up the calling and vision of the leaders in this part of Nepal. Thank you for igniting the servants of the Lord.”</blockquote><p>A ministry leader · Nepal</p></li></ul></section><section class="latest" aria-labelledby="latest-title"><div class="section-head"><div><p class="eyebrow">News &amp; devotionals</p><h2 id="latest-title">Latest updates</h2></div><a href="__ROOT__updates/">All updates →</a></div><ul class="cards">{latest}</ul></section><section class="scripture"><blockquote>“…encouraging one another; and all the more as you see the day drawing near.”</blockquote><p>Hebrews 10:25</p></section>''',head=legacy_js)

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
