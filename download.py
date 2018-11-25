#coding:utf-8
#written by pojoy


import requests, sys, os, io, re, time
sys.setrecursionlimit(10**6)

# initialize
www_gamecity = ["https:", "", "d00030400.gamecity.ne.jp", "a_girl"]
news_top_html = ["www","news","top.html"]
official_blog_index_html = ["www", "official", "blog", "index.html"]
ps = "/"
ostype = "posix"
if os.name == "nt":
	ps = "\\"
	ostype = "nt"
errornumber = 0
updated_lst = []
setting = []
allupdate = True
htmlupdate = True
setting_date = {}
updated_setting_date = {}

"""
www/official/blog/index.html
https://d00030400.gamecity.ne.jp/a_girl/www/news/top.html
https://d00030400.gamecity.ne.jp/a_girl/www/official/blog/index.html
からたどれる html,jpg,png,ico,js,css,mp3,mp4ファイルを深さ優先で探索しつつダウンロード
"""

def nowlocaltime():
	t = time.localtime()
	return f"{t.tm_year}/{t.tm_mon}/{t.tm_mday} {t.tm_hour}:{t.tm_min}"

def errlog(mess, end = "\n"):
	# type(mess) == string
	global errornumber
	with open(pathname(["Error.log"]), "a") as f:
		if errornumber == 0:
			f.write(f"\n----------------------- errorlog start -----------------------\n{nowlocaltime()}\n")
		errornumber += 1
		f.write(mess+end)

def note(par, child):
	with open(pathname(["note.txt"]), "a", encoding = "utf-8") as f:
		f.write(f"future warning: '{pathname(child)}' in {pathname(par)}\n")

# return True or False
def judge_readablefile(s):
	# arr == "example.html"
	j = ["jpg", "png", "gif", "ico", "mp", "pdf", "js"]
	flag = True
	for i in j:
		if i in s:
			flag = False
	return flag

# return ["www", "example.html"]
def urlstring2list(arr, string):
	# arr == ["www", "sample.html"], str == "'www/example.html'" or "(example.com)"
	lst = string.replace('"', '').replace("'", "").replace("(", "").replace(")", "").split("/")
	if lst[0] == "https:" and lst[2] == "d00030400.gamecity.ne.jp":
		note(arr, lst)
		lst = lst[4:]
	elif lst[0] == "https:" or lst[0] == "http:":
		errlog(f"Unexpected url : {'/'.join(lst)}")
		return []
	return lst

# return True or False
def judge_unexpected(s):
	# s == "'example/example.html'"
	lst = ["google", "join", "pop", "viewport", "stop", "shift"]
	flag = True
	for i in lst:
		if i in s:
			flag = False
	return flag

# return list(urllist)
def fildallurl(s):
	# type(s) == string
	lst = re.findall('["\'(][0-9a-zA-Z./:_-]+\.[(html|jpg|png|ico|css|js|mp3|mp4|csv|pdf|gif)]+["\')]',s)
	ref = []
	for l in lst:
		if judge_unexpected(l):
			ref += [l]
	return ref

# return "./www/example/example.html" if linux/Mac else "www/example/example.html"
def pathname(arr):
	# arr = ["www", "example", "example.html"]
	if ostype == "nt":
		return ps.join(arr)
	else:
		return ps.join(["."]+arr)

#return []
def findurlfromarr(arr):
	# arr == ["www", "example", "example.html"]
	if not(judge_readablefile(arr[-1])):
		return []
	lst = []
	try:
		with open(pathname(arr), "r", encoding="utf-8") as f:
			for line in f.readlines():
				lst += fildallurl(line)
	except FileNotFoundError:
		errlog(f"downloaded file does not exist : {pathname(arr)}")
	except UnicodeDecodeError:
		errlog(f"unicode decode error : {pathname(arr)}")
	ret = []
	for i in lst:
		ret += [urlstring2list(arr, i)]
	return ret

# return requests.class.Responce
def get(arr):
	# arr = ["www"] + [something]
	print(f"download : {'/'.join(arr)}", end="")
	ref = requests.get("/".join(www_gamecity + arr))
	time.sleep(0.05)
	print("\tOK." if ref.status_code == 200 else "\tMiss.")
	return ref

# return arr or []
def download(arr, par):
	# arr = ["www", "example", "example.html"]
	global updated_lst
	ret = []
	if not(judge_readablefile(arr[-1])) and not(allupdate) and os.access(pathname(arr), os.F_OK):
		updated_lst += [arr]
		return ret
	if not(os.access(pathname(arr), os.F_OK)) or htmlupdate :
		os.makedirs(pathname(arr[:-1]), exist_ok=True)
		ref = get(arr)
		if ref.status_code == 200:
			with open(pathname(arr), "wb") as f:
				f.write(ref.content)
			# updated_setting_date[ps.join(arr)] = re.sub(" ", "", ref.headers["Last-Modified"])
			ret = arr
		else:
			errlog(f"Get Error: {ref.status_code} {ps.join(arr)} in {ps.join(par)}")
	elif not(arr in updated_lst):
		ret = arr
	updated_lst += [arr]
	return ret

# return ["www", "exampledir", "example.html"]
def organize_lst(arr):
	# arr == ["www", "example", "..", "..", "www", "example", "example.html"]
	ref = []
	for i in range(len(arr)):
		if arr[i] == "..":
			ref = ref[:-1]
		else:
			ref += [arr[i]]
	return ref

# return
def search_newfile_and_download(arr):
	# arr == ["www", "example", "example.html"]
	if not(judge_readablefile(arr[-1])):
		return
	print(f"check {ps.join(arr)}")
	lst = []
	lst += findurlfromarr(arr)
	for l in lst:
		# l == [".., "example", example.html]
		new_path = organize_lst(arr[:-1] + l)
		# if l == ["www", "examle", "example.html"]
		if l[0] == "www":
			new_path = l
		# new_path == ["www", "exaple", "exapmle.thml"]
		if not new_path in updated_lst:
			download(new_path, arr)
			search_newfile_and_download(new_path)

def main():
	global allupdate
	global updated_lst
	global htmlupdate
	global setting_date

	# time check
	nowtime = time.localtime()
	if nowtime.tm_year >= 2019 or (nowtime.tm_year == 2018 and nowtime.tm_mon >= 12):
		print(u"\nperhaps, site closed.\nzou realz want ro run this program?(y/n)\n> ", end = "")
		s = input()
		while(not(s == "yes" or s == "no" or s == "y" or s == "n" or s == "Y" or s == "N") or s==""):
			s = input(u"yes or no> ")
		if s == "y" or s == "yes" or s == "Y":
			pass
		else:
			print(u"\nR.\nHave a nice trip with you and all bots!\n\n")
			return
	
	# file check
	if os.access(pathname(["setting.txt"]), os.F_OK):
		with open(pathname(["setting.txt"]), mode="r", encoding="utf-8") as f:
			for line in f.readlines():
				try:
					r1, r2 = line.split()
					setting_date[r1] = r2
				except:
					pass
	else:
		print(u"\nsetting.txt does not exist.")
	
	# select option
	if os.access(pathname(news_top_html), os.F_OK):
		print(u"\nperhaps, already downloaded.\nselect number\n\
1, download all\n\
2, download html, css, js and missing imgs.\n\
3, download only missing items\n\
4, stop this program\n\
(1/2/3/4)> ", end="")
		s = input()
		while(not(s == "1" or s == "2" or s == "3" or s == "4" or s == "１" or s == "２" or s == "３" or s == "４") or s==""):
			s = input("(1/2/3/4) > ")
		if s == "1" or s == "１":
			pass
		elif s == "2" or s == "２":
			allupdate = False
		elif s == "3" or s == "３":
			allupdate = False
			htmlupdate = False
		else:
			print(u"stop this program.\nHave a nice trip with you and all bots!\n")
			return
	else:
		print("if you have questions, twitterID:@96kawasemi")
	ref = input(u"\npless enter\n")
	if ref == "numa":
		print(u"numa!")
		return

	# www/official/blog/index.html
	ref = requests.get("/".join(www_gamecity+official_blog_index_html))
	temp = re.sub(r' ', '', ref.headers["Last-Modified"])
	os.makedirs(pathname(official_blog_index_html[:-1]), exist_ok=True)
	blogindex_skip = False
	updated_setting_date[ps.join(official_blog_index_html)] = temp
	if not(pathname(official_blog_index_html) in setting_date):
		pass
	elif setting_date[pathname(official_blog_index_html)] == temp and htmlupdate and not(allupdate):
		s = input(u"official/blog/index.html dont updated. you want update?\n(y/n)> ")
		while(not(s == "yes" or s == "no" or s == "y" or s == "n" or s == "Y" or s == "N") or s==""):
			s = input(u"yes or no > ")
		if s == "y" or s == "Y" or s == "yes":
			pass
		else:
			print("skip official/blog/index.html")
			blogindex_skip = True
	# save data
	if ref.status_code == 200:
		try:
			if blogindex_skip:
				pass
			else:
				with open(pathname(official_blog_index_html), mode=("wb" if htmlupdate else "xb")) as f:
					f.write(ref.content)
		except FileExistsError:
			pass
		updated_lst += [official_blog_index_html]
		search_newfile_and_download(official_blog_index_html)
	elif ref.status_code == 404:
		print(f"404 NotFound (;ω;) : {pathname(official_blog_index_html)}")
	else:
		print(f"please check network\nerror code : {ref.status_code}")
	
	# www/news/top.html
	ref = requests.get("/".join(www_gamecity+news_top_html))
	os.makedirs(pathname(news_top_html[:-1]), exist_ok=True)
	# check update
	oshirase_skip = False
	temp = re.sub(r' ', '', ref.headers["Last-Modified"])
	updated_setting_date[ps.join(news_top_html)] = temp
	if not(pathname(news_top_html) in setting_date) or news_top_html in updated_lst:
		pass
	elif setting_date[pathname(news_top_html)] == temp and htmlupdate and not(allupdate):
		s = input(u"news/top.html dont updated. you want update?\n(y/n)> ")
		while(not(s == "yes" or s == "no" or s == "y" or s == "n" or s == "Y" or s == "N") or s==""):
			s = input(u"yes or no > ")
		if s == "y" or s == "Y" or s == "yes":
			pass
		else:
			print("skip news/top.html")
			oshirase_skip = True
	# save data
	if oshirase_skip or (pathname(news_top_html) in updated_lst):
		pass
	elif ref.status_code == 200:
		try:
			with open(pathname(news_top_html), mode=("wb" if htmlupdate else "xb")) as f:
				f.write(ref.content)
		except FileExistsError:
			pass
		updated_lst += [news_top_html]
		search_newfile_and_download(news_top_html)
	elif ref.status_code == 404:
		print(f"404 NotFound (;ω;) : {pathname(news_top_html)}")
	else:
		print(f"please check network\nerror code : {ref.status_code}")
	
	# end main
	if errornumber != 0:
		errlog("------------------------ errorlog end ------------------------\n")

# main()
main()

# make setting.txt
with open(pathname(["setting.txt"]), "w", encoding="utf-8") as f:
	for i in updated_setting_date:
		f.write(f"{i} {updated_setting_date[i]}\n")

# after main
print("program finished\n\nHave a nice trip with you and all bots!\n")

s = input("pless enter")

