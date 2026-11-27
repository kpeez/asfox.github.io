import re,json,sys,html
from bs4 import BeautifulSoup
ROOT='/home/user/asfox.github.io/'
def parse_li(li):
    a=li.find('a'); em=li.find('em')
    pdf=a['href'] if a and a.get('href') else None
    title=a.get_text(' ',strip=True) if a else None
    emt=em.get_text(' ',strip=True) if em else None
    # text before the first <a>
    pre=''; post=''
    seen_a=False; seen_em=False; mid=''
    for n in li.children:
        if n is a: seen_a=True; continue
        if getattr(n,'name',None)=='span': continue
        if n is em: seen_em=True; continue
        t=n.get_text() if hasattr(n,'get_text') else str(n)
        if not seen_a: pre+=t
        elif not seen_em: mid+=t
        else: post+=t
    norm=lambda s: re.sub(r'\s+',' ',s.replace('\xa0',' ')).strip()
    return dict(pre=norm(pre),title=norm(title or ''),mid=norm(mid),em=norm(emt or ''),post=norm(post),pdf=pdf)
def parse_file(path):
    s=BeautifulSoup(open(path,encoding='utf-8').read(),'html.parser')
    out=[]
    for li in s.find_all('li'):
        if li.find('a') and li.find('em'): out.append(parse_li(li))
    return out
if __name__=='__main__':
    for p in ['category/publications.html','category/posters.html']:
        r=parse_file(ROOT+p); print(p,len(r))
        json.dump(r,open('/tmp/raw_'+p.split('/')[-1]+'.json','w'),indent=1,ensure_ascii=False)
