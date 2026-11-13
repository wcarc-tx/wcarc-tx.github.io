import glob, os, re
from bs4 import BeautifulSoup
HCOL='https://secure.hamclubonline.com/payment.php'
GIO='https://wcarc.groups.io/g/main'
DROP_LABELS={'Members','Presentations','Newsletters','Membership Plans'}
for f in glob.glob('site/*.html')+glob.glob('site/m/*.html'):
    mobile='/m/' in f; name=os.path.basename(f)
    soup=BeautifulSoup(open(f).read(),'lxml')
    # menu items to drop
    for li in soup.find_all('li'):
        a=li.find('a'); lab=a.get_text(strip=True) if a else ''
        if lab in DROP_LABELS and len(li.get_text(strip=True))<20: li.decompose()
    for a in soup.find_all('a',href=True):
        h=a['href']
        if 'membership.html' in h or 'pricing-plans' in h or 'plans-pricing' in h: a['href']=HCOL; a['target']='_blank'
        elif re.search(r'wcarc\.com/(members|profile|account)',h) or h.endswith('/members'):
            if a.get_text(strip=True) in ('','0'): a.decompose()
            else: a['href']=GIO
        elif re.search(r'(newsletters|presentations)\.html',h) or 'general-clean' in h: a['href']='index.html'
    # cart icon wrappers
    for a in soup.find_all('a',href=True):
        if 'cart-page' in a['href']:
            a['style']=(a.get('style') or '')+';visibility:hidden'; a['href']='#'
    qa=soup.find(id='QUICK_ACTION_BAR')
    if qa: qa['onclick']="location.href='mailto:board@wcarc.groups.io?subject=WCARC%20Website%20Question'"; qa['style']=(qa.get('style') or '')+';cursor:pointer'
    # login button -> groups.io link
    for btn in soup.find_all('button'):
        if 'Log In' in btn.get_text() or btn.find(attrs={'data-hook':re.compile('login',re.I)}):
            a=soup.new_tag('a',href=GIO,target='_blank'); a['class']=btn.get('class',[]); a['style']=(btn.get('style') or '')+';text-decoration:none;display:flex;align-items:center;justify-content:center'
            for c in list(btn.contents): a.append(c.extract())
            btn.replace_with(a)
    # wix chat / ads leftovers
    for el in soup.select('[id^="comp-"][data-testid="chat"], #WIX_ADS, [data-hook="chat-button"]'): el.decompose()
    # strip remaining Wix-only attributes that do nothing
    # mobile switch
    head=soup.head
    if not mobile:
        sc=soup.new_tag('script'); sc.string="if(/Mobi|Android|iPhone|iPod/i.test(navigator.userAgent)&&!/[?&]desktop/.test(location.search))location.replace('m/'+(location.pathname.split('/').pop()||'index.html'));"
        head.insert(0,sc)
    else:
        sc=soup.new_tag('script'); sc.string="if(!/Mobi|Android|iPhone|iPod/i.test(navigator.userAgent)&&!/[?&]mobile/.test(location.search))location.replace('../'+(location.pathname.split('/').pop()||'index.html'));"
        head.insert(0,sc)
    t=soup.find('title')
    open(f,'w').write(str(soup))
print('done')

# ---- contact forms -> Formspree (endpoint set in assets/site-config.js) ----
open('site/assets/site-config.js','w').write("// Paste the club's Formspree endpoint here (Formspree dashboard -> form -> Integration).\nwindow.WCARC_FORM_ENDPOINT = 'https://formspree.io/f/REPLACE_ME';\n")
FIX="""<script src="{p}assets/site-config.js"></script><script>document.addEventListener('DOMContentLoaded',function(){{document.querySelectorAll('form').forEach(function(f){{f.action=window.WCARC_FORM_ENDPOINT;f.method='POST';}});}});</script>"""
for f in glob.glob('site/*.html')+glob.glob('site/m/*.html'):
    soup=BeautifulSoup(open(f).read(),'lxml')
    forms=soup.find_all('form')
    if not forms: continue
    for fm in forms:
        for i in fm.find_all('input'):
            n=(i.get('name') or '').replace('-','_')
            if n: i['name']=n
            if i.get('type')=='email': i['name']='email'
        for t in fm.find_all('textarea'): t['name']='message'
        for b in fm.find_all('button'):
            if 'Send' in b.get_text() or 'Submit' in b.get_text(): b['type']='submit'
        hp=soup.new_tag('input',type='hidden',attrs={'name':'_subject','value':'WCARC website contact'}); fm.append(hp)
    p='../' if '/m/' in f else ''
    soup.body.append(BeautifulSoup(FIX.format(p=p),'lxml').find_all('script')[0])
    soup.body.append(BeautifulSoup(FIX.format(p=p),'lxml').find_all('script')[1])
    open(f,'w').write(str(soup))
print('forms wired')

# ---- desktop dropdown menus on hover (Wix used JS) ----
JS="""document.querySelectorAll('li.wixui-horizontal-menu__item').forEach(function(li){var pb=li.querySelector('[data-testid=positionBox]');if(!pb)return;function on(){li.setAttribute('data-hovered','true');li.setAttribute('data-shown','true');pb.style.marginTop='-4px';}function off(){li.removeAttribute('data-hovered');li.removeAttribute('data-shown');}li.addEventListener('mouseenter',on);li.addEventListener('mouseleave',off);li.addEventListener('focusin',on);li.addEventListener('focusout',function(e){if(!li.contains(e.relatedTarget))off();});});"""
for f in glob.glob('site/*.html'):
    soup=BeautifulSoup(open(f).read(),'lxml')
    for pb in soup.select('.itemDepth02233374943__positionBox'):
        if not pb.find('li'): pb.decompose()
    old=soup.find(id='menu-hover')
    if old: old.decompose()
    sc=soup.new_tag('script'); sc['id']='menu-hover'; sc.string=JS; soup.body.append(sc)
    open(f,'w').write(str(soup))
print('menus')

# ---- final touches (2026-11-11) ----
exec(open('_build/fix8.py').read())
open('site/assets/site-config.js','w').write("// Club Formspree endpoint (Formspree dashboard -> WCARC Contact -> Integration).\nwindow.WCARC_FORM_ENDPOINT = 'https://formspree.io/f/meerjpod';\n")
import subprocess
os.makedirs('site/docs',exist_ok=True)
for f in glob.glob('site/*.html')+glob.glob('site/m/*.html'):
    s=open(f).read(); pre='../' if '/m/' in f else ''
    s=s.replace('http://newwcarc.wcarc.com/wp-content/uploads/The-Williamson-County-Amateur-Radio-Club-Charter.pdf',pre+'docs/WCARC-Charter.pdf')
    s=re.sub(r'<link href="https://www\.wcarc\.com/blog-feed\.xml"[^>]*>','',s)
    open(f,'w').write(s)
