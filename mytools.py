#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project ：${PROJECT_NAME}
# @File    ：${NAME}.py
# @Author  ：吾非同
# @Date    ：${DATE} ${TIME}
import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from redis import StrictRedis

load_dotenv(verbose=True)
# TODO: 部署正式环境记得换.env中的内容
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_PASS = os.getenv("REDIS_PASS")


def find_url(string: str):
    # findall() 查找匹配正则表达式的字符串
    url_regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](
    ?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name
    |post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba
    |bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl
    |cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj
    |fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr
    |ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz
    |la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt
    |mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm
    |pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so
    |sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug
    |uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[
    \]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[
    ^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[
    .\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs
    |mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as
    |at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd
    |cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh
    |er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu
    |gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km
    |kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn
    |mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe
    |pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj
    |Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr
    |tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(
    ?!@)))"""

    url = re.findall(url_regex, string)
    if url:
        return url[0][0]
    else:
        print(f"url={url}")


def check_session_id(request):
    try:
        session_id = str(dict(request["headers"])[b"sessionid"], encoding="utf-8")
        redis = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASS)
        return redis.exists(session_id)
    except (SyntaxError, KeyError):
        return 0


class Video:
    status_code = int
    video_info = {
        "video": "",
        "cover": "",
        "desc": "",
        "app_name": "",
        "music": {
            "title": "",
            "author": "",
            "cover_hd": "",
            "play_url": "",
            "duration": "",
        },
        "author": {
            "nickname": "",
            "signature": "",
            "avatar_larger": "",
            "unique_id": "",
        },
    }

    def __init__(self, url):
        self.url = url

    def douyin(self):
        res = requests.get(url=self.url)
        if res.status_code == 200:
            Video.status_code = 200
            regex = re.compile(r"/video/(.*)\?")
            video_id = regex.match(res.request.path_url).group(1)
            info_url = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids="
            res_info = requests.get(url=info_url + video_id)
            item_list = res_info.json()["item_list"][0]
            play_addr = item_list["video"]["play_addr"]["url_list"][0]
            play_addr = play_addr.replace("playwm", "play")
            Video.video_info["app_name"] = "抖音"
            Video.video_info["video"] = play_addr
            Video.video_info["cover"] = item_list["video"]["cover"]["url_list"]
            Video.video_info["desc"] = item_list["desc"]
            Video.video_info["music"]["title"] = item_list["music"]["title"]
            Video.video_info["music"]["author"] = item_list["music"]["author"]
            Video.video_info["music"]["cover_hd"] = item_list["music"]["cover_hd"][
                "url_list"
            ][0]
            Video.video_info["music"]["play_url"] = item_list["music"]["play_url"][
                "url_list"
            ][0]
            Video.video_info["music"]["duration"] = item_list["music"]["duration"]
            Video.video_info["author"]["nickname"] = item_list["author"]["nickname"]
            Video.video_info["author"]["signature"] = item_list["author"]["signature"]
            Video.video_info["author"]["avatar_larger"] = item_list["author"][
                "avatar_larger"
            ]["url_list"][0]
            Video.video_info["author"]["unique_id"] = item_list["author"]["unique_id"]

    def pi_pi_xia(self):
        res = requests.get(url=self.url)
        if res.status_code == 200:
            Video.status_code = 200
            regex = re.compile(r"/item/(.*)\?")
            video_id = regex.match(res.request.path_url).group(1)
            info_url = "https://is.snssdk.com/bds/cell/detail/?cell_type=1&aid=1319&app_name=super&cell_id="
            res_info = requests.get(url=info_url + video_id)
            item_list = res_info.json()["data"]["data"]["item"]
            play_addr = res_info.json()["data"]["data"]["item"][
                "origin_video_download"
            ]["url_list"][0]["url"]
            Video.video_info["app_name"] = "皮皮虾"
            Video.video_info["video"] = play_addr
            Video.video_info["cover"] = item_list["cover"]["url_list"][0]["url"]
            Video.video_info["desc"] = item_list["content"]
            # TODO: 没找到音乐，待找
            Video.video_info["author"]["nickname"] = item_list["author"]["name"]
            Video.video_info["author"]["signature"] = item_list["author"]["description"]
            Video.video_info["author"]["avatar_larger"] = item_list["author"]["avatar"][
                "url_list"
            ][0]
            Video.video_info["author"]["unique_id"] = item_list["author"]["id_str"]

    def huo_shan(self):
        res = requests.get(url=self.url)
        if res.status_code == 200:
            Video.status_code = 200
            video_id = re.search(r"item_id=(.*)&tag=", res.request.path_url).group(1)
            info_url = "https://share.huoshan.com/api/item/info?item_id="
            res_info = requests.get(url=info_url + video_id)
            item_list = res_info.json()["data"]
            play_addr = item_list["item_info"]["url"]
            Video.video_info["app_name"] = "火山"
            Video.video_info["video"] = play_addr
            Video.video_info["cover"] = item_list["item_info"]["cover"]

    def wei_shi(self):
        if "h5.weishi" in self.url:
            video_id = self.url
        else:
            video_id = re.search(r"&id=(.*)&spid=", self.url).group(1)
        info_url = "https://h5.weishi.qq.com/webapp/json/weishi/WSH5GetPlayPage?feedid="
        res_info = requests.get(url=info_url + video_id)
        if res_info.status_code == 200:
            Video.status_code = 200
        else:
            Video.status_code = 400
        item_list = res_info.json()["data"]["feeds"][0]
        play_addr = item_list["video_url"]
        Video.video_info["app_name"] = "微视"
        Video.video_info["video"] = play_addr
        Video.video_info["cover"] = item_list["video_cover"]["static_cover"]["url"]
        Video.video_info["desc"] = item_list["feed_desc"]
        Video.video_info["music"]["title"] = item_list["music_info"]["songInfo"][
            "strName"
        ]
        Video.video_info["music"]["cover_hd"] = item_list["music_info"]["albumInfo"][
            "strPic"
        ]
        Video.video_info["music"]["play_url"] = item_list["music_info"]["songInfo"][
            "strPlayUrl"
        ]
        Video.video_info["music"]["duration"] = item_list["music_info"]["songInfo"][
            "iPlayTime"
        ]
        Video.video_info["author"]["nickname"] = item_list["poster"]["nick"]
        Video.video_info["author"]["signature"] = item_list["poster"]["status"]
        Video.video_info["author"]["avatar_larger"] = item_list["poster"]["avatar"]

    def wei_bo(self):
        if "show?fid=" in self.url:
            video_id = re.search(r"fid=(.*)", self.url).group(1)
        else:
            video_id = re.search(r"(\d+):\d+", self.url).group(1)
        res_info = weibo_request(video_id)
        try:
            if res_info.status_code == 200:
                Video.status_code = 200
                item_list = res_info.json()["data"]["Component_Play_Playinfo"]
                key_one = list(item_list["urls"].keys())[0]
                play_addr = item_list["urls"][key_one]
                Video.video_info["app_name"] = "微博"
                Video.video_info["video"] = f"https:{play_addr}"
                Video.video_info["cover"] = item_list["cover_image"]
                Video.video_info["desc"] = item_list["text"]
        except TypeError:
            print(
                f"""
            ==========weibo TypeError Begin===========
            传入url: {self.url}
            返回json: {res_info}
            """
            )

    def lv_zhou(self):
        res = requests.get(url=self.url)
        if res.status_code == 200:
            Video.status_code = 200
            soup = BeautifulSoup(res.text, "html.parser")
            item_video = soup.select("body > div.oasis > div.media > div > video")
            item_cover_tmp = soup.select(
                "body > div.oasis > div.media > div > div.video-cover"
            )
            item_cover = re.search(r"\((.*)\)", item_cover_tmp[0].attrs["style"]).group(
                1
            )
            item_desc = soup.select(
                "body > div.oasis > div.content.btn-status > div.main-content > div.status-text"
            )
            item_nick = soup.select(
                "body > div.oasis > div.content.btn-status > div.user > div"
            )
            item_avatar = soup.select(
                "body > div.oasis > div.content.btn-status > div.user > a > img"
            )
            Video.video_info["app_name"] = "绿洲"
            Video.video_info["video"] = item_video[0].attrs["src"]
            Video.video_info["cover"] = item_cover
            Video.video_info["desc"] = item_desc[0].contents[0].text
            Video.video_info["author"]["nickname"] = item_nick[0].contents[0].text
            Video.video_info["author"]["avatar_larger"] = item_avatar[0].attrs["src"]

    def zui_you(self):
        res_info = my_request(url=self.url)
        if res_info.status_code == 200:
            Video.status_code = 200
            Video.video_info["video"] = re.search(
                r"urlsrc\": \"(.*)\"", res_info.text
            ).group(1)
            Video.video_info["cover"] = ""
            Video.video_info["desc"] = ""
            Video.video_info["music"]["title"] = ""
            Video.video_info["music"]["author"] = ""
            Video.video_info["music"]["cover_hd"] = ""
            Video.video_info["music"]["play_url"] = ""
            Video.video_info["music"]["duration"] = ""
            Video.video_info["author"]["nickname"] = ""
            Video.video_info["author"]["signature"] = ""
            Video.video_info["author"]["avatar_larger"] = ""
            Video.video_info["author"]["unique_id"] = ""

    def bilibili(self, url):
        pass

    def kuai_shou(self):
        r = my_request(url=self.url)
        cookies = dict(r.headers)["Set-Cookie"]
        headers = {
            "Referer": r.request.url,
            "User-Agent": dict(r.request.headers)["User-Agent"],
        }
        headers = 1

    def quan_min(self):
        if "quanmin.baidu.com/v/" in self.url:
            vid = re.search(r"v/(.*?)\?", self.url).group(1)
        else:
            vid = re.search(r"vid=(.*)&shareTime", self.url).group(1)
        url = f"https://quanmin.hao222.com/wise/growth/api/sv/immerse?source=share-h5&pd=qm_share_mvideo&vid={vid}&_format=json"
        res_info = my_request(url=url)
        if res_info.status_code == 200:
            Video.status_code = 200
            item_list = res_info.json()["data"]
            Video.video_info["app_name"] = "度小视"
            Video.video_info["video"] = item_list["meta"]["video_info"]["clarityUrl"][
                2
            ]["url"]
            Video.video_info["cover"] = item_list["meta"]["image"]
            Video.video_info["desc"] = item_list["meta"]["title"]

    def movie_base(self, url):
        pass

    def xia_tou(self, url):
        pass

    def kai_yan(self, url):
        pass

    def momo(self, url):
        pass

    def vue_vlog(self, url):
        pass

    def xiao_ka_xiu(self, url):
        pass

    def pi_pi_gao_xiao(self, url):
        pass

    def quan_min_kge(self):
        sid = re.search(r"play_v2\?s=(.*)&shareuid", self.url).group(1)
        url = f"https://kg.qq.com/node/play?s={sid}"
        res_info = requests.get(url=url).text
        if res_info:
            Video.status_code = 200
            Video.video_info["app_name"] = "全民K歌"
            Video.video_info["video"] = re.search(
                r"playurl_video\":\"(.*?)\"", res_info
            ).group(1)
            Video.video_info["cover"] = re.search(r"cover\":\"(.*?)\"", res_info).group(
                1
            )
            Video.video_info["desc"] = re.search(
                r'<p class="singer_say__cut">(.*)</p>', res_info
            ).group(1)

    def xi_gua(self, url):
        pass

    def dou_pai(self, url):
        pass

    def six_room(self, url):
        pass

    def hu_ya(self, url):
        pass

    def pear(self, url):
        pass

    def xin_pian_chang(self, url):
        pass

    def meipai(self, url):
        pass

    def acfun_curl(self, url):
        pass

    def set_info(self):
        pass


def my_request(url, headers=""):
    header = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
    }
    if headers:
        header = headers
    res = requests.get(url=url, headers=header)
    return res


def weibo_request(video_id: str):
    cookie = {
        "login_sid_t": "6b652c77c1a4bc50cb9d06b24923210d",
        "cross_origin_proto": "SSL",
        "WBStorage": "2ceabba76d81138d|undefined",
        "_s_tentry": "passport.weibo.com",
        "Apache": "7330066378690.048.1625663522444",
        "SINAGLOBAL": "7330066378690.048.1625663522444",
        "ULV": "1625663522450:1:1:1:7330066378690.048.1625663522444:",
        "TC-V-WEIBO-G0": "35846f552801987f8c1e8f7cec0e2230",
        "SUB": "_2AkMXuScYf8NxqwJRmf8RzmnhaoxwzwDEieKh5dbDJRMxHRl"
        "-yT9jqhALtRB6PDkJ9w8OaqJAbsgjdEWtIcilcZxHG7rw",
        "SUBP": "0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5Qx3Mf.RCfFAKC3smW0px0",
        "XSRF-TOKEN": "JQSK02Ijtm4Fri-YIRu0-vNj",
    }
    post_data = {"data": f'{{"Component_Play_Playinfo":{{"oid":"{video_id}"}}}}'}
    header = {
        "referer": f"https://weibo.com/tv/show/{video_id}",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    res = requests.post(
        url=f"https://weibo.com/tv/api/component?page=/tv/show/{video_id}",
        data=post_data,
        cookies=cookie,
        headers=header,
    )
    return res


if __name__ == "__main__":
    check_session_id("5a0d879a2a3b11eda50af131fcd020c7")
