zhiyin_comic

---
title: 从知音漫客上下载漫画(核心脚本实现)
tags: 
			- python
			- 爬虫
---
  
# 前言
* 好久没看知音漫客了,突然想起来看,但是知音漫客上看漫画有个缺点,就
是登录很麻烦,而且每次重新登录以后就会忘记之前看漫画的进度,所以就想
直接将漫画下载下来在本地看,这样每次只要在本地操作就可以享受漫画了  
ps:果然还是偷懒是第一生产力!!
<br>
<br>
<!--more-->
# 流程
* 说干就干,开始设计爬虫的流程.

## 一.分析url

1. 观察漫客网上的url,用F12的开发者工具打开网页代码查看器,并用定位功能,
发现漫画原图的url,这里用一话的斗破苍穹的漫画作为示例,找到漫画的原图url.

    ```html
    http://mhpic.xiaomingtaiji.net/comic/D%2F%E6%96%97%E7%A0%B4%E8%8B%8D%E7%A9%B9%2F%E7%AC%AC841%E8%AF%9DF1_262538%2F1.jpg-zymk.middle.webp
    ```

2. 分析url,前部为域名,comic固定,重点就在后面这串神秘代码,这一段应该是包含漫画信息的了,
复制这段url到网页中看看什么情况.发现在浏览器的显示中解析了这段神秘代码,果然这段代码的信息就是漫画的信息,
解析后的url写作如下:

    ```html
    http://mhpic.xiaomingtaiji.net/comic/D%2F%斗破苍穹2F%第841话F1_262538%2F1.jpg-zymk.middle.webp
    ```
3. 可以很明显的看出来对应的关系那么原url的通式可以写作如下:
    ```html
    http://mhpic.xiaomingtaiji.net/comic/D%2F%{漫画名代码}2F%E7%AC%AC{第n话}%E8%AF%9DF1_262538%2F{页码}.jpg-zymk.middle.webp
    ```
    将对应的参数的修改好就能访问了.
4. 除此之外,如果手动去获取url的话,会因为每一话的页码不同,导致url的获取有错误,所以需要进一步分析网页代码,
查看有没有获取页码数的方法,在漫画页面定位页码位置,马上可以的到一个xpath,这里就有本话的页码信息:
    ```html
    /html/body/div[3]/div/div[2]/div[1]/span[2]
    ```
5. 拿到url和页码就能进行下一步的爬虫获取了.

## 二.爬虫设计

1. 获取漫画基本信息（包括漫画名，最新更新的章节数，每话的extra_url） 
2. 拼接url，模拟移动端访问网页，进入章节，获取本话的最大页码
3. 从页面中，使用正则表达式，筛选出漫画本身的url，并进行拼接，用get访问后，使用循环保存至章节文件夹
4. 创建一个方法，直接下载全本漫画，依次完成：
    - 获取漫画信息
    ```html
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
    ```
    - 创建一个漫画名文件夹
    ```html
    if not os.path.exists(fr'./resource/{self.name}'):
       os.mkdir(fr'./resource/{self.name}')
    ```
    - 模拟访问移动端网页
    ```html
        def select_chapter(self, num):
           extra_url_list = self.home_code.xpath(f'//li/a[@title="{num}"]/@href')
           self.extra_url = str(extra_url_list[0])
           self.url = "https://m." + self.base_url + self.extra_url + '/'
           print(self.url)
    ```
    - 循环下载漫画每一页，保存至章节文件夹  
    ```html
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
   ```
5. 创建一个方法，下载未下载的更新漫画
    - 获取漫画信息
    - 遍历漫画章节数，依次检查本地章节文件夹，当本地文件夹内已有本文件夹时，代表已有文件，此时停止遍历
    - 将章节数列表进行切片，仅获得未下载的更新话列表，对其依次遍历，使用get_comic完成下载

# 常见问题
1. 页面的url很离谱，要认真仔细才看的明白
2. PC端的html和移动端的html源代码不一样，在PC端无法读取的东西可以通过模拟移动端获取，
尤其是获得漫画原始url时，pc端加密无法破解。

# 版本
**v1.0.0**   
<br><br>
*本爬虫仅供学习参考，禁止传播与商用*
   
# 相关链接
 [个人博客] (https://myblog.icanqi.cn)  
 [github] (github.com/zhong131899/zhiyin_comic)
