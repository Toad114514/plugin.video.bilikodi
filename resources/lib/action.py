import requests, time, os, sys
import xbmc, xbmcgui, xbmcvfs, xbmcplugin

from resources.lib.xbmc import *
from resources.lib.core import *
from resources.lib.get import *
from resources.lib.wbi import *

# 点赞给某ups
def like_action(bv):
    # sel = xbmcgui.Dialog().select("点赞？", "对"+bv+"稿件进行的点赞操作是？", "取消操作", yeslabel="点赞", nolabel="取消点赞")
    # xbmcgui.Dialog().ok("?", sel)
    params={
      'bvid': bv,
      'like': 1,
      'csrf': read_cookie("bili_jct")
    }
    res=postbackAuto("https://api.bilibili.com/x/web-interface/archive/like", params)
    if res != False:
        xbmcgui.Dialog.ok("good", "已为 "+bv+" 视频点赞")


    