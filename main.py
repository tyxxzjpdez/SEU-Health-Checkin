#!/usr/bin/env python
# coding=utf-8
from bs4 import BeautifulSoup
import requests
import sys
import os
from urllib import parse
from requests.cookies import merge_cookies
import json
from datetime import datetime, date, timedelta

params = sys.argv
assert len(params) == 3, "You need 2 parameters: USERNAME and PASSWORD!"

START_URL="https://newids.seu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.seu.edu.cn%2Fqljfwapp2%2Fsys%2FlwReportEpidemicSeu%2F*default%2Findex.do%23%2FdailyReport"

r = requests.get(START_URL)
last_cookies = r.cookies
soup = BeautifulSoup(r.text, features="lxml")

data = {'username':params[1]}

father = soup.find(id="casLoginForm")
Salt = father.find(id="pwdDefaultEncryptSalt")['value']
data["password"] = os.popen("node ./interfaces.js {} {}".format(params[2], Salt)).read()[:-1]

others = father.find_all("input")[-6:-1]
for tag in others:
    data[tag['name']] = tag['value']

"""
get MOD_AUTH_CAS
"""
r = requests.post(START_URL, data=data, cookies=last_cookies)


"""
get old WEU
"""
r = requests.get("http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/*default/index.do", cookies=r.request._cookies)
new_cookies = r.request._cookies
new_cookies = merge_cookies(new_cookies, r.cookies)

"""
get new WEU
"""
r = requests.post("http://ehall.seu.edu.cn/qljfwapp2/sys/itpub/MobileCommon/getMenuInfo.do", cookies=new_cookies, 
                  data="data=%7B%27APPID%27%3A+%275821102911870447%27%2C+%27APPNAME%27%3A+%27lwReportEpidemicSeu%27%7D",
                  headers={"Content-Type": "application/x-www-form-urlencoded"})
new_cookies = r.request._cookies
new_cookies = merge_cookies(new_cookies, r.cookies)

"""
update time and WID
"""
r = requests.post("http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/mobile/dailyReport/getMyTodayReportWid.do", cookies=r.request._cookies)
initdict = json.loads(r.text)["datas"]["getMyTodayReportWid"]['rows'][0]

with open("./checkin.json","r") as f:
    template = json.load(f)
for k,v in template.items():
    if initdict[k]:
        template[k] = initdict[k]
    else:
        template[k] = "请选择"
template['CREATED_AT'] = datetime.now().strftime("%Y-%m-%d %H:%M")
template['DZ_DBRQ'] = datetime.strptime(str(date.today() + timedelta(days=-1)),"%Y-%m-%d").strftime("%Y-%m-%d")

"""
checkin
"""
r = requests.post("http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/mobile/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_SAVE.do", cookies=new_cookies,
                  data=template)
print(r.status_code)
print(r.text)
