import wikipediaapi
from time import time
from bs4 import BeautifulSoup
from urllib.request import urlopen
from IPython.core.debugger import set_trace
from pytrends.request import TrendReq
import requests
import json
import asyncio
import re
import time


def brandinfo(bname):
    endpoint = 'https://autocomplete.clearbit.com/v1/companies/suggest?query='
    doc = requests.get(endpoint + bname)
    info = json.loads(doc.text)
    return info

def brandinfos(*bnames):
    return {bname:brandinfo(bname) for bname in bnames}


class Gtrend:
    def __init__(self, brand):
        kw_list = [brand]
        self.brand = brand
        self.pytrends = TrendReq()
        self.pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo='', gprop='froogle')

    def trend(self):
        return self.pytrends.interest_over_time().drop(columns=['isPartial'])

    def queries(self):
        return self.pytrends.related_queries()[self.brand]


def brand_from_wiki(*categories, names_db=[], limit=None):

    def _pages(cats, names):
        wk = wikipediaapi.Wikipedia('en')
        pages = {}
        [pages.update(wk.page(cat).categorymembers) for cat in cats]
        #[pages.pop(name, None) for name in names]
        return {k:v for k,v in pages.items() if (k not in names) & (v.ns==0)}

    def _url(page):
        return page.canonicalurl

    def _desc(page):
        return page.summary

    def _parse_logo_url(soup):
        tags = soup.find_all('td', class_='logo')

        if len(tags)==0:
            tags = soup.find_all('a', class_='image', href=re.compile('.*logo.*'))

        if len(tags)==1:
            return  tags[0].img['src']

        elif len(tags)==0:
            return ''

        else:
            return tags[0].img['src'] #'err'

    def _read(url):
        return urlopen(url).read()


    async def fetch(page):
        url = await loop.run_in_executor(None, _url, page)
        #resp = await loop.run_in_executor(None, urlopen, url)
        #html = await loop.run_in_executor(None, resp.read)
        html = await loop.run_in_executor(None, _read, url)
        soup = await loop.run_in_executor(None, BeautifulSoup, html, 'lxml')
        logo_url = await loop.run_in_executor(None, _parse_logo_url, soup)

        #if (logo_url!='') & (logo_url!='err'):
        # page 전체를 db에 미리 저장해놓기 위해 logo_url='' 인 경우도 모두 저장
        # 이렇게하지 않으면, 카테고리 페이지에서 늘 크롤링 할게 생긴다
        desc = await loop.run_in_executor(None, _desc, page)
        return (page.title, {'logo':logo_url, 'desc':desc})


    async def main():
        st = time.time()
        pages = _pages(categories, names_db)
        print(time.time()-st)

        if len(pages)==0:
            print('**********')
            return {}

        else:
            futures = [asyncio.ensure_future(fetch(page)) for page in list(pages.values())[:limit]]# if page.ns==0]
            result = await asyncio.gather(*futures)
            return dict([res for res in result if res])


    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()          # 이벤트 루프를 얻음
    res = loop.run_until_complete(main())    # main이 끝날 때까지 기다림
    loop.close()                             # 이벤트 루프를 닫음

    return res
