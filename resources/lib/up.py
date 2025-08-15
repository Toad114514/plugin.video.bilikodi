import requests, os, sys, time
import xbmc, xbmcgui, xbmcvfs, xbmcplugin

from resources.lib.xbmc import *
from resources.lib.core import *
from resources.lib.cookie import *
from resources.lib.get import *
from resources.lib.wbi import *

"""
投稿明细
"""
def up_video(mid, pn=1, ps=20):
    mid=str(mid)
    params=getwbip(mid=mid, pubdate="pubdate", pn=pn, ps=ps)
    res=getbackAuto(f"https://api.bilibili.com/x/space/wbi/arc/search?{params}")
    if res == False or "v_voucher" in res["data"]:
        return
    # 解析
    xbmcplugin.setPluginCategory(HANDLE, "视频投稿")
    for x in res["data"]["list"]["vlist"]:
        # 部分投稿可能是联合创作视频，所以此处mid直接从数据中提取
        plot="作者: "+x["author"]+"[COLOR=grey]("+str(x["mid"])+")[/COLOR]"
        plot+="\n投稿时间: "+unix2time(x["created"])
        plot+="\n[COLOR=blue]"+str(x["play"])+" 次播放[/COLOR]      "
        plot+="[COLOR=red]"+str(x["comment"])+" 评论[/COLOR]\n\n"
        plot+=x["description"]
        addXbmcItemCustom(
            x["title"],
            get_url(action="bvplay", bv=x["bvid"]),
            plot,
            False,
            icon=x["pic"],
            fanart=x["pic"],
            is_media=True
        )
    # 检测是否到底
    pages=int(res["data"]["page"]["count"] / ps)
    # 余数多一页显示
    if res["data"]["page"]["count"] % ps != 0:
        pages+=1
    if pages > int(pn):
        log("pages <= int(pn)")
        i={'name': "[COLOR=yellow]下一页[/COLOR] ("+str(pn)+"/"+str(pages)+" 每页"+str(ps)+"项)", 'url': get_url(action="ups_send", mid=mid, pn=int(pn)+1)}
    else:
        i={'name': "[COLOR=grey]页面最底处[/COLOR] ("+str(pages)+"/"+str(pn)+" 每页"+str(ps)+"项)", 'url': get_url(action="not")}
    addXbmcItemCustom(
        i["name"],
        i["url"],
        "跳到下一页使的，或者可能你到底了",
        True
    )
    xbmcplugin.endOfDirectory(HANDLE)
 
"""
UpInfo
"""
def up_info(mid):
    mid=str(mid)
    # res up主基础状态
    res=getbackAuto(f"https://api.bilibili.com/x/relation/stat?vmid={mid}")
    # res2 用户详情 bywbi key
    params=getwbip(mid=mid)
    res2=getbackAuto(f"https://api.bilibili.com/x/space/wbi/acc/info?{params}")
    # 两请求任意一个回 False 或 "v_voucher" key 存在则k飞
    if res == False or res2 == False or "v_voucher" in res2["data"]:
        return
    # 初始化数据
    res=res["data"]
    res2=res2["data"]
    follow=str(res["following"])
    fan=str(res["follower"])
    xbmcplugin.setPluginCategory(HANDLE, "用户 & Up主")
    ## Ups状态
    plot=res2["sign"]
    plot+="\n\n[COLOR=grey]UID: "+mid
    plot+="\n[COLOR=pink]"+fan+" 粉     "+follow+" 关注[/COLOR]"
    # 等级
    match res2["level"]:
        case 0:
            head="[COLOR=grey]"
        case 1:
            head="[COLOR=grey]"
        case 2:
            head="[COLOR=green]"
        case 3:
            head="[COLOR=blue]"
        case 4:
            head="[COLOR=yellow]"
        case 5:
            head="[COLOR=orange]"
        case 6:
            head="[COLOR=red]"
    plot+="\n"+head+"LV"+str(res2["level"])+"[/COLOR]"
    if res2["is_followed"] == True:
        plot+="\n[COLOR=yellow]已关注[/COLOR]"
    addXbmcItemCustom(
        res2["name"],
        get_url(action="nothing"),
        plot,
        False,
        icon=res2["face"]
    )
    
    ## Others
    items=[
      {'name': '投稿视频', 'params': get_url(action="ups_send", mid=mid, pn=1)},
      {'name': '用户收藏', 'params': get_url(action="ups_fav", mid=mid)},
      {'name': '关注列表', 'params': get_url(action="ups_sub", mid=mid)}
    ]
    for x in items:
        addXbmcItemCustom(
          x["name"],
          x["params"],
          x["name"],
          True
        )
    xbmcplugin.endOfDirectory(HANDLE)

"""
=====================
关注列表函数
=====================
"""

def up_sub(mid, page=1, ps=30):
    ps=str(ps)
    pn=str(page)
    res=getbackAuto(f"https://api.bilibili.com/x/relation/followings?vmid={mid}&ps={ps}&pn={pn}")
    if res == False:
        return
    # 列表格
    xbmcplugin.setPluginCategory(HANDLE, "关注列表")
    for data in res["data"]["list"]:
        plot=data["sign"]
        plot+="\n\n[COLOR=grey]UID: "+str(data["mid"])+"[/COLOR]"
        if data["special"] == 1:
            plot+="\n[COLOR=yellow]特别关注[/COLOR]"
        if data["attribute"] == 6:
            plot+="\n[COLOR=pink]已互粉[/COLOR]"
        addXbmcItemCustom(
          data["uname"],
          get_url(action="ups_info", mid=str(data["mid"])),
          plot,
          True,
          icon=data["face"]
        )
    xbmcplugin.endOfDirectory(HANDLE)

"""
收藏夹元数据
"""
def up_fav_2nd(idx, p):
    idx2=str(idx)
    p2=str(p)
    res=getbackAuto(f"https://api.bilibili.com/x/v3/fav/resource/list?media_id={idx2}&order=mtime&ps=20&pn={p2}")
    if res == False:
        return
    xbmcplugin.setPluginCategory(HANDLE, "收藏夹/"+res["data"]["info"]["title"])
    total=res["data"]["info"]["media_count"]
    for d in res["data"]["medias"]:
        if d["type"] != 12 and d["attr"] == 0:
            plot=str(d["cnt_info"]["play"])+" 播放  "+str(d["cnt_info"]["danmaku"])+" 弹幕"
            plot+="\nUp主: "+d["upper"]["name"]+" [COLOR=grey]("+str(d["upper"]["mid"])+")[/COLOR]"
            plot+="\n"+unix2time(d["pubtime"])+" 发布"
            plot+="\n[COLOR=yellow]"+unix2time(d["fav_time"])+" 收藏[/COLOR]"
            plot+="\n\n"+d["intro"]
            addXbmcItemCustom(
              d["title"],
              get_url(action="bvplay", bv=d["bvid"]),
              plot,
              False,
              is_media=True,
              icon=d["cover"],
              fanart=d["cover"]
            )
    pages=int(total / 20)
    # 余数多一页显示
    if total % 20 != 0:
        pages+=1
    if pages > int(p):
        i={'name': "[COLOR=yellow]下一页[/COLOR] ("+str(p)+"/"+str(pages)+")", 'url': get_url(action="ups_fav_2nd", fid=idx, p=int(p)+1)}
    else:
        i={'name': "[COLOR=grey]页面最底处[/COLOR] ("+str(pages)+"/"+str(p)+")", 'url': get_url(action="not")}
    addXbmcItemCustom(
        i["name"],
        i["url"],
        "跳到下一页使的，或者可能你到底了",
        True
    )
    xbmcplugin.endOfDirectory(HANDLE)

def up_fav(mid):
    mid2=str(mid)
    res=getbackAuto(f"https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid={mid2}")
    if res == False:
        return
    # 好像一个用户默认都会有个默认文件夹罢
    # if res["data"]["list"] == Null or res["data"]["list"] == None:
        # warDialog("你的收藏夹里什么也没有。")
        # log("神人一点东西也一点不收藏是吧")
        # return
    xbmcplugin.setPluginCategory(HANDLE, "收藏夹")
    for data in res["data"]["list"]:
        plot=data["title"]+"\n\n共收藏 "+str(data["media_count"])+" 个视频"
        if int(str(data["attr"])[0]) == 0:
            plot+="\n[COLOR=yellow]公开收藏夹[/COLOR]"
        if int(str(data["attr"])[0]) == 1:
            plot+="\n[COLOR=yellow]私有收藏夹[/COLOR]"
        addXbmcItemCustom(
          data["title"],
          get_url(action="ups_fav_2nd", fid=data["id"], p=1),
          plot,
          True
        )
    xbmcplugin.endOfDirectory(HANDLE)