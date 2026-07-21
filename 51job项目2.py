import os
from time import sleep
from random import uniform
from random import random
from typing import List, Callable, Tuple, Optional, Dict

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
		TimeoutException,
		InvalidSelectorException,
		ElementClickInterceptedException,
		ElementNotInteractableException,
		StaleElementReferenceException
)

import tools

class Project_51job(object):
	
	WAIT_AFTER_SEARCH: Tuple[float, ...] = (0.5, 2.0)
	WAIT_NORMALLY: Tuple[float, ...] = (5.0, 9.0)
	WAIT_LONG: Tuple[float, ...] = (15.0, 25.0)
	WAIT_QUICK: Tuple[float, ...] = (3.0, 5.0)
	DEMAND: List[str] = ["职位", "薪资", "条件", "福利", "内容", "上班地址"]
	SEARCH_CONTENT = "python工程师"
	
	def __init__(self, url: str) -> None:
		"""
		count = 请求次数
		lazy_loading: 0 = 禁止懒加载, 2 = 懒加载
		headless: 0 = 不是无头, 1 = 无头
		"""
		count = 3
		lazy = 2
		yes = 0
		logger = tools.logging_configuration("51_job", logging.INFO, error=True)
		driver = tools.huoqu2(url, count, lazy, yes)
		if not driver:
			logger.critical("driver连接超时")
			raise RuntimeError("driver连接超时")
		EC_wait = 20
		find_element_wait = 10
		wait = WebDriverWait(driver, EC_wait)
		driver.implicitly_wait(find_element_wait)
		self.logger = logger
		self.driver = driver
		self.wait = wait
		
	def get_to_work_page(self) -> None:
		self.logger.info("查找搜索框")
		inputs = self.wait.until(
			EC.presence_of_element_located((By.ID, "keywordInput"))
		)
		sleep(uniform(*self.WAIT_AFTER_SEARCH))
		inputs.clear()
		tools.install_intervals_input()
		self.logger.info(f"输入{self.SEARCH_CONTENT}")
		inputs.intervals_input(self.SEARCH_CONTENT)
		sleep(uniform(*self.WAIT_AFTER_SEARCH))
		seek = self.wait.until(
			EC.presence_of_element_located((By.CLASS_NAME, "search-btn"))
		)
		self.logger.info("点击搜索")
		seek.click()
		sleep(uniform(*self.WAIT_AFTER_SEARCH))
		
	def find_target_object(self) -> list:
		self.logger.info("查找爬取内容")
		target_object = self.wait.until(
		EC.presence_of_all_elements_located((By.CLASS_NAME, "joblist-item-job-wrapper"))
		)
		sleep(uniform(*self.WAIT_AFTER_SEARCH))
		return target_object
		
	def find_data(self) -> Optional[Dict]:
		# 默认设置
		position_data = {demand: "暂无数据" for demand in self.DEMAND}
		self.logger.info("初始化爬取内容")
		# [需求，查找，方法，属性，处理器，前缀，替换]
		hint = Tuple[str, str, str, Optional[str], Optional[List[Callable[[str], str]]], Optional[str], Optional[str]]
		find_rules: List[hint] = [
			(self.DEMAND[0], './/div[@class="cn"]/h1', "attr", "title", None, None, None),
			(self.DEMAND[1], './/div[@class="cn"]/strong', "text", None, None, None, None),
			(self.DEMAND[2], './/div[@class="cn"]/p', "attr", "title", [tools.jcqx], None, None),
			(self.DEMAND[3], './/div[@class="t1"]/span[@class = "sp4"]', "text_list", None, None, None, None),
			(self.DEMAND[4], './/div[contains(@class,  "msg job_msg inbox" )]', "text", None, None, "\n", None),
			(self.DEMAND[5],  './/div[contains(@class, "bmsg inbox")]/p', "text", None, [tools.jcqx], None, "上班地址：")
		]
		for demand, xpath, method, attribute, disposes, prefix, replace in find_rules:
			try:
				# 查找
				if method == "attr":
					data = self.driver.find_element(By.XPATH, xpath).get_attribute(attribute)
				elif method == "text":
					element = self.driver.find_element(By.XPATH,xpath)
					data = element.text
				elif method == "text_list":
					elements = self.driver.find_elements(By.XPATH,xpath)
					data = " ".join([x.text for x in elements]) if elements else None
				else:
					data = None
				if data is None:
					self.logger.warning(f"{demand}未找到")
					continue
				# 数据清洗
				if disposes:
					for dispose in disposes:
						data = dispose(data)
				# 添加前缀
				if prefix:
					data = prefix + data
				# 多余数据删除
				if replace:
					data = data.replace(replace, "")
				position_data[demand] = data
			except Exception as e:
				self.logger.error(f"获取其他错误：{type(e).__name__} - {e}", exc_info=True)
				return None
		return position_data
		
	def save_file(self, position_data: Dict) -> None:
		fold = tools.establish_folder_path("work")
		file = tools.wjmz(position_data[self.DEMAND[0]] + ".txt")
		path = os.path.join(fold, file)
		file_path = tools.file_duplication_process(path, 1)
		with open(file_path, mode="a", encoding="utf-8") as f:
			for i, j in position_data.items():
				f.write(f"{i}: {j}\n")
			self.logger.info(f"保存{file}文件成功")
		
	def find_save(self) -> None:
		try:
			tools.qhwy(self.driver)
			position_data = self.find_data()
			self.logger.info(f"爬取{position_data[self.DEMAND[0]]}职位成功")
			self.save_file(position_data)
		except Exception as e:
			self.logger.error(f"查找保存阶段错误：{type(e).__name__} - {e}")
			return None
		
	def work_page(self) -> Optional[List]:
		try:
			self.get_to_work_page()
			target_object = self.find_target_object()
			return target_object
		except TimeoutException as e:
			self.logger.error(f"请求阶段wait超时未找到, {e}")
			return None
		except InvalidSelectorException as e:
			self.logger.error(f"请求阶段语法错误, {e}")
			return None
		except ElementClickInterceptedException as e:
			self.logger.error(f"请求阶段元素被挡, {e}")
			return None
		except ElementNotInteractableException as e:
			self.logger.error(f"请求阶段元素不可交互, {e}")
			return None
		except StaleElementReferenceException as e:
			self.logger.error(f"请求阶段元素过时, {e}")
			return None
		except Exception as e:
			self.logger.error(f"请求阶段其他错误：{type(e).__name__} - {e}", exc_info=True)
			return None
		
	def preserve_wait(self, target_object) -> None:
		length = len(target_object)
		for num, position in enumerate(target_object, start=1):
			position.click()
			sleep(uniform(*self.WAIT_QUICK))
			self.find_save()
			wait_time = random()
			lose_interest = 0.2
			# 0.3比0.2大0.1实际上就是0.1
			interest = 0.3
			# 剩下的0.7为正常时间
			if wait_time < lose_interest:
				sleep(uniform(*self.WAIT_QUICK))
			elif wait_time < interest:
				sleep(uniform(*self.WAIT_LONG))
			else:
				sleep(uniform(*self.WAIT_NORMALLY))
			self.driver.close()
			sleep(uniform(*self.WAIT_NORMALLY))
			tools.qhwy(self.driver)
			if num != length:
				self.logger.info("下一个职位")
			
	def search_for_page_numbers(self) -> Optional[int]:
		try:
			self.logger.info("查找最大页数")
			num = self.wait.until(
				EC.presence_of_element_located((By.XPATH, './/ul[@class="el-pager"]/li[@class="number"]'))
			)
			sleep(uniform(*self.WAIT_AFTER_SEARCH))
			num = int(num.text)
			return num
		except TimeoutException as e:
			self.logger.error(f"查找页数阶段wait超时未找到, {e}")
			return None
		except InvalidSelectorException as e:
			self.logger.error(f"请求阶段语法错误, {e}")
			return None
		except Exception as e:
			self.logger.error(f"查找页数阶段其他错误：{type(e).__name__} - {e}")
			return None
		
	def next_page(self) -> None:
		try:
			self.logger.info("查找下一页按钮")
			button = self.wait.until(
				EC.presence_of_element_located((By.CLASS_NAME, "btn-next"))
			)
			sleep(uniform(*self.WAIT_AFTER_SEARCH))
			button.click()
		except ElementClickInterceptedException as e:
			self.logger.error(f"下一页阶段元素被挡, {e}")
			return None
		except ElementNotInteractableException as e:
			self.logger.error(f"下一页阶段元素不可交互, {e}")
			return None
		except StaleElementReferenceException as e:
			self.logger.error(f"下一页阶段元素过时, {e}")
			return None
		except Exception as e:
			self.logger.error(f"下一页阶段其他错误：{type(e).__name__} - {e}", exc_info=True)
			return None
		
	def activate(self) -> None:
		try:
			num = self.search_for_page_numbers()
			for i in range(1, num+1):
				target_object = self.work_page()
				self.preserve_wait(target_object)
				if i != num:
					self.logger.info("下一页")
					self.next_page()
		except TypeError as e:
			self.logger.error(f"获取参数错误, {e}")
			return None
		except Exception as e:
			self.logger.error(f"其他错误：{type(e).__name__} - {e}", exc_info=True)
			return None
		finally:
			self.driver.quit()
			self.logger.info("浏览器已关闭")
		
if __name__ == "__main__":
	url = "https://we.51job.com/pc/search"
	project_51job = Project_51job(url)
	project_51job.activate()
	