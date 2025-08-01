import os, sys, requests, json, random, sys
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
from resources.lib.core import *
from urllib.parse import urlencode, parse_qsl

ADDON=xbmcaddon.Addon()
URL = sys.argv[0]
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
HANDLE = int(sys.argv[1])
IMAGE_dir = os.path.join(ADDON_PATH, 'resources', 'images')
# good folder
fanart_bg = os.path.join(ADDON_PATH, "fanart.png")
folder_icon = os.path.join(IMAGE_dir, "folder.png")

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(URL, urlencode(kwargs))

def addXbmcItem(label,param,is_folder):
    list_item = xbmcgui.ListItem(label)
    info_tag = list_item.getVideoInfoTag()
    info_tag.setMediaType('video')
    info_tag.setTitle(label)
    list_item.setArt({'icon': get_img('folder'), 'fanart': fanart_bg})
    url=get_url(action=param)
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

def addXbmcItemInfo(label,param,info,is_folder):
    list_item = xbmcgui.ListItem(label)
    info_tag = list_item.getVideoInfoTag()
    info_tag.setMediaType('video')
    info_tag.setTitle(label)
    info_tag.setPlot(info)
    list_item.setArt({'icon': get_img('folder'), 'fanart': fanart_bg})
    url=get_url(action=param)
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)

def addXbmcItemCustom(label, url, info, is_folder=True, is_media=False, icon=folder_icon, fanart=fanart_bg, context=None):
    """
    添加较高自定义的 Xbmc 菜单项目
    
    :string label: 项目名
    :string url: Url params，一般填 get_url()
    :string info: 项目详细信息
    :boolean is_folder: 是否为文件夹（默认True）
    :boolean is_media: 是否可播放（默认False）
    :string icon: 图标
    :string fanart: 同人图（项目被选中时的背景）
    :list context: 上下文菜单（默认 None 就啥也不设置）
    """
    list_item = xbmcgui.ListItem(label)
    info_tag = list_item.getVideoInfoTag()
    info_tag.setMediaType('video')
    info_tag.setTitle(label)
    info_tag.setPlot(info)
    if is_media:
        list_item.setProperty('IsPlayable', 'true')
    if context != None:
        list_item.addContextMenuItems(context)
    list_item.setArt({'icon': icon, 'fanart': fanart})
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)