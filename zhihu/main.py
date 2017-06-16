#/usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = 'ByPupil'

import requests, os, time, json
import http.cookiejar as cookielib
from bs4 import BeautifulSoup



headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
	"Referer": "https://www.zhihu.com/",
	'Host': 'www.zhihu.com'
}


session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
	session.cookies.load(ignore_discard=True)
except:
	print("Cookie未加载")

def get_xsrf():
	'''
		获取_xsrf参数
	'''
	index_url = "https://www.zhihu.com"
	index_page = session.get(index_url, headers=headers)
	soup = BeautifulSoup(index_page.text, "html.parser")
	_xsrf = soup.find('input', {'name': '_xsrf', 'type': 'hidden'}).get('value')
	return _xsrf


def get_captcha():
	'''
		获取验证码内容
	'''
	t = str(int(time.time() * 1000))
	captcha_url = "https://www.zhihu.com/captcha.gif?r=" + t + "&type=login"
	r = session.get(captcha_url, headers=headers)
	with open('captcha.gif', 'wb') as f:
		f.write(r.content)
	print(u"请到 %s 目录下找到验证码" % os.path.abspath('captcha.gif'))
	captcha = input(r"请输入验证码:")
	return captcha


def isLogin():
	'''
		查看个人信息判断是否登录
	'''
	url = "https://www.zhihu.com/settings/profile"
	login_code = session.get(url, allow_redirects=False, headers=headers).status_code
	print(login_code)
	if int(login_code) == 200:
		return True
	else:
		return False


def login(secret, account):
	'''
		用户登录	
	'''
	_xsrf = get_xsrf()
	headers['X-Xsrftoken'] = _xsrf
	headers["X-Requested-With"] = "XMLHttpRequest"
	if account.find('@') == -1:
		print(u"手机号")
		post_url = "https://www.zhihu.com/login/phone_num"
		postdata = {
			'_xsrf': _xsrf,
			'password': secret,
			'phone_num': account
		}
	else:
		print(u"邮箱")
		post_url = "https://www.zhihu.com/login/email"
		postdata = {
			'_xsrf': _xsrf,
			'password': secret,
			'email': account
		}

	try:
		login_page = session.post(post_url, data=postdata, headers=headers)
		login_code = login_page.json()
		if login_code['r'] == 1:
			postdata['captcha'] = get_captcha()
			login_page = session.post(post_url, data=postdata, headers=headers)
			login_code = login_page.json()
			print(login_code['msg'])
	except:
		postdata['captcha'] = get_captcha()
		login_page = session.post(post_url, data=postdata, headers=headers)
		login_code = login_page.json()
		print(login_code['msg'])
	session.cookies.save(filename='cookies', ignore_discard=True)
	return True


def get_content_list(offset, start):
	_xsrf = get_xsrf()
	headers['X-Xsrftoken'] = _xsrf
	headers["X-Requested-With"] = "XMLHttpRequest"
	list_url = 'https://www.zhihu.com/node/TopStory2FeedList'
	params = '{"offset":%d,"start":"%d"}' % (offset, start)
	print(params)
	postdata = {
		'params': params,
		'method': 'next'
	}
	resp = session.post(list_url, data=postdata, headers=headers)
	return json.loads(resp.text)


def get_real_data(list_content):
	return 0


if __name__ == '__main__':
	while True:
		if isLogin():
			print("您已经登录")
			print(get_content_list(1, 20))
			break
		else:
			account = input('请输入用户名\n>')
			secret = input('请输入密码\n>')
			result = login(secret, account)
			if result == True:
				conf_url = "https://www.zhihu.com/settings/profile"
				text = session.get(conf_url, headers=headers).text
				print(text)
				break







