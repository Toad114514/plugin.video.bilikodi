import requests as req
import json, os, time, requests
import xbmcaddon, xbmcvfs, xbmc, xbmcgui

import resources.lib.get as g
import resources.lib.secret as s
import resources.lib.core as c

from bs4 import BeautifulSoup

ADDON=xbmcaddon.Addon()
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

UA_head = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; PBAM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 EdgA/114.0.1823.74'
}

def save_cookie(rep):
    dictc = req.utils.dict_from_cookiejar(rep.cookies)
    # 添加一些空值以通过部分api风控
    # 如用户基础信息APi
    dictc["a"] = ""
    dictc["b"] = ""
    with open(os.path.join(ADDON_PATH, "resources", "config", "cookies"),"w") as f:
        json.dump(dictc, f, indent=4)
        
def load_cookie():
    try:
        with open(os.path.join(ADDON_PATH, "resources", "config", "cookies"),"r") as f:
            dictc = json.loads(f.read())
        return req.utils.cookiejar_from_dict(dictc)
    except:
        c.log("无cookies。")
        return False

# 旧 cookies
def save_cookie_old():
    old = os.path.join(ADDON_PATH, "resources", "config", "cookies")
    oldo = os.path.join(ADDON_PATH, "resources", "config", "cookies.old")
    with open(old, "rb") as src, open(oldo, "wb") as dst:
        dst.write(src.read())

def load_cookie_old():
    with open(os.path.join(ADDON_PATH, "resources", "config", "cookies.old"),"r") as f:
        dictc = json.loads(f.read())
    return req.utils.cookiejar_from_dict(dictc)

# 读取 cookies
# param: key [cookiejar]
def read_cookie(key):
    q=req.utils.dict_from_cookiejar(load_cookie())
    return q[key]

# 刷新密钥（长久保存）
def save_ref_token(data):
    if os.path.exists(os.path.join(ADDON_PATH, "resources", "config", "refresh_token")):
        os.remove(os.path.join(ADDON_PATH, "resources", "config", "refresh_token"))
    with open(os.path.join(ADDON_PATH, "resources", "config", "refresh_token"),"w") as f:
        f.write(data)

def load_ref_token():
    with open(os.path.join(ADDON_PATH, "resources", "config", "refresh_token"),"r") as f:
        ref_token = f.read()
    return ref_token

# 通过 cookies 返回当前用户mid
def get_mid():
    res=requests.get("https://api.bilibili.com/x/web-interface/nav", headers=UA_head, cookies=load_cookie()).json()
    if res["code"] != 0:
        return 0
    return res["data"]["mid"]

# 网页端 Cookies 刷新实现代码
# 可能有bug。

def cookie_ok(newcsrf, refkey):
    url="https://passport.bilibili.com/x/passport-login/web/confirm/refresh"
    param={
      'csrf': newcsrf, # new csrf
      'refresh_token': refkey #oldrefkey
    }
    try:
        res=requests.post(url, data=param)
        res_text = json.loads(res.text)
    except requests.exceptions.RequestException as e:
        xbmc.log("网络不好")
    if c.check_json(res.text):
        # 检测
        if cd == 0:
            xbmcgui.Dialog().ok("ok", "refresh_key 和 cookie 应该已完成更新")
        else:
            if cd == -101:
                xbmc.log("未登录")
            if cd == -111:
                xbmc.log("csrf error")
            if cd == -400:
                xbmc.log("请求错误")
    else:
        xbmc.log("无法解析")

def cookie_real_ref(csrf, ref_csrf, ref_token):
    url="https://passport.bilibili.com/x/passport-login/web/cookie/refresh"
    param={
      'csrf': csrf, # bili_jct in cookie
      'refresh_csrf': ref_csrf, # corrkey
      'source': 'main_web', # default main web
      'refresh_token': ref_token # longer refresh_token
    }
    # 检测
    try:
        res=requests.post(url, data=param)
        res_text = res.text
    except requests.exceptions.RequestException as e:
        xbmc.log("网络不好")
    if c.check_json(res.text):
        res_text = json.loads(res_text)
        # 检测是否正常
        cd=res_text["code"]
        if cd == -101:
            xbmc.log("未登录")
        elif cd == -111:
            xbmc.log("csrf key error")
        elif cd == 86095:
            xbmc.log("refresh_csrf 错误或 refresh_token 与 cookie 不匹配")
        elif cd == 0:
            xbmc.log("存储新cookies")
            # 保存 cookies
            save_cookie(res)
            # save refresh_token
            save_ref_token(res["data"]["refresh_token"])
            # 作废
            new_csrf=read_cookie("bili_jct")
            xbmc.log("开始作废旧 refresh_token")
            cookie_ok(new_csrf, ref_token)
        else:
            print("未知错误: "+ res_text, xbmc.LOGINFO)
    else:
        xbmc.log("[Bilikodi] 无法解析 json 数据")
    

def cookie_ref(dev):
    url="https://passport.bilibili.com/x/passport-login/web/cookie/info"
    res = g.getback_c(url, UA_head, load_cookie())
    if res == False:
        xbmc.log("刷新cookies时出现问题。")
        return False
    else:
        if res["data"]["refresh"] or dev == True:
            # cpkey
            cpkey=s.getCorrespondPath(round(time.time() * 1000))
            xbmc.log("获取cpkey: "+cpkey)
            csrf=requests.get("https://www.bilibili.com/correspond/1/"+cpkey, headers=UA_head, cookies=load_cookie())
            if csrf == False:
                xbmc.log("未知错误。")
                xbmcgui.Dialog().ok("e","无法刷新 cookies")
                return
            # get html id 1-name
            soup = BeautifulSoup(csrf.text, "html.parser")
            csrfkey = soup.find("div", id="1-name").text
            # try refresh cookie
            csrf=read_cookie("bili_jct")
            reft=load_ref_token()
            cookie_real_ref(csrf, csrfkey, reft)
        else:
            xbmc.log("已检查，无需刷新cookies。")
            xbmcgui.Dialog().ok("ok", "无需刷新cookie")
    
    