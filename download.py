# from scihub import SciHub
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
import re
proxy = 'http://127.0.0.1:8088'
url = 'https://sci-hub.tw/'
pdf_pattern = r'<iframe name ="pdf" src = "(.+?)" id = "pdf"></iframe>'

# sh = SciHub()

# sh.set_proxy(proxy)

# s_res = sh.search('A Collaborative Session-based Recommendation Approach with Parallel Memory Modules')
# print(s_res)
# results = sh.download('A Collaborative Session-based Recommendation Approach with Parallel Memory Modules')
# print(results)

sess = requests.Session()
sess.proxies = {
    "http": proxy,
    "https": proxy, 
}

def search(identifier):
    obj = {'request': identifier}
    for i in range(5):
        # 重复5次尝试
        res = sess.post(url, obj).text
        links = re.findall(pdf_pattern, res)
        if len(links) > 0:
            return links
    return []

def fetch(title, output):
    result = search(title)
    if len(result) > 0:
        if result[0][:2] == '//':
            result[0] = result[0][2:]
        output.writelines([title, result[0]])
        output.write('\n')
        print('link found for ' + title)
    else:
        print('no result for ' + title)

# 并行搜索论文
async def get_data():
    with ThreadPoolExecutor(max_workers=30) as executor:
        loop = asyncio.get_event_loop()
        tasks = []
        print('***SIGIR***')
        sigir = open('SIGIR.txt', encoding='utf-8')
        sigir_links = open('SIGIR Links.txt', 'w')
        for line in sigir.readlines():
            if line[:8] == 'title:  ':
                title = line[8:]
                tasks.append(loop.run_in_executor(
                    executor,
                    fetch,
                    *(title, sigir_links) # Allows us to pass in multiple arguments to `fetch`
                ))
        for response in await asyncio.gather(*tasks):
            pass
        sigir.close()
        sigir_links.close()

        tasks = []
        print('***RecSys***')
        recsys = open('RecSys.txt', encoding='utf-8')
        recsys_links = open('RecSys Links.txt', 'w')
        for line in recsys.readlines():
            if len(line) > 1 and line[0] != '*':
                title = line
                tasks.append(loop.run_in_executor(
                    executor,
                    fetch,
                    *(title, recsys_links) # Allows us to pass in multiple arguments to `fetch`
                ))
        for response in await asyncio.gather(*tasks):
            pass
        recsys.close()
        recsys_links.close()

def main():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data())
    loop.run_until_complete(future)

if __name__ == '__main__':
    main()
