import requests
import re
from lxml import etree
import os

# 定义一个获取漫画的类
class GetComic:
    # 初始化
    # 传入参数 name(漫画名字) url(漫画主页的url)
    def __init__(self, url):
        self.page = 1
        self.name = None
        self.base_url = re.search(r'https://\w*.(.+)', url).group(1)
        self.home_url = 'https://www.'+self.base_url
        self.home = None
        self.last_chapter = None
        self.extra_url = None
        self.url = None
        self.max_page = None
        self.home_code = None
        self.src_url = None
        self.last_src_url = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; NX563J Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/85.0.4183.127 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'If-Modified-Since': 'Sun, 20 Sep 2020 03:22:56 GMT',
            'If-None-Match': '5f66cb10-1b18c'
        }
        self.headers2 = {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "referer": "https://m.zymk.cn/2/",
            "x-requested-with": "mark.via",
            "origin": "https://m.zymk.cn",
            "accept-encoding": "gzip, deflate, br",
        }
        self.header3 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'Connection': 'keep-alive',
            'If-None-Match': 'F9BC58C7CE084A915E9DC516A718EBFE'
        }

    # 获取漫画信息
    def get_chapter(self):
        # 拼接url访问漫画的主页
        self.home = requests.get(self.home_url)

        print(self.home.text)
        # 最新更新
        self.home_code = etree.HTML(self.home.text)
        name_list = self.home_code.xpath('/html/head/meta[12]/@content')
        self.name = str(name_list[0])
        last_chapter_list = self.home_code.xpath('/html/body/div[2]/div[3]/div[1]/div/div[1]/div[2]/ul/li[1]/a[1]/@title')
        self.last_chapter = str(last_chapter_list[0])
        print(f'<<{self.name}>>最新更新到第{self.last_chapter}')

    # 选取章节,获取其url
    def select_chapter(self, num):
        extra_url_list = self.home_code.xpath(f'//li/a[@title="{num}"]/@href')
        self.extra_url = str(extra_url_list[0])
        self.url = "https://m." + self.base_url + self.extra_url + '/'
        print(self.url)

    # 获取页码
    def get_page(self):
        url_code = etree.HTML(requests.get(self.url, headers=self.headers2).text)
        max_page_list = url_code.xpath("/html/body/div[3]/div[2]/div/span/text()")
        self.max_page = int(max_page_list[0])
        print(f'本话最大页数为{self.max_page}')
        src_list = url_code.xpath('//*[@id="content"]/div/script/text()')
        src = src_list[0]
        self.src_url = re.search(r'chapter_addr_original:"(.*)",comic_name', src).group(1)
        # print(self.src_url)

        # print(requests.get("https://m.zymk.cn/2/323085.html", headers=self.headers2).text)

    # 获取本话漫画
    def get_comic(self, chapter):
        if os.path.exists(fr'./resource/{self.name}/{chapter}'):
            return 0
        os.mkdir(fr'./resource/{self.name}/{chapter}')
        for num in range(1, self.max_page+1):
            self.last_src_url = 'http://mhpic.xiaomingtaiji.net/comic/' + self.src_url + f'{num}.jpg-zymk.high'
            print(f'下载中，url为{self.last_src_url}')
            img = requests.get(self.last_src_url, headers=self.headers2).content
            with open(f'./resource/{self.name}/{chapter}/{num}.jpg', 'wb') as f:
                f.write(img)

    # 获取所有章节漫画
    def get_all_comic(self):
        self.get_chapter()
        if not os.path.exists(fr'./resource/{self.name}'):
            os.mkdir(fr'./resource/{self.name}')
        all_chapter_list = self.home_code.xpath('//ul[@id="chapterList"]/li/a/@title')
        for chapter in all_chapter_list:
            self.select_chapter(chapter)
            self.get_page()
            self.get_comic(chapter)

        print(all_chapter_list)


if __name__ == '__main__':
    getComic = GetComic('https://www.zymk.cn/881/')
    # getComic.get_chapter()
    # getComic.get_comic(getComic.result)
    # getComic.select_chapter('867话')
    # getComic.get_page()
    # getComic.get_comic()
    getComic.get_all_comic()