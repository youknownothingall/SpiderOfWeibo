#coding:utf-8
import urllib
import urllib2
import re
import os
import time
import random
import cookielib
#使用beautifulsoup对HTML页面进行解析
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#get_html()函数用于获取所爬取的页面的html源码
def get_html(url):
	headers={
		"Host":"s.weibo.com",
		"X-Requested-With":"XMLHttpRequest",
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
		#cookie必须加入header中，不然会新浪被识别爬虫，
		#此cookie是登陆新浪微博后的cookie，如果爬取微博搜索后的结果，请在浏览器搜素结果页面审查元素即可得到cookie
		#本程序不使用模拟登陆，用cookie足矣。
		"Cookie":"SINAGLOBAL=349097985308.6174.1443356423924; UOR=www.liaoxuefeng.com,widget.weibo.com,www.liaoxuefeng.com; _s_tentry=passport.weibo.com; Apache=2798693382646.8887.1443880700648; ULV=1443880700656:3:1:3:2798693382646.8887.1443880700648:1443497910007; SWB=usrmdinst_14; SUS=SID-1745602624-1443880732-GZ-sdpzu-684ac1aee00239c153a5fb22bce34c61; SUE=es%3D93f092dc576d6ff34be81638d4def405%26ev%3Dv1%26es2%3Ded9f307bedf27bf6e1c362d4eaeacc89%26rs0%3Dy1jtoxfkcLq7fU0lrBhVEgAeJ3ZJgA1hDq5cSDfYUuEjubh39NULk8DPNZWW5x4S3Q00Mi%252B%252FmZC%252Fcmc8fsaTK6IhGJPqzR5GyZc2sqdXZJDOSMqiiYMTiU5T4hjLyLVYaHQcy%252B%252BigI5My5VcvCnPVTC1Pb%252BJ3olOONq7p126Bms%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1443880732%26et%3D1443967132%26d%3Dc909%26i%3D4c61%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D27%26st%3D0%26uid%3D1745602624%26name%3D18813298638%26nick%3D%25E9%2598%25AE%25E6%259D%25BE%25E6%259D%25BE%26fmp%3D%26lcp%3D; SUB=_2A257C69MDeTxGedJ71cX8CzKyTiIHXVYYIeErDV8PUNbuNBeLW7kkW8AI3QS1bI5lBuN8Abx5jFDnf1SFA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh.8GBLH2hEPIeNpKaPiTNF5JpX5K2t; SUHB=0k1Du2TCRU6I30; ALF=1444485532; SSOLoginState=1443880732; un=18813298638; wvr=6; NSC_wjq_txfjcp_mjotij=ffffffff094113d445525d5f4f58455e445a4a423660; WBStore=4e40f953589b7b00|undefined"
	}
	mycookie = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
	openner = urllib2.build_opener(mycookie)
	req=urllib2.Request(url)
	for keys in headers:
		req.add_header(keys,headers[keys])
	html = openner.open(req).read()
	#将获取到的html源码分行，因为新浪微博将网页进行了压缩
	lines=html.splitlines()
	for line in lines:
		#以<script>STK && STK.pageletM && STK.pageletM.view({"pid":"pl_weibo_direct开头的是所有微博内容
		#如果报错的话，说明被识别成机器人了，然后手动将最后输出的URL用浏览器打开，输入验证码
		#一般爬取30几页就会被识别为爬虫，但是这个程序也有用，因为新浪微博搜索最多显示50页
		if line.startswith('<script>STK && STK.pageletM && STK.pageletM.view({"pid":"pl_weibo_direct'):
			#print "not caught"
			n = line.find('"html":"')
			if n > 0:
				get_html = line[n + 8: ].encode("utf-8").decode('unicode_escape').encode("utf-8").replace("\\", "")
			#else:
			#	print "caught"
	return get_html
#get_details()用于获得每条味浓的具体信息，如果看不懂的话可以去看看源码的HTML结构
def get_details(html):
	soup=BeautifulSoup(html)
	#得到作者、作者链接、微博正文
	div_content=soup.find_all(attrs={'class': 'content clearfix'})
	#得到发微博时间
	div_time=soup.find_all(attrs={'class':'feed_from W_textb'})
	#将用户名称，用户主页地址、微博正文、发微博时间初始化
	nick_name=[]
	nickname_href=[]
	content_text=[]
	time=[]
	#print get_content[0]
	for i in range(len(div_content)):
		#查找a标签
		a_tag=div_content[i].find('a')
		nick_name.append(a_tag.get('nick-name'))
		nickname_href.append(a_tag.get('href'))
		#查找p标签
		p_tag=div_content[i].find('p')
		content_text.append(p_tag.get_text())
	#得到发微博时间
	for j in range(len(div_time)):
		a_time=div_time[j].find('a')
		time.append(a_time.get('title'))
	return (nick_name,nickname_href,content_text,time)
#get_number_info()用于获得转发、评论、赞的数据
def get_number_info(html):#一次性得到所有数字
	soup = BeautifulSoup(html)
	#获取标签内容
	#查找
	get=soup.find_all(attrs={'class': 'feed_action_info feed_action_row4'})
	#收集转发、评论、赞的数据
	get_number_info=[]
	for i in range(len(get)):
		#转发
		forward=get[i].find(attrs={'action-type':'feed_list_forward'})
		forward_em=forward.find_all('em')
		#判断数据是否为0，
		if (len(forward_em[0].get_text())==0):
			temp_forward="0"
			get_number_info.append(temp_forward)
		else:
			temp_forward=forward_em[0].get_text()
			get_number_info.append(temp_forward)
		#评论
		comment=get[i].find(attrs={'action-type':'feed_list_comment'})
		if bool(comment.find_all('em')):
			comment_em=comment.find_all('em')
			temp_comment=comment_em[0].get_text()
			get_number_info.append(temp_comment)
		else:
			temp_comment="0"
			get_number_info.append(temp_comment)
		#赞
		like=get[i].find(attrs={'action-type':'feed_list_like'})
		like_em=like.find_all('em')
		if (len(like_em[0].get_text())==0):
			temp_like="0"
			get_number_info.append(temp_like)
		else:
			temp_like=like_em[0].get_text()
			get_number_info.append(temp_like)
	return get_number_info
#write_all_info()将所有数据写入文本
def write_all_info(nick_name,nickname_href,content_text,times,number_info):
	nick_name_list=nick_name
	nickname_href_list=nickname_href
	content_text_list=content_text
	time_list=times
	number_info_list=number_info
	path='E:/ruansongsong/'
	isExists=os.path.exists(path)
	if not isExists:
	    os.makedirs(path)
	temp=0
	for i in range(len(nick_name)):
		write_all_list=open(path+"weibo.txt",'a')
		write_all_list.writelines("微博用户名称："+nick_name_list[i]+"\n"+"微博链接："+nickname_href[i]+"\n"+"正文:"+"\n"+content_text_list[i]+"\n"+"发微博时间："+time_list[i]+"\n")
		j=0
		#由于我是将转发、评论、赞的数据储存到一个list中的，所以每一个微博正文要写入3个数据。
		while (j!=3):
			write_all_list.writelines("==="+number_info_list[temp]+"==="+"\n")
			j+=1
			temp+=1
		write_all_list.close()
#keyword="天津"
i=1#设置第一页
while (i<60):
	url="http://s.weibo.com/weibo/%25E5%25A5%2587%25E8%2591%25A9%25E8%25AF%25B4&page="+str(i)
	print url
	html=get_html(url)
	number_info=get_number_info(html)
	print len(number_info)
	(nick_name,nickname_href,content_text,times)=get_details(html)
	write_all_info(nick_name,nickname_href,content_text,times,number_info)
	#设置时间休眠，不然很快被识别成爬虫了
	sleeptime_rand = random.randint(1,30)
	print sleeptime_rand
	time.sleep(sleeptime_rand)
	i+=1