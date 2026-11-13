import re, os, hashlib, glob, html, urllib.parse, concurrent.futures, requests
import sys
V=sys.argv[1] if len(sys.argv)>1 else 'd'
SRC='raw-'+V; OUT='/tmp/cap/site'+('' if V=='d' else '/m'); A='/tmp/cap/site/assets'
os.makedirs(A,exist_ok=True)
PAGES={'/':'index','/about-6':'about','/contact-8':'contact','/pricing-plans/plans-pricing':'membership','/general-5':'club-information','/blog':'blog','/general-9':'field-day','/general-clean-1':'presentations','/general-clean-2':'faqs','/event-list':'events','/repeaters-map':'repeaters-map','/post/wcarc-saturday-breakfast':'post-wcarc-saturday-breakfast','/post/2025-wcarc-picnic':'post-2025-wcarc-picnic','/general-clean':'newsletters'}
URLRE=re.compile(r'''(?:https?:)?//(?:static\.wixstatic\.com|static\.parastorage\.com|siteassets\.parastorage\.com|pages\.parastorage\.com|staticorigin\.wixstatic\.com|www\.wcarc\.com/_files|video\.wixstatic\.com)[^"'\s)<>*]*?(?=&quot;|&#34;|["'\s)<>*]|$)''')
sess=requests.Session(); cache={}
def hires(full):
    def dbl(m):
        return m.group(1)+'w_%d,h_%d'%(int(m.group(2))*2,int(m.group(3))*2)
    return re.sub(r'(/v1/(?:fill|fit|crop/[^/]*/fill)/)w_(\d+),h_(\d+)',dbl,full)
def fetch(u):
    full=hires(html.unescape(u if u.startswith('http') else 'https:'+u))
    p=urllib.parse.urlparse(full); ext=os.path.splitext(p.path.split('/v1/')[0] if '/v1/' in p.path else p.path)[1][:6]
    if '/v1/fill/' in p.path or '/v1/fit/' in p.path or '/v1/crop/' in p.path:
        ext=os.path.splitext(p.path)[1][:6] or ext
    if 'contentType=text%2Fcss' in full or 'contentType=text/css' in full: ext='.css'
    name=hashlib.md5(full.encode()).hexdigest()[:16]+(ext or '')
    dst=os.path.join(A,name)
    if not os.path.exists(dst):
        try:
            r=sess.get(full,timeout=60)
            if r.status_code!=200: return u,None
            data=r.content
            if (ext=='.css' or 'text/css' in r.headers.get('content-type','')):
                txt=data.decode('utf-8','ignore'); 
                # nested assets in css
                for m in set(URLRE.findall(txt)):
                    _,n=fetch(m)
                    if n: txt=txt.replace(m,n)
                data=txt.encode()
            open(dst,'wb').write(data)
        except Exception as e: print('fail',full[:100],e); return u,None
    return u,name
for f in glob.glob(SRC+'/*.html'):
    s=open(f).read()
    urls=sorted(set(URLRE.findall(s)),key=len,reverse=True)
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        res=list(ex.map(fetch,urls))
    for u,n in res:
        if n: s=s.replace(u,('assets/' if V=='d' else '../assets/')+n)
    # internal links
    def lk(m):
        path=m.group(1).rstrip('/') or '/'
        path=path.split('?')[0].split('#')[0]
        return 'href="'+(PAGES.get(path)+'.html' if path in PAGES else 'https://www.wcarc.com'+m.group(1))+'"'
    s=re.sub(r'href="https://www\.wcarc\.com(/[^"]*)?"',lambda m: lk(type('M',(),{'group':lambda self,i: m.group(1) or '/'})()),s)
    s=s.replace('</head>','<style id="freeze-fix">*:not(:defined){visibility:visible!important}fluid-columns-repeater,fluid-columns-repeater *{visibility:visible}wow-image.bgImage img{width:100%!important;height:100%!important}</style></head>',1)
    open(os.path.join(OUT,os.path.basename(f)),'w').write(s)
    print(os.path.basename(f),len(urls),sum(1 for _,n in res if not n),'unresolved')
