import json, os, requests, sys, time
from resources.lib.cookie import *
from urllib.parse import urlencode
import xbmcgui, xbmc, xbmcvfs, xbmcaddon, xbmcplugin

ADDON_name = "Bilikodi"
URL = sys.argv[0]
ADDON=xbmcaddon.Addon()
IMAGE_dir = os.path.join(ADDON_PATH, 'resources', 'images')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

def log(string):
    strings = "[plugin.video.bilikodi](info): "+str(string)
    xbmc.log(strings, xbmc.LOGINFO)

def check_json(jsondata):
    try:
        data = json.loads(jsondata)
        return True
    except:
        return False

def get_ua():
    UA_head = {
    'Referer': 'https://www.bilibili.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; PBAM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 EdgA/114.0.1823.74'
    }
    return UA_head

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(URL, urlencode(kwargs))

def unix2time(unix, fmat="%Y-%m-%d %H:%M:%S"):
    """
    Unix时间戳转人工可读时间
    
    :param unix: [num] 时间戳
    :param fmat: [str] 可自定义返回的格式信息，默认为 %Y-%m-%d %H:%M:%S
    :return: 返回人类可读时间格式
    :rtype: str
    """
    ltime=time.localtime(unix)
    return time.strftime(fmat, ltime)

def get_cid(bv):
    try:
        data=requests.get("https://api.bilibili.com/x/web-interface/view?bvid="+bv,headers=UA_head)
    except requests.exceptions.RequestException as e:
        data=""
        return False
    if check_json(data.text):
        res_text=json.loads(data.text)
        if res_text["code"] == 0:
            return res_text["data"]["cid"]
        else:
            return False
    else:
        return False

def get_img(key):
    img={
      'bilikodi': os.path.join(ADDON_PATH, "icon.png"),
      'fanart': os.path.join(ADDON_PATH, "fanart.png"),
      'folder': os.path.join(IMAGE_dir, "folder.png"),
      'user': os.path.join(IMAGE_dir, "user.png"),
      'video': os.path.join(IMAGE_dir, "video.png")
    }
    return img[key]

def getSetting(name):
    return xbmcplugin.getSetting(int(sys.argv[1]), name)

def warDialog(msg):
    xbmc.log("[plugin.video.bilikodi] [Err]: "+msg, xbmc.LOGERROR)
    xbmcgui.Dialog().notification(
        heading=ADDON_name,
        message=msg,
        time=3000
    )

def infoDialog(msg):
    xbmc.log("[plugin.video.bilikodi] [Info]: "+msg, xbmc.LOGINFO)
    xbmcgui.Dialog().notification(
        heading=ADDON_name,
        message=msg,
        time=2500
    )