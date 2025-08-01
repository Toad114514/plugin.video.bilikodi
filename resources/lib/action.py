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
    return 6
    