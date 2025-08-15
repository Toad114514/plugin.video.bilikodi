import os, sys, requests, json, random, string
import xbmc

from resources.lib.core import *
from resources.lib.cookie import *

def check_json(jsondata):
    try:
        data = json.loads(jsondata)
        return True
    except:
        return False

def getback_c(url, UA_head, c=load_cookie()):
    try:
        res=requests.get(url, headers=get_ua(), cookies=c)
        res_text=res.text
    except requests.exceptions.RequestException as e:
        warDialog("无法从网上获取 json 数据")
        return False
    if check_json(res_text):
        xbmc.log(res_text)
        res_text=json.loads(res_text)
        if res_text["code"] == 0:
            log(res_text)
            return res_text
        else:
            warDialog("[Bilikodi] 数据返回错误码: "+str(res_text["code"]))
            return False
    else:
        warDialog("[Bilikodi] 无法解析 json 数据")
        return False

def getbackAuto(url, headers=get_ua(), cookies=load_cookie()):
    try:
        res=requests.get(url, headers=headers, cookies=cookies).json()
    except:
        warDialog("网络不好或无法解析")
        log("Fuck you wifi!!!") # Oops, 发现我的神秘彩蛋了
        return False
    if res["code"] == 0:
        return res
    else:
        warDialog("[Bilikodi] 数据错误: "+str(res["code"])+"("+res["message"]+")")
        log("Fuck API return "+str(res["code"]))
        return False

def getback(url, UA_head):
    try:
        res=requests.get(url, headers=UA_head)
        res_text=res.text
    except requests.exceptions.RequestException as e:
        xbmc.log("无法从网上获取 json 数据")
        return False
    if check_json(res_text):
        xbmc.log(res_text)
        res_text=json.loads(res_text)
        if res_text["code"] == 0:
            return res_text
        else:
            warDialog("[Bilikodi] 数据返回错误码: "+str(res_text["code"]))
            xbmc.log(str(res_text))
            return False
    else:
        xbmc.log("[Bilikodi] 无法解析 json 数据")
        xbmc.log(res_text)
        return False

# POST
def postbackAuto(url, p, h=get_ua(), c=load_cookie()):
    try:
        res=requests.post(url, data=p, headers=h, cookies=c).json()
    except:
        warDialog("网络不好或无法解析")
        log("Fuck you wifi/API return!!!")
        return False
    if res["code"] == 0:
        return res
    else:
        warDialog("[Bilikodi] 数据错误: "+str(res["code"])+"("+res["message"]+")")
        log("Fuck API return (POST) "+str(res["code"]))
        return False
    