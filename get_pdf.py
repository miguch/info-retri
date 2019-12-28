# from scihub import SciHub
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import requests
from io import BytesIO
import re
proxy = 'http://127.0.0.1:8088'
captcha_pattern = r'<img id="captcha" src="(.+?)" />'
id_pattern = r'<input type[ ]?=[ ]?"hidden" name[ ]?=[ ]?"id" value[ ]?=[ ]?"(.+?)">'
baseUrl = 'https://dacemirror.sci-hub.tw'

sess = requests.Session()
sess.proxies = {
    "http": proxy,
    "https": proxy, 
}

def showImage(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.show()

def download(name, url, subName):
    print(name[:-1])
    while True:
        result = sess.get('https://' + url)
        contentType = result.headers['content-type']
        if contentType == 'application/pdf':
            # 下载 pdf
            with open('papers/%s/%s.pdf'%(subName, name), 'wb') as pdf:
                pdf.write(result.content)
            print('*downloaded*')
            break
        else:
            # 处理验证码
            captcha_links = re.findall(captcha_pattern, result.text)
            id_str = re.findall(id_pattern, result.text)
            if len(captcha_links) == 0:
                continue
            showImage(baseUrl + captcha_links[0])
            captcha = input('Enter Captcha: ')
            result = sess.post('https://' + url, {'answer': captcha, 'id': id_str[0]})
            contentType = result.headers['content-type']
            if contentType == 'application/pdf':
                # 下载 pdf
                with open('papers/%s/%s.pdf'%(subName, name), 'wb') as pdf:
                    pdf.write(result.content)
                print('*downloaded*')
                break

# 并行搜索论文
def get_data():
    print('***SIGIR***')
    # sigir = open('SIGIR Links.txt')
    # for title in sigir:
    #     url = sigir.readline()
    #     download(title, url, 'SIGIR')
    # sigir.close()

    print('***RecSys***')
    recsys = open('RecSys Links.txt', errors='ignore')
    for title in recsys:
        url = recsys.readline()
        download(title, url, 'RecSys')
    recsys.close()

def main():
    get_data()

if __name__ == '__main__':
    main()
