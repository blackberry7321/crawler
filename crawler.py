import requests, random, time, os, re, json
from bs4 import BeautifulSoup
import sys
from urllib.parse import urljoin, urlparse

whole_pages = {}

def visit_onion(onion_urls, depth, folder):
    if depth == 0:
        return
    
    proxies = {
        "http" : "socks5h://127.0.0.1:9150",
        "https" : "socks5h://127.0.0.1:9150"
    }
    headers = {
        "Content-Type": "application/json"
    }
    while onion_urls:
        onion_url = onion_urls.pop(0)
        if onion_url in whole_pages:
            continue  # 이미 방문한 URL은 스킵
        whole_pages[onion_url] = True  # URL 방문 기록

        data = {
            "origin_url": onion_url,
            "parameter": urlparse(onion_url).query,
            "title": "",
            "url": urlparse(onion_url).scheme + '://' + urlparse(onion_url).netloc + urlparse(onion_url).path,
            "domain": urlparse(onion_url).netloc,
            "HTML": "",
            "wordlist": [],
            "isCrawling": True
        }
        try:
            response = requests.post(onion_url, proxies=proxies, headers=headers, json=data, allow_redirects=True)
            response.close()
        except Exception as e:
            print(onion_url, e)
            continue
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            data['title'] = soup.title.text if soup.title else ""
            data['HTML'] = str(soup)
            text_nodes = soup.find_all(text=True)
            cleaned_texts = [re.sub(r'\s+', ' ', text).strip() for text in text_nodes if text.strip()]
            data['wordlist'] = cleaned_texts

            print(onion_url, response.status_code, data['title'])
            print(data['wordlist'])  # 확인용 출력
            
            new_links = set()  # 새 링크 저장
            for a in soup.findAll("a"):
                href = a.get('href', '')
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                full_url = urljoin(onion_url, href)
                if full_url not in whole_pages:
                    new_links.add(full_url)
            
            onion_urls.extend(new_links)  # 새로운 링크 추가
        else:
            print(onion_url, response.status_code, response.headers)

        depth -= 1  # 재귀 깊이 감소

def main():
    script_name = sys.argv[0]
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        visit_onion([arg], 3, arg[7:-6])
    else:
        print("인자가 제공되지 않았습니다.")

if __name__ == "__main__":
    main()
