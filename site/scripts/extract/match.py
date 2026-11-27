import csv,json,re,sys
sys.path.insert(0,'/home/user/asfox.github.io/site/scripts/extract')
from parse_raw import *
from bs4 import BeautifulSoup
inv=list(csv.DictReader(open(ROOT+'audit/data/inventory.csv')))
pubs=json.load(open('/tmp/raw_publications.html.json')); posts=json.load(open('/tmp/raw_posters.html.json'))
def key(x): return (x['pdf'],x['title'],x['pre'])
pages={}
for row in inv:
    if row['type'] in('journal-publication','book-chapter','conference-poster-talk','STALE-not-in-archives'):
        f=row['file']
        s=BeautifulSoup(open(ROOT+f,encoding='utf-8').read(),'html.parser')
        t=s.find('time'); 
        lis=[parse_li(li) for li in s.find_all('li') if li.find('a')]
        # article only
        art=s.find('article')
        lis=[parse_li(li) for li in art.find_all('li')] if art else lis
        pages[f]=dict(row=row,lis=lis,time=t['datetime'][:10] if t else None,h1=(art.find('h1').get_text(strip=True) if art else None))
json.dump(pages,open('/tmp/pages.json','w'),indent=1,ensure_ascii=False)
for f,p in pages.items():
    if len(p['lis'])!=1: print('LIS',f,len(p['lis']))
