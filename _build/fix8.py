import glob
from bs4 import BeautifulSoup
CSS="fluid-columns-repeater[justify-content=center]{display:flex!important;flex-wrap:wrap;justify-content:center!important}fluid-columns-repeater[justify-content=center]>*{position:relative!important;left:auto!important;margin-left:0!important;margin-right:0!important}"
for f in glob.glob('site/*.html'):
    s=BeautifulSoup(open(f).read(),'lxml')
    if not s.find('fluid-columns-repeater'): continue
    old=s.find(id='repeater-center')
    if old: old.decompose()
    st=s.new_tag('style'); st['id']='repeater-center'; st.string=CSS; s.head.append(st)
    open(f,'w').write(str(s)); print('patched',f)
