import os, sys, requests, json, random, string
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
from xbmcswift2 import Plugin
from urllib.parse import urlencode, parse_qsl

from resources.lib.cookie import *
from resources.lib.get import *
from resources.lib.core import *
from resources.lib.xbmc import *
from resources.lib.wbi import *

URL = sys.argv[0]
HANDLE = int(sys.argv[1])

# addon info
ADDON=xbmcaddon.Addon()
ADDON_name="bilikodi"
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
ADDON_icon=ADDON.getAddonInfo('icon')
ADDON_version = ADDON.getAddonInfo('version')
ADDON_TempDir = os.path.join(xbmcvfs.translatePath('special://home/temp'), ADDON.getAddonInfo('id'), '')

# Dirs
IMAGE_dir = os.path.join(ADDON_PATH, 'resources', 'images')
# good folder
fanart_bg = os.path.join(ADDON_PATH, "fanart.png")
folder_icon = os.path.join(IMAGE_dir, "folder.png")

plugin = Plugin()

def report_history(bvid, cid):
    params={
       'bvid': bvid,
       'cid': cid,
       'csrf': read_cookie("bili_jct")
    }
    res=requests.post("https://api.bilibili.com/x/click-interface/web/heartbeat", data=params, headers=UA_head, cookies=load_cookie())

def bvstartp(bv, qn=getSetting("qn")):
    cid=get_cid(bv)
    if cid:
        # Requests
        try:
            params = getwbip(bvid=bv, cid=cid, qn=qn, fnval=1, platform="html5")
            res=requests.get(f"https://api.bilibili.com/x/player/wbi/playurl?{params}", headers=UA_head, cookies=load_cookie()).json()
        except:
            warDialog("网络错误")
            return
        # Code
        if res["code"] == -400:
            warDialog("请求错误")
            return
        elif res["code"] != 0:
            warDialog(str(res["code"])+": 未知错误")
            return
        try:
            # wbi 验证
            # 抛出错误 KeyError 才能保证该字段不存在
            # 这样wbi验证也会通过
            voucher=res["data"]["v_voucher"]
        except KeyError:
            # 寻找流并播放
            media=res["data"]["durl"][0]["url"]
            media=media.encode('latin-1').decode('unicode_escape')
            report_history(bv, cid)
            xbmcgui.Dialog().ok("Url", media)
            play_item = xbmcgui.ListItem(offscreen=True)
            play_item.setPath(media)
            xbmcplugin.setResolvedUrl(HANDLE, True, play_item)
            # plugin.set_resolved_url(media)
            return
        warDialog("wbi 签名失败")
        return

def videoplay_list(icon, t, bv):
    xbmcplugin.setPluginCategory(HANDLE, "播放")
    listm=[
      {
        'name': '[COLOR=yellow][720P][/COLOR] '+t,
        'url': get_url(action="bvplayR", bv=bv, qn="64"),
        'icon': icon
      },
      {
        'name': '[COLOR=yellow][480P][/COLOR] '+t,
        'url': get_url(action="bvplayR", bv=bv, qn="32"),
        'icon': icon
      },
      {
        'name': '[COLOR=yellow][320P][/COLOR] '+t,
        'url': get_url(action="bvplayR", bv=bv, qn="16"),
        'icon': icon
      },
      {
        'name': '[COLOR=yellow][240P][/COLOR] '+t,
        'url': get_url(action="bvplayR", bv=bv, qn="6"),
        'icon': icon
      },
      {
        'name': '[COLOR=yellow][Default byset][/COLOR] '+t,
        'url': get_url(action="bvplay", bv=bv),
        'icon': icon
      }
    ]
    for x in listm:
        addXbmcItemCustom(
            x["name"],
            x["url"],
            "",
            False,
            icon=x["icon"],
            fanart=x["icon"],
            is_media=True
        )
    xbmcplugin.endOfDirectory(HANDLE)

def orig_play(bvid):
    li = xbmcgui.ListItem("[COLOR=grey]直接调用旧定义的播放函数播放[/COLOR]")
    url = get_url(action='play_video', bv=bvid)
    li.getVideoInfoTag().setPlot("Refer play video by bvideoplay() from addon.py. And get back video by 480p.")
    li.setArt({'icon': folder_icon})
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(HANDLE, url, li, False)

def play_menu(video):
    xbmcplugin.setPluginCategory(HANDLE, "bro的稿件信息")
    # infolab
    time="[COLOR=grey]"+str(video["pubdate"])+"[/COLOR]"
    list_item = xbmcgui.ListItem("[Pub "+time+"] "+video["title"])
    view="[COLOR=blue]"+str(video["stat"]["view"])+"[/COLOR]"
    like="[COLOR=red]"+str(video["stat"]["like"])+"[/COLOR]"
    coin="[COLOR=yellow]"+str(video["stat"]["coin"])+"[/COLOR]"
    sc="[COLOR=green]"+str(video["stat"]["favorite"])+"[/COLOR]"
    plot="播放量 "+view+"\n"+like+" 赞 "+coin+" 投币 "+sc+" 收藏\nby"+video["owner"]["name"]+" [mid:"+str(video["owner"]["mid"])+"]"
    plot+="\n\n[COLOR=grey]aid: "+str(video["aid"])+"\ncid: "+str(video["cid"])+"[/COLOR]"
    plot+="\n\n"+video["desc"]
    list_item.getVideoInfoTag().setDuration(video['duration'])
    list_item.getVideoInfoTag().setWriters([video["owner"]["name"]])
    list_item.getVideoInfoTag().setPlot(plot)
    list_item.setArt({'icon': video["pic"], 'fanart': video["pic"]})
    url=get_url(action="not")
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)
    # Ups
    ups="视频投稿 by"+video["owner"]["name"]+"\nmid: "+str(video["owner"]["mid"])
    ups+="\n点击进入其Up主页查看（未完善）"
    li = xbmcgui.ListItem("Up主")
    li.getVideoInfoTag().setPlot(ups)
    li.setArt({'icon': video["owner"]["face"]})
    xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
    # State
    stt=video["stat"]
    state="播放量 "+str(stt["view"])+"\n点赞量 "+str(stt["like"])+"\n投币 "+str(stt["coin"])+"\n收藏 "+str(stt["favorite"])+"\n分享 "+str(stt["share"])+"\n弹幕数量 "+str(stt["danmaku"])+"\n评论 "+str(stt["reply"])
    addXbmcItemInfo("投稿 Stat 状态","not",state,False)
    # Rights
    rights=video["rights"]
    rtext="该投稿具有以下属性：\n"
    if rights["download"] == 1:
        rtext+="可允许下载的稿件\n"
    elif rights["ugc_pay"] == 1:
        rtext+="UGC 付费内容\n"
    elif rights["is_cooperation"] == 1:
        rtext+="联合投稿\n"
    elif rights["is_360"] == 1:
        rtext+="360 度全景视频\n"
    elif rights["no_reprint"] == 1:
        rtext+="禁止转载\n"
    rtext+="实际该投稿特性可能不止这些。"
    addXbmcItemInfo("投稿属性","nothing",rtext,False)
    # playby
    addXbmcItemCustom(
        "播放",
        get_url(action="videoplaylist", icon=video["pic"], title=video["title"], bv=video["bvid"]),
        "选择一种方案播放",
        True,
        get_img("video")
    )
    # other
    addXbmcItemInfo("稿件操作(未完成)","nothing","Debug Option.",False)
    addXbmcItemInfo("评论区","nothing","Debug Option.",False)
    
    xbmcplugin.endOfDirectory(HANDLE)

def play_info(vid,num):
    if num == 0: # in bvid params
       param="bvid="+vid
    elif num == 1: # in aid params
       param="aid="+str(vid)
    url="https://api.bilibili.com/x/web-interface/view?"+param
    # xbmcgui.Dialog().ok("URL 信息", url)
    # get
    try:
        res=getback_c(url, get_ua(), load_cookie())
        if res == False:
            return
    except requests.exceptions.RequestException as e:
        warDialog("扫码网络。")
    else:
        rest=res
        # code
        cd = rest["code"]
        match cd:
            case -400:
                warDialog("错误参数请求")
            case -403:
                warDialog("你没有权限访问")
            case -404:
                warDialog("666是404 not found!!!")
            case 62002:
                warDialog("隐藏的稿件")
            case 62004:
                warDialog("稿件审核中ing...")
            case 62012:
                warDialog("UP主私藏稿件不分享")
            case 0:
                play_menu(rest["data"])
            case _:
                warDialog("未知错误")
    