###############################
#          Bilikodi addon.py
#     插件入口，包含一个比较完整的路由框架
###############################

import os, sys, requests, json, random, string
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
from urllib.parse import urlencode, parse_qsl
# wbikey
import resources.lib.wbi as wbi
import resources.login as login
# xbmc
from resources.lib.xbmc import *
from resources.lib.cookie import *
from resources.lib.player import *
from resources.lib.core import *
from resources.lib.up import *
from resources.lib.action import *
#version
version="v1.0.41"
dev=True

# urls
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

UA_head = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; PBAM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36 EdgA/114.0.1823.74'
}
# UA_head["referer"] = "www.bilibili.com"
#apiurl="https://api.bilibili.com/x/web-interface/"

######$$$$$######
#   Fuck this!
#################
# 以前写的代码还是太石了
# 这一堆石山代码我肯定要k飞的
# 后面找时间重构部分函数
#      toadXtech64 08.01 正好兄弟生日
#################

# 提醒我 上下文菜单 更新条目用 Container.Update()

#######
# Global function
#######
    
def log(string):
    strings = "[plugin.video.bilikodi](info): "+string
    xbmc.log(strings, xbmc.LOGINFO)

def getcookie():
    res = requests.session().post("https://www.bilibili.com", headers=UA_head)
    return res.cookies.get_dict()

########
# Tplist
########

def tp_list():
    xbmcplugin.setPluginCategory(HANDLE, '跳转到...')
    # home tuijian
    addXbmcItem("用户","tp_user",True)
    xbmcplugin.endOfDirectory(HANDLE)

def tp_user_get():
    keyboard=xbmc.Keyboard()
    keyboard.setHeading("输入该up主的uid...")
    keyboard.doModal()
    if keyboard.isConfirmed():
        keyword = keyboard.getText()
        if len(keyword) < 1:
            msgbox = xbmcgui.Dialog().ok(ADDON_name, '您还没输入uid')
        elif len(keyword) > 0:
            getuserinfo(keyword)
    else:
        keyword = ""
#######
# MenuList
#######

def mainmenu():
    if os.path.exists(os.path.join(ADDON_TempDir, "temp_video")) == False:
        os.mkdir(ADDON_TempDir)
        os.mkdir(os.path.join(ADDON_TempDir, "temp_video"))
    if dev:
        xbmcplugin.setPluginCategory(HANDLE, '[InWIP]主页')
    else:
        xbmcplugin.setPluginCategory(HANDLE, '主页')
    xbmcplugin.setContent(HANDLE, 'folder')
    # home tuijian
    addXbmcItemCustom("推荐视频",get_url(action="home", pn=1),"b站的主页视频推荐",True)
    addXbmcItem("前 100","top100",True)
    addXbmcItemCustom(
        "关注列表",
        get_url(action="ups_sub", mid=get_mid()),
        "你最喜欢的关注的佬",
        True,
        icon=get_img("user")
    )
    addXbmcItemCustom("自己的用户信息",get_url(action="ups_me"),"看看你自己",True,icon=get_img("user"))
    addXbmcItemCustom("个人收藏夹",get_url(action="ups_fav", mid=get_mid()),"bro你喜欢的都在这了",True)
    # addXbmcItemInfo("搜索","search","这个还没完善你先死一边去",True)
    addXbmcItem("跳转到...","tp",True)
    addXbmcItem("帮助","helper",True)
    
    """
    Development Menu Items
    """
    if dev:
        addXbmcItemCustom(
            "特别警告！！",
            get_url(action="dev"),
            "特别警告，长按测试上下文菜单",
            True,
            context=[
             ("Hello", "RunPlugin(plugin://plugin.video.bilikodi/?action=dev)"),
             ("Me too", "RunPlugin(plugin://plugin.video.bilikodi/?action=helper)")
            ]
        )
        addXbmcItemInfo("新版播放详情框架","player_test","Debug Option.\nThe new video info to show in development state.[WIP]",True)
        addXbmcItemInfo("like","like_test","r",True)
        addXbmcItemInfo("wbikey","wbikey","Debug Option",True)
        addXbmcItemInfo("立即申请刷新 cookie 测试","ref_cookie","Debug Option",True)
    xbmcplugin.endOfDirectory(HANDLE)

def gethomevideo(pn=1):
    res=getbackAuto("https://api.bilibili.com/x/web-interface/index/top/feed/rcmd?fresh_idx="+str(pn))
    if res != False:
        xbmcplugin.setPluginCategory(HANDLE, '主页推荐')
        for video in res["data"]["item"]:
            # 描述
            url = get_url(action='bvplay', bv=video["bvid"])
            view="[COLOR=blue]"+str(video["stat"]["view"])+"[/COLOR]"
            like="[COLOR=red]"+str(video["stat"]["like"])+"[/COLOR]"
            owner="[COLOR=green]"+video["owner"]["name"]+"[/COLOR][COLOR=yellow] ("+str(video["owner"]["mid"])+")[/COLOR]"
            plot=video["title"]+"\n\n播放量 "+view+"\n点赞量 "+like+"\nUp主 "+owner
            plot+="\n\n长按进行其他操作"
            # 提供上下文
            bv=video["bvid"]
            mid=video["owner"]["mid"]
            # 内容
            addXbmcItemCustom(
                video["title"],
                get_url(action='bvplay', bv=bv),
                plot,
                False,
                icon=video["pic"],
                fanart=video["pic"],
                is_media=True,
                context=[
                  ("查看详细信息", f"Container.Update(plugin://plugin.video.bilikodi/?action=player&bv={bv})"),
                  ("跳转至UP主", f"Container.Update(plugin://plugin.video.bilikodi/?action=ups_info&mid={mid})")
                  ]
                )
        # Next Pages
        addXbmcItemCustom(
          "[COLOR=yellow]下一页[/COLOR]",
          get_url(action="home", pn=int(pn)+1),
          "如题",
          True
        )
        xbmcplugin.endOfDirectory(HANDLE)

def search():
    keyboard=xbmc.Keyboard()
    keyboard.setHeading("搜索...")
    keyboard.doModal()
    # xbmc.sleep(1500)
    if keyboard.isConfirmed():
        keyword = keyboard.getText()
        if len(keyword) < 1:
            msgbox = xbmcgui.Dialog().ok(ADDON_name, '您必须输入关键词才可以搜索相关内容')
        elif len(keyword) > 0:
            cookies=getcookie()
            try:
                res=requests.get("https://api.bilibili.com/x/web-interface/search/all/v2?keyword="+keyword, headers=UA_head, cookies=get_cookie())
                res_text=res.text
            except requests.exceptions.RequestException as e:
                res_text=""
                warDialog("无法从网上获取数据")
            if check_json(res_text):
                search_data=json.loads(res_text)
                if search_data["code"] == 0:
                    if len(search_data["data"]["result"][11]["data"]) > 0:
                        for video in res_text["data"]["result"][11]["data"]:
                            list_item = xbmcgui.ListItem(video["title"])
                            url = get_url(action='play_video', bv=video["bvid"])
                            list_item.setArt({'icon': video["pic"]})
                            list_item.setProperty('IsPlayable', 'true')
                            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)
                        xbmcplugin.endOfDirectory(HANDLE)
                    else:
                        list_item=xbmcgui.ListItem("你这搜的什么√8关键词我是连灰都找不到")
                        url=get_url(action="nothing")
                        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)
                        xbmcplugin.endOfDirectory(HANDLE)
                else:
                    warDialog("数据返回了错误代码"+str(res_text["code"]))
            else:
                warDialog("无法解析 Json 数据")
    else:
        keyword = ""

def wbikeys():
    query = wbi.getwbikey(
      params={
        'acrion': 'good',
        'mid': 1257,
        'page': 'one'
      }
    )
    xbmcgui.Dialog().ok(ADDON_name, query)

def helper():
    helper_text="Bilikodi Helper\n"
    helper_text+="一个基于bilibili-api的b站kodi客户端\n"
    helper_text+="通过文件夹提示去选择对应的选项\n"
    helper_text+="在上面观看你所要看的视频\n"
    helper_text+="搜索中文时请确保安装了中文输入法\n"
    xbmcgui.Dialog().ok(ADDON_name+" 帮助", helper_text)

def warning_dev():
    helper_text="警告！！\n"
    helper_text+="您正在使用 Dev 分支的 Bilikodi!!!!\n"
    helper_text+="使用 Dev 版本可以获得更多的新功能\n但可能出现一大堆bug!\n使用 Dev 分支的 bilikodi 造成的后果本人均不负责!!\n"
    xbmcgui.Dialog().ok(ADDON_name+" Warning!", helper_text)

def nothing():
    xbmcgui.Dialog().notification(ADDON_name,"无内容弹窗。")

# def clean():
    # if xbmcvfs.exists(ADDON_TempDir):
        # if xbmcvfs.rmdir(ADDON_TempDir, True):
            # xbmcgui.Dialog().notification(ADDON_name, message="清理成功", time=3000)
        # else:
            # warDialog("清理失败")
    # else:
        # xbmcgui.Dialog().notification(ADDON_name, message="无需清理", time=3000)
######
# Router
######

def router(pars):
    params = dict(parse_qsl(pars))
    if not params:
        log("主页")
        mainmenu()
    elif params["action"] == "home":
        log("获取主页推荐视频, 页码"+str(params["pn"]))
        gethomevideo(pn=params["pn"])
    # players 播放器
    elif params["action"] == "player":
        play_info(params["bv"], 0)
    elif params["action"] == "videoplaylist":
        videoplay_list(params["icon"], params["title"], params["bv"])
    elif params["action"] == "bvplayR":
        log("播放...（指定分辨率）")
        bvstartp(params["bv"], qn=params["qn"])
    elif params["action"] == "bvplay":
        log("播放（默认分辨率）.....")
        bvstartp(params["bv"])
    # 其他杂项
    elif params["action"] == "helper":
        helper()
    elif params["action"] == "nothing":
        nothing()
    elif params["action"] == "wbikey":
        wbikeys()
    # login
    elif params["action"] == "qrcode":
        login.qrcode_get()
    ## 用户
    # user
    elif params["action"] == "ups_me":
        up_info(get_mid())
    elif params["action"] == "ups_info":
        up_info(params["mid"])
    elif params["action"] == "ups_sub":
        up_sub(params["mid"])
    elif params["action"] == "ups_send":
        up_video(params["mid"], pn=params["pn"])
    elif params["action"] == "ups_fav":
        up_fav(params["mid"])
    elif params["action"] == "ups_fav_2nd":
        up_fav_2nd(params["fid"], params["p"])
    # Tp_list
    elif params["action"] == "tp":
        tp_list()
    elif params["action"] == "tp_user":
        tp_user_get()
    # warning
    elif params["action"] == "dev":
        warning_dev()
    elif params["action"] == "not":
        nothing()
    # dev
    elif params["action"] == "ref_cookie":
        cookie_ref(True)
    elif params["action"] == "player_test":
        play_info("BV1k7JazfEV2", 0) # 睡前必看，来自星野大叔的睡前问候
        #play_info(113961538292695, 1) # linux大战比尔·盖茨 (2009年) (by aid number.)
    elif params["action"] == "like_test":
        # 这里个人测试出现 -403 账号异常，有谁能帮忙测试一下口牙
        # cookies buvid3和csrf检测看了也没有问题
        like_action("BV1mmbgzwEEU") # 纸片马力欧的神人视频 别点开看！
    else:
        raise ValueError(f'Invalid paramstring: {pars}!')

######
# loop
######
log("===========================")
log("Bilikodi ("+version+") Route 路由框架重定向...")
log(str(sys.argv[2][1:]))
log("===========================")
if __name__ == '__main__':
    if login.check_login() == False:
        xbmcgui.Dialog().ok("登录", "未检测到Cookies，需登录您的b站账号才能使用\n请转到插件设置选择一个方式登录\n（只是为了API稳定返回数据而已）")
        # 仅允许通过 by qrcode
        if sys.argv[2][1:] == "action=qrcode":
            router(sys.argv[2][1:])
            sys.exit()
        else:
            sys.exit()
    router(sys.argv[2][1:])
    log(sys.argv[2][1:])
    