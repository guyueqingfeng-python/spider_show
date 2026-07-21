from time import sleep
import random
import os
import ast

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import (
	InvalidSelectorException,
	ElementClickInterceptedException,
	ElementNotInteractableException,
	StaleElementReferenceException,
	TimeoutException,
	NoSuchElementException
)

import tools




def qingqiu(driver):
	tools.install_intervals_input()
	wait = WebDriverWait(driver, 10)
	driver.implicitly_wait(10)
	sleep(random.uniform(0.5, 2))
	inputs = wait.until(
		EC.presence_of_element_located((By.ID, "keywordInput"))
	)
	sleep(random.uniform(0.5, 2))
	inputs.clear()
	inputs.intervals_input("python工程师")
	sleep(random.uniform(0.5, 2))
	cilke = wait.until(
		EC.presence_of_element_located((By.CLASS_NAME, "search-btn"))
	)
	cilke.click()
	sleep(random.uniform(0.5, 2))
	return wait
	
def jinbu(wait):
	zxx = wait.until(
		EC.presence_of_all_elements_located((By.CLASS_NAME, "joblist-item-job-wrapper"))
	)
	sleep(random.uniform(0.5, 2))
	return zxx
	
def huoqu(cxx, driver):
		cxx.click()
		sleep(random.uniform(0.5, 2))
		# try:
		tools.qhwy(driver)
		cid = {}
		sleep(random.uniform(2, 4))
		cid["职位"] = driver.find_element(By.XPATH, './/div[@class = "cn"]/h1').get_attribute("title")
		cid["薪资"] = driver.find_element(By.XPATH, './/div[@class = "cn"]/strong').text
		wei1 = driver.find_element(By.XPATH, './/div[@class = "cn"]/p').get_attribute("title")
		cid["条件"] = tools.jcqx(wei1)
		wei2 = [x.text for x in driver.find_elements(By.XPATH, './/div[@class = "t1"]/span[@class = "sp4"]')]
		cid["福利"] = " ".join(wei2) if wei2 else "暂无数据"
		de = [x.text for x in driver.find_elements(By.XPATH, './/div[contains(@class,  "msg job_msg inbox" )]')]
		ni = "\n" + "".join(de)
		cid["内容"] = ni if ni else "暂无数据"
		try:
			wei3 = tools.jcqx(driver.find_element(By.XPATH, './/div[contains(@class, "bmsg inbox")]/p').text)
			wei3 = wei3.replace("上班地址：", "")
			cid["上班地址"] = wei3
		except NoSuchElementException:
			cid["上班地址"] = "暂无数据"
		sleep(random.uniform(1, 3))
		# except:
		# 	button1 = driver.find_element(By.XPATH, "(.//button[contains(@class, 'el-button el-button--primary')])[3]")
		# 	button1.click()
		# 	sleep(random.uniform(5, 9))
		# 	tool.qhwy(driver)
		# 	button2 = driver.find_element(By.XPATH, '(.//button[@class = "el-dialog__headerbtn"])[4]')
		# 	sleep(random.uniform(0.5, 1.5))
		# 	button2.click()
		# 	cid = {}
		# 	cid["职位"] = driver.find_element(By.CLASS_NAME, "job").text
		# 	sleep(random.uniform(0.5, 1.5))
		# 	cid["薪资"] = driver.find_element(By.CLASS_NAME, "salary").get_attribute("title")
		# 	sleep(random.uniform(0.5, 1.5))
		# 	wei1 = driver.find_elements(By.XPATH, './/div[@class="detail-title-left-center"]/div[@class = "item"]/span')
		# 	wei1 = list(map(lambda x: tool.jcqx(x.text), wei1))
		# 	n = wei1[:-1]
		# 	cid["条件"] = " ".join(n[1:])
		# 	sleep(random.uniform(0.5, 1.5))
		# 	wei2 = list(
		# 		map(lambda x: x.text, driver.find_elements(By.XPATH, './/div[@class = "t1"]/span[@class = "sp4"]')))
		# 	if not wei2:
		# 		wei2.append("暂无数据")
		# 	cid["福利"] = " ".join(wei2)
		# 	sleep(random.uniform(0.5, 1.5))
		# 	de = list(map(lambda x: x.text, driver.find_elements(By.XPATH, '(.//div[@class = "text"])[2]')))
		# 	de = "\n" + "".join(de)
		# 	cid["内容"] = "".join(de)
		# 	sleep(random.uniform(0.5, 1.5))
		# 	try:
		# 		cid["上班地址"] = wei1[0]
		# 	except:
		# 		cid["上班地址"] = "暂无数据"
		# 	driver.close()
		# 	sleep(5)
		# 	tool.qhwy(driver)
		return cid
		
def lj(path, x):
	fold = os.path.dirname(path)
	file = os.path.basename(path)
	name, ext = os.path.splitext(file)
	nam = list(name)
	while True:
		n = nam.pop()
		try:
			b = ast.literal_eval(n)
		except:
			b = n
		if not type(b) == int:
			nam.append(n)
			name = "".join(nam)
			break
	refile = f"{name}{x}{ext}"
	path2 = os.path.join(fold, refile)
	if os.path.exists(path2):
		return lj(path2, x+1)
	else:
		return path2
	
def baocun(cid):
	os.makedirs("work", exist_ok=True)
	a  = tools.wjmz(f'{cid["职位"]}.txt')
	path = os.path.join("work", a)
	dir = os.path.dirname(path)
	file = os.path.basename(path)
	name, ext = os.path.splitext(file)
	refile = f"{name}1{ext}"
	path1 = os.path.join(dir, refile)
	if os.path.exists(path1):
		path2 = lj(path, 1)
		path = path2
	if os.path.exists(path):
		os.rename(path, path1)
		path2 = lj(path, 1)
		path = path2
	with open(path, mode = "w", encoding="utf-8") as f:
		for i, j in cid.items():
			f.write(i)
			f.write("：")
			f.write(j)
			f.write("\n")

def qidong(url):
	driver = tools.huoqu2(url, 3, 0, 0)
	if not driver:
		raise RuntimeError("driver请求失败")
	try:
		wait = qingqiu(driver)
		num = wait.until(
			EC.presence_of_element_located((By.XPATH, './/ul[@class="el-pager"]/li[8]'))
		)
		num = int(num.text)
	except TypeError as e :
		print(f"请求阶段参数错误, {e}")
		return
	except TimeoutException as e:
		print(f"请求阶段wait超时未找到, {e}")
		return
	except NoSuchElementException as e:
		print(f"请求阶段元素不存在, {e}")
		return
	except InvalidSelectorException as e:
		print(f"请求阶段语法错误, {e}")
		return
	except ElementClickInterceptedException as e:
		print(f"请求阶段元素被挡, {e}")
		return
	except ElementNotInteractableException as e:
		print(f"请求阶段元素不可交互, {e}")
		return
	except StaleElementReferenceException as e:
		print(f"请求阶段元素过时, {e}")
		return
	except Exception as e:
		print(f"请求阶段其他错误：{type(e).__name__} - {e}")
		return
	try:
		for x in range(1, num+1):
			zxx = jinbu(wait)
			for i in (zxx):
				cid = huoqu(i, driver)
				try:
					baocun(cid)
				except Exception as e:
					print(f"存在错误：{type(e).__name__} - {e}")
				shu = random.random()
				if shu < 0.2:
					sleep(random.uniform(3, 5))
				elif shu < 0.3:
					sleep(random.uniform(15, 25))
				else:
					sleep(random.uniform(5, 9))
				driver.close()
				tools.qhwy(driver)
				sleep(random.uniform(3, 6))
			butten = driver.find_element(By.CLASS_NAME, "btn-next")
			sleep(random.uniform(0.5, 1.5))
			if x == num:
				pass
			else:
				butten.click()
			sleep(random.uniform(5, 9))
		sleep(5)
	except TypeError as e:
		print(f"获取参数错误, {e}")
		return
	except TimeoutException as e:
		print(f"获取wait超时未找到, {e}")
		return
	except NoSuchElementException as e:
		print(f"获取元素不存在, {e}")
		return
	except InvalidSelectorException as e:
		print(f"获取语法错误, {e}")
		return
	except ElementClickInterceptedException as e:
		print(f"获取元素被挡, {e}")
		return
	except ElementNotInteractableException as e:
		print(f"获取元素不可交互, {e}")
		return
	except StaleElementReferenceException as e:
		print(f"获取元素过时, {e}")
		return
	except Exception as e:
		print(f"获取其他错误：{type(e).__name__} - {e}")
		return
	finally:
		driver.quit()
		print("已关闭")
		
if __name__ == "__main__":
	url = "https://search.51job.com/list/000000,000000,0000,00,9,99,+,2,1.html"
	qidong(url)