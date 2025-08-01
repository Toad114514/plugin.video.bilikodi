import os, sys, requests, json, random, string
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
import pyqrcode
from urllib.parse import urlencode, parse_qsl

from resources.lib.get import *
from resources.lib.cookie import *
from resources.lib.xbmc import *

HANDLE = int(sys.argv[1])
URL = sys.argv[0]
ADDON=xbmcaddon.Addon()
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

# Dirs
IMAGE_dir = os.path.join(ADDON_PATH, 'resources', 'images')
# good folder
fanart_bg = os.path.join(ADDON_PATH, "fanart.png")
folder_icon = os.path.join(IMAGE_dir, "folder.png")

UA_head = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; PBAM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 EdgA/114.0.1823.74'
}

def log(string):
    strings = "[plugin.video.bilikodi](info): "+string
    xbmc.log(strings, xbmc.LOGINFO)

def check_login():
    if os.path.exists(os.path.join(ADDON_PATH, "resources", "config", "cookies")):
        return True
    else:
        return False

def check_json(jsondata):
    try:
        data = json.loads(jsondata)
        return True
    except:
        return False

def start():
    # tips
    xbmcgui.Dialog().ok("登录", "未检测到Cookies，需登录您的b站账号才能使用\n（只是为了API稳定返回数据而已）")
    xbmcplugin.setPluginCategory(HANDLE, '登录')
    addXbmcItemInfo("二维码扫码","qrcode","生成二维码然后给你扫码登录",True)
    addXbmcItem("直接输入 Cookies（输一辈子，所以不实现。）","not",True)
    xbmcplugin.endOfDirectory(HANDLE)

# new
def qrcode_get():
    if check_login():
        xbmcgui.Dialog().ok("提示", "不要重复登录！")
        return
    try:
        res = requests.get('https://passport.bilibili.com/x/passport-login/web/qrcode/generate', headers=UA_head).json()
    except:
        xbmcgui.Dialog().ok("错误","无法获取二维码，请检查网络。")
        return
    # get url and key
    qrcode_url=res["data"]["url"]
    qrcode_key=res["data"]["qrcode_key"]
    qrc = pyqrcode.create(qrcode_url+qrcode_key)
    # 检测
    if os.path.exists(os.path.join(ADDON_PATH, "resources", "config", "qrcode.png")):
        os.remove(os.path.join(ADDON_PATH, "resources", "config", "qrcode.png"))
    qrc.png(os.path.join(ADDON_PATH, "resources", "config", "qrcode.png"), scale=6)
    qrcode_img=os.path.join(ADDON_PATH, "resources", "config", "qrcode.png")
    xbmcgui.Dialog().ok("提示", "请拿起手机打开b站客户端\n我的 -> 右上角扫码图标\n进行扫码确认登录")
    xbmc.executebuiltin('ShowPicture(%s)' % qrcode_img)
    login_status(qrcode_key)

def login_status(key):
    session = requests.Session()
    for i in range(50):
        try:
            rep = session.get(f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={key}', headers=UA_head)
            res = rep.json()
        except:
            time.sleep(3)
            continue
        if res['code'] != 0:
            xbmc.executebuiltin('Action(Back)')
            return
        if res["data"]["code"] == 0:
            # 存储 cookies
            dictc = req.utils.dict_from_cookiejar(rep.cookies)
            with open(os.path.join(ADDON_PATH, "resources", "config", "cookies"),"w") as f:
                json.dump(dictc, f, indent=4)
            # 存储 refresh_token
            with open(os.path.join(ADDON_PATH, "resources", "config", "refresh_token"),"w") as f:
                f.write(res["data"]["refresh_token"])
            xbmcgui.Dialog().ok('提示', '登录成功\n可以放心看b站了')
            xbmc.executebuiltin('Action(Back)')
            return
        elif res["data"]["code"] == 86090:
            xbmcgui.Dialog().ok("bro步骤错啦","bro想必你肯定是手滑了没点到确认")
            xbmc.executebuiltin('Action(Back)')
            return
        elif res["data"]['code'] == 86038:
            xbmcgui.Dialog().ok("bro步骤错啦","bro黄花菜都凉了才想起来吃：二维码过期了哇")
            xbmc.executebuiltin('Action(Back)')
            return
        time.sleep(3)
    xbmc.executebuiltin('Action(Back)')

def qrcode_create():
    qrcode_URL="https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    res=getback(qrcode_URL, UA_head)
    if res == False:
        xbmcgui.Dialog().ok("司马玩意出错了","一个亲切的问候！\n私人api又出问题了wwww\n速速查看xbmclog.txt!")
    else:
        qrcode_url=res["data"]["url"]
        qrcode_key=res["data"]["qrcode_key"]
        qrc = pyqrcode.create(qrcode_url+qrcode_key)
        if os.path.exists(os.path.join(ADDON_PATH, "resources", "config", "qrcode.png")):
            os.remove(os.path.join(ADDON_PATH, "resources", "config", "qrcode.png"))
        qrc.png(os.path.join(ADDON_PATH, "resources", "config", "qrcode.png"), scale=6)
        qrcode_img=os.path.join(ADDON_PATH, "resources", "config", "qrcode.png")
        xbmcplugin.setPluginCategory(HANDLE, '扫码阶段')
        # qrcode
        list_item=xbmcgui.ListItem("扫扫码")
        list_item.getVideoInfoTag().setPlot("该二维码仅180秒内有效！\n\n拿起你的手机！\n打开b站 -> 我的 -> 右上角扫码图标\n扫一扫我上面这个东西！\n之后手机在弹出的新界面中点击同意！\n\n上述所有操作完成之后，请点击下一步")
        list_item.setArt({'icon': qrcode_img})
        url=get_url(action="not")
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)
        # tips
        addXbmcItemInfo("Play版用户的提示","not","Play版本的用户（也就是白色版用户）的提示：\n疑似使用Play版的噼里啪啦在扫码后，如果已经授权之后就不能火速进行第二次授权\n如果第二次授权频繁，则在手机上会出现二维码过期的提示，点击下一步出现没扫码的神奇问题\n\n这是噼里啪啦特有的东西，我整不了\n（再这么下去我感觉Play版快要无了）",False)
        # i can!
        list_item=xbmcgui.ListItem("下一步")
        list_item.setArt({'icon': folder_icon})
        url=get_url(action="qrcode2", key=qrcode_key)
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
        
        xbmcplugin.endOfDirectory(HANDLE)

def qrcode3(rd):
    cd=rd["code"]
    # 未扫码
    if cd == 86101:
        os.remove(os.path.join(ADDON_PATH, 'resources', "config", 'cookie'))
        xbmcgui.Dialog().ok("bro步骤错啦","bro手机没掏出来忘记扫码了（没骂你是真的没扫）")
    # 过期
    elif cd == 86038:
        os.remove(os.path.join(ADDON_PATH, 'resources', "config", 'cookie'))
        xbmcgui.Dialog().ok("bro步骤错啦","bro黄花菜都凉了才想起来吃：二维码过期了哇")
    # 未确认
    elif cd == 86090:
        os.remove(os.path.join(ADDON_PATH, 'resources', "config", 'cookie'))
        xbmcgui.Dialog().ok("bro步骤错啦","bro想必你肯定是手滑了没点到确认")
    # 正常完成
    else:
        # write
        xbmcplugin.setPluginCategory(HANDLE, '恭喜！')
        addXbmcItemInfo("恭喜你登录了！","exit","你已经成功登陆了你的b站账号\ncookie数据已存放到你的本地目录！\n现在请你退回到Kodi主界面，重新打开该插件就能看噼里啪啦力！",False)
        xbmcplugin.endOfDirectory(HANDLE)

def qrcode2(key):
    url="https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key="+key
    try:
        ss=requests.Session()
        res=requests.get(url, headers=UA_head)
        res_text=res.text
    except requests.exceptions.RequestException as e:
        xbmc.log("无法从网上获取 json 数据")
        xbmcgui.Dialog().ok("司马玩意出错了","一个亲切的问候！\n私人api又出问题了wwww\n速速查看xbmclog.txt!")
    if check_json(res_text):
        log(res_text)
        res_text=json.loads(res_text)
        if res_text["code"] == 0:
            save_cookie(res)
            save_ref_token(res_text["data"]["refresh_token"])
            qrcode3(res_text["data"])
        else:
            xbmc.log("[Bilikodi] 数据返回了错误的代码: "+str(res_text["code"]))
            xbmc.log(res_text)
            xbmcgui.Dialog().ok("司马玩意出错了","一个亲切的问候！\n私人api又出问题了wwww\n速速查看xbmclog.txt!")
    else:
        xbmc.log("[Bilikodi] 无法解析 json 数据")
        xbmc.log(res_text)
        xbmcgui.Dialog().ok("司马玩意出错了","一个亲切的问候！\n私人api又出问题了wwww\n速速查看xbmclog.txt!")

def rt(p):
    params = dict(parse_qsl(p))
    if not params:
        log("登录")
        start()
    elif params["action"] == "qrcode":
        qrcode_create()
    elif params["action"] == "not":
        xbmcgui.Dialog().ok("????????","你点你m呢")
    elif params["action"] == "qrcode2":
        qrcode2(params["key"])
    elif params["action"] == "exit":
        sys.exit()
    else:
        raise ValueError(f'Invalid paramstring: {pars}!')
    