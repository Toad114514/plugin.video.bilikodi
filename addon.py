import os, sys, requests, json, random, string
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
from urllib.parse import urlencode, parse_qsl
# wbikey
import resources.lib.wbi as wbi

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


#######
# Global function
#######
def warDialog(msg):
    xbmc.log("[plugin.video.bilikodi] [Err]: "+msg, xbmc.LOGERROR)
    xbmcgui.Dialog().notification(
        heading=ADDON_name,
        message=msg,
        time=3000
    )
    
def log(string):
    strings = "[plugin.video.bilikodi](info): "+string
    xbmc.log(strings, xbmc.LOGINFO)
    

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(URL, urlencode(kwargs))

def check_json(jsondata):
    try:
        data = json.loads(jsondata)
        return True
    except:
        return False

def getcookie():
    res = requests.session().post("https://www.bilibili.com", headers=UA_head)
    return res.cookies.get_dict()

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

def bvideoplay(bv):
    cid=get_cid(bv)
    if cid:
        # data=requests.get("https://api.bilibili.com/x/player/playurl?bvid="+bv+"&cid="+str(cid)+"&qn=16&fnval=16", headers=UA_head)
        data=requests.get("https://api.bilibili.com/x/player/playurl?bvid="+bv+"&cid="+str(cid)+"&qn=16&platform=html5", headers=UA_head)
        if check_json(data.text):
            res_text=json.loads(data.text)
            log(data.text)
            print(data.text)
            if res_text["code"] == 0:
                # url=res_text["data"]["dash"]["video"][0]["baseUrl"]
                url=res_text["data"]["durl"][0]["url"]
                # url=download_video(urlbase)
                play_item = xbmcgui.ListItem(offscreen=True)
                play_item.setPath(url)
                log("播放视频 "+url)
                xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)
            else:
                warDialog("数据返回了错误的代码: "+str(res_text["code"]))
        else:
            warDialog("无法解析 json 数据")
    else:
        warDialog("无法获取 cid")
######
# GetVideo_list
######

#########
# UserGet
#########

# getuser info
# params action="getuserinfo"&mid=mid

def getuserinfo(mid):
    try:
        f=open(os.path.join(ADDON_PATH, "resources", "config", "sub_list.json"),"r")
        sublist=f.read()
        f.close()
    except:
        sublist=False
    try:
        res=requests.get("https://api.bilibili.com/x/web-interface/card?mid="+mid, headers=UA_head)
        res_text=res.text
    except requests.exceptions.RequestException as e:
        res_text=""
        warDialog("无法从网上获取 json 数据")
    if check_json(res_text):
        xbmc.log(res_text, xbmc.LOGINFO)
        ups_data=json.loads(res_text)
        if ups_data["code"] == 0:
            xbmcplugin.setPluginCategory(HANDLE, ups_data["data"]["card"]["name"])
            # info
            upsinfo=ups_data["data"]["card"]["sign"]+"\n[COLOR=yellow]粉丝量："+str(ups_data["data"]["card"]["fans"])+"[/COLOR]"
            list_item=xbmcgui.ListItem(ups_data["data"]["card"]["name"])
            list_item.setArt({"icon": ups_data["data"]["card"]["face"]})
            list_item.getVideoInfoTag().setPlot(upsinfo)
            url=get_url(action=nothing)
            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)

            #### subscribe!!!!
            if sublist:
                sublist=json.loads(sublist)
                submids=[]
                for sub in sublist["sub"]:
                    submids.append(str(sub["mid"]))
                if str(mid) in submids:
                    # is_sub
                    list_item=xbmcgui.ListItem("取消关注")
                    list_item.getVideoInfoTag().setPlot("如题")
                    list_item.setArt({'icon': folder_icon})
                    url=get_url(action="unsub", mid=mid)
                    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
                else:
                    # is not sub
                    list_item=xbmcgui.ListItem("关注")
                    list_item.getVideoInfoTag().setPlot("如题")
                    list_item.setArt({'icon': folder_icon})
                    url=get_url(action="sub", mid=mid)
                    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
            else:
                # no sub_list.json them pass
                pass
            
            # videossssss
            list_item=xbmcgui.ListItem("投稿")
            list_item.getVideoInfoTag().setPlot("Up主的视频信息列表")
            list_item.setArt({'icon': folder_icon})
            url=get_url(action="dynamic_get", mid=mid, page=0)
            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
            
            # season
            list_item=xbmcgui.ListItem("合集视频")
            list_item.getVideoInfoTag().setPlot("Up主的合集视频")
            list_item.setArt({'icon': folder_icon})
            url=get_url(action="season", mid=mid)
            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
            xbmcplugin.endOfDirectory(HANDLE)
        elif ups_data["code"] == -404:
            warDialog("没找到"+mid+"对应的up主")
        else:
            warDialog("数据返回了错误的代码: "+str(res_json["code"]))
    else:
        warDialog("无法解析 json 数据")
        log(res_text)


def unsub(mid):
    # load sub_list.json
    log("params-mid"+mid)
    with open(os.path.join(ADDON_PATH, "resources", "config", "sub_list.json"),"r") as f:
        f_text=f.read()
    sublist=json.loads(f_text)
    # for
    for i in range(len(sublist["sub"])):
        log(sublist["sub"][i]["mid"])
        if sublist["sub"][i]["mid"] == mid:
            sublist["sub"].pop(i)
            log("del done")
            os.remove(os.path.join(ADDON_PATH, "resources", "config", mid+".jpg"))
            break
        else:
            pass
    # rewrite
    with open(os.path.join(ADDON_PATH, "resources", "config", "sub_list.json"),"w") as f:
        f.write(json.dumps(sublist))
    xbmcgui.Dialog().ok(ADDON_name,"已取消关注该Up主")
    
def sub(mid):
    # get sub_list.json
    with open(os.path.join(ADDON_PATH, "resources", "config", "sub_list.json"),"r") as f:
        f_text=f.read()
    sublist=json.loads(f_text)
    try:
        # get biliapi json
        res=requests.get("https://api.bilibili.com/x/web-interface/card?mid="+mid, headers=UA_head)
    # if err in gets
    except requests.exceptions.RequestException as e:
        res_text=""
        warDialog("无法从网上获取 json 数据")
    # loads res_text to dict
    get=json.loads(res.text)
    # download ups img
    face_path = os.path.join(ADDON_PATH, "resources", "config", "face")
    with open(os.path.join(face_path, str(mid)+".jpg"),"wb") as face_file:
        # get ups face file
        res=requests.get(get["data"]["card"]["face"])
        # write img binary in file [mid].jpg
        face_file.write(res.content)
    # create a dict about ups info
    sub_info={'mid': mid,'name': get["data"]["card"]["name"], 'face': str(mid)+'.jpg','desc': get["data"]["card"]["sign"], 'fans': get["data"]["card"]["fans"]}
    # add them in sublist
    sublist["sub"].append(sub_info)
    # rewrite to sub_list.json
    with open(os.path.join(ADDON_PATH, "resources", "config", "sub_list.json"),"w") as f:
        f.write(json.dumps(sublist))
    xbmcgui.Dialog().ok(ADDON_name,"已关注该Up主\n请退出重进本列表")

# getuserdynamic
# Get Error -799(请求频繁)
def getuserdynamic(mid,page):
    try:
        res=requests.get("https://api.bilibili.com/x/space/arc/search?mid="+mid, headers=UA_head)
        res_text=res.text
    except requests.exceptions.RequestException as e:
        res_text=""
        warDialog("无法从网上获取 json 数据")
    if check_json(res_text):
        log(res_text)
        res_text=json.loads(res_text)
        if res_text["code"] == 0:
            xbmcplugin.setPluginCategory(HANDLE, "投稿")
            for video in res_text["data"]["list"]["vlist"]:
                list_item = xbmcgui.ListItem(video["title"])
                url = get_url(action='play_video', bv=video["bvid"])
                list_item.getVideoInfoTag().setPlot(video['description'])
                list_item.setArt({'icon': video["pic"], 'fanart': video["pic"]})
                list_item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)
            # nextpage
            list_item = xbmcgui.ListItem("下一页")
            url=get_url(action="dynamic_get", mid=mid, page=page+1)
            list_item.getVideoInfoTag().setPlot("下一页")
            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
            xbmcplugin.endOfDirectory(HANDLE)
        else:
            warDialog("数据返回了错误的代码: "+str(res_text["code"]))
    else:
        warDialog("无法解析 json 数据")
        log(res_text)
        
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
###########
# series and archive
###########

def season_list(mid):
    headers=UA_head
    headers["referer"]=".bilibili.com"
    query=wbi.getwbikey({
      'mid': mid,
      'page_num': 1,
      'page_size': 20
    })
    try:
        # res=requests.get("https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid="+mid+"&page_num=1&page_size=20&w_rid=03b4190fbc78ab21a46bade3e32a5064&wts=1706173818", headers=UA_head)
        res=requests.get("https://api.bilibili.com/x/polymer/web-space/seasons_series_list?"+query, headers=headers)
        res_text=res.text
    except requests.exceptions.RequestException as e:
        res_text=""
        warDialog("无法从网上获取 json 数据")
    if check_json(res_text):
        res_json=json.loads(res_text)
        if res_json["code"] == 0:
            xbmcplugin.setPluginCategory(HANDLE, '合集')
            if len(res_json["data"]["items_lists"]["season_list"]) > 0:
                for season in res_json["data"]["items_lists"]["season_list"]:
                    list_item = xbmcgui.ListItem(season["meta"]["name"])
                    url = get_url(action='season', id=str(season["meta"]["season_id"]))
                    plot=series["meta"]["description"]
                    list_item.getVideoInfoTag().setPlot(plot)
                    list_item.getVideoInfoTag().setPlot(plot)
                    list_item.setArt({'icon': series["meta"]["cover"], 'fanart': series["meta"]["cover"]})
                    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
                xbmcplugin.endOfDirectory(HANDLE)
            else:
                warDialog("这里连吊都没有")
        else:
            warDialog("数据返回了错误的代码: "+str(res_json["code"]))
            log(res_text)
    else:
        warDialog("无法解析 json 数据")
        log(res_text)
#######
# MenuList
#######
def addXbmcItem(label,param,is_folder):
    list_item = xbmcgui.ListItem(label)
    info_tag = list_item.getVideoInfoTag()
    info_tag.setMediaType('video')
    info_tag.setTitle(label)
    list_item.setArt({'icon': folder_icon, 'fanart': fanart_bg})
    url=get_url(action=param)
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

def addXbmcItemInfo(label,param,info,is_folder):
    list_item = xbmcgui.ListItem(label)
    info_tag = list_item.getVideoInfoTag()
    info_tag.setMediaType('video')
    info_tag.setTitle(label)
    info_tag.setPlot(info)
    list_item.setArt({'icon': folder_icon, 'fanart': fanart_bg})
    url=get_url(action=param)
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

def mainmenu():
    if os.path.exists(os.path.join(ADDON_TempDir, "temp_video")) == False:
        os.mkdir(ADDON_TempDir)
        os.mkdir(os.path.join(ADDON_TempDir, "temp_video"))
    xbmcplugin.setPluginCategory(HANDLE, '快乐老家')
    xbmcplugin.setContent(HANDLE, 'folder')
    # home tuijian
    addXbmcItemInfo("推荐视频","home","b站的主页视频推荐\n仅能获取30条视频推荐\n过段时间会自动刷新",True)
    addXbmcItem("前 100","top100",True)
    addXbmcItemInfo("搜索","search","这个还没完善你先死一边去",True)
    addXbmcItemInfo("本地关注列表","sublist","该功能灵感来自PipePipe\n数据文件存放于本插件根目录/resources/config/sub_list.json",True)
    addXbmcItem("跳转到...","tp",True)
    addXbmcItem("帮助","helper",True)
    addXbmcItemInfo("wbikey","wbikey","Debug Option",True)
    xbmcplugin.endOfDirectory(HANDLE)

def gethomevideo():
    try:
        res=requests.get("https://api.bilibili.com/x/web-interface/index/top/feed/rcmd", headers=UA_head)
        res_text=res.text
    except requests.exceptions.RequestException as e:
        res_text=""
        warDialog("无法从网上获取 json 数据")
    if check_json(res_text):
        res_json=json.loads(res_text)
        if res_json["code"] == 0:
            if len(res_json["data"]["item"]) > 0:
                xbmcplugin.setPluginCategory(HANDLE, '主页推荐')
                for video in res_json["data"]["item"]:
                    list_item = xbmcgui.ListItem(video["title"])
                    url = get_url(action='play_video', bv=video["bvid"], cid=video["cid"])
                    view="[COLOR=blue]"+str(video["stat"]["view"])+"[/COLOR]"
                    like="[COLOR=red]"+str(video["stat"]["like"])+"[/COLOR]"
                    owner="[COLOR=green]"+video["owner"]["name"]+"[/COLOR][COLOR=yellow] ("+str(video["owner"]["mid"])+")[/COLOR]"
                    plot=video["title"]+"\n播放量 "+view+"\n点赞量 "+like+"\nUp主 "+owner
                    list_item.getVideoInfoTag().setTitle(video['title'])
                    list_item.getVideoInfoTag().setDuration(video['duration'])
                    list_item.getVideoInfoTag().setWriters([video["owner"]["name"]])
                    list_item.getVideoInfoTag().setPlot(plot)
                    list_item.setArt({'icon': video["pic"], 'fanart': video["pic"]})
                    list_item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, False)
                xbmcplugin.endOfDirectory(HANDLE)
            else:
                warDialog("这里连吊都没有")
        else:
            warDialog("数据返回了错误的代码: "+str(res_json["code"]))
    else:
        warDialog("无法解析 json 数据")
        log(res_text)

# local subscribe list
def getsublist():
    try:
        f=open(os.path.join(ADDON_PATH, "resources", "config", "sub_list.json"),"r")
        res_text=f.read()
        f.close()
    except IOError as e:
        warDialog("找不到 sub_list.json")
    if check_json(res_text):
        sublist=json.loads(res_text)
        xbmcplugin.setPluginCategory(HANDLE, '本地关注')
        for sub in sublist["sub"]:
            face_path=os.path.join(ADDON_PATH,"resources","config","face",str(sub["mid"])+".jpg")
            # info
            upsinfo=sub["desc"]+"\n[COLOR=yellow]粉丝量："+str(sub["fans"])+"[/COLOR]"
            list_item=xbmcgui.ListItem(sub["name"])
            list_item.setArt({"icon": face_path})
            list_item.getVideoInfoTag().setPlot(upsinfo)
            url=get_url(action="getuserinfo", mid=sub["mid"])
            xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)
        xbmcplugin.endOfDirectory(HANDLE)
    else:
        warDialog("非正规json数据")

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
                res=requests.get("https://api.bilibili.com/x/web-interface/search/all/v2?keyword="+keyword, headers=UA_head)
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

def nothing():
    xbmcgui.Dialog().notification(ADDON_name,"该项里面啥也没有别找了（仅展示作用）")

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
        log("获取主页推荐视频")
        gethomevideo()
    elif params["action"] == "play_video":
        log("准备播放")
        log("参数传入: "+params["bv"])
        bvideoplay(params["bv"])
    elif params["action"] == "search":
        search()
    elif params["action"] == "helper":
        helper()
    elif params["action"] == "nothing":
        nothing()
    elif params["action"] == "wbikey":
        wbikeys()
    # user
    elif params["action"] == "dynamic_get":
        getuserdynamic(params["mid"], params["page"])
    elif params["action"] == "getuserinfo":
        getuserinfo(params["mid"])
    elif params["action"] == "sublist":
        getsublist()
    elif params["action"] == "sub":
        sub(params["mid"])
    elif params["action"] == "unsub":
        unsub(params["mid"])
    elif params["action"] == "season":
        season_list(params["mid"])
    # Tp_list
    elif params["action"] == "tp":
        tp_list()
    elif params["action"] == "tp_user":
        tp_user_get()
    else:
        raise ValueError(f'Invalid paramstring: {pars}!')

######
# loop
######
if __name__ == '__main__':
    log("正在运行 Bilikodi... (v1.01)")
    router(sys.argv[2][1:]) 
    