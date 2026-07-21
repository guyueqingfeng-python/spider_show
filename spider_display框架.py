import os
import json
from time import sleep
from random import uniform
from random import random
from typing import List, Callable, Tuple, Optional, Dict

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

class Spider_display_frame():

    WAIT_AFTER_SEARCH: Tuple[float, ...] = (0.5, 2.0)
    WAIT_NORMALLY: Tuple[float, ...] = (5.0, 9.0)
    WAIT_LONG: Tuple[float, ...] = (15.0, 25.0)
    WAIT_QUICK: Tuple[float, ...] = (3.0, 5.0)

    def __init__(self, config_path: str) -> None:
        with open(config_path, "r", encoding="UTF-8") as f:
            self.config = json.load(f)
        logger = tools.logging_configuration(self.config["基础信息"]["logger_name"])
        driver = tools.huoqu2(self.config["基础信息"]["url"])
        if not driver:
            logger.critical("driver连接超时")
            raise RuntimeError("driver连接超时")
        wait = WebDriverWait(driver, self.config["基础信息"]["wait"]["EC_wait"])
        driver.implicitly_wait(self.config["基础信息"]["wait"]["find_element_wait"])
        self.logger = logger
        self.driver = driver
        self.wait = wait

    def get_to_work_page(self) -> None:
        self.logger.info("查找搜索框")
        inputs = self.wait.until(
            EC.presence_of_element_located(tools.get_by(self.config["找到页面"]["search_box"]))
        )
        sleep(uniform(*self.WAIT_AFTER_SEARCH))
        inputs.clear()
        tools.install_intervals_input()
        self.logger.info(f"输入{self.config['找到页面']['search_input']}")
        inputs.intervals_input(self.config["找到页面"]["search_input"])
        sleep(uniform(*self.WAIT_AFTER_SEARCH))
        seek = self.wait.until(
            EC.presence_of_element_located(tools.get_by(self.config["找到页面"]["search_btn"]))
        )
        self.logger.info("点击搜索")
        seek.click()
        sleep(uniform(*self.WAIT_AFTER_SEARCH))


    def find_target_object(self) -> list:
        self.logger.info("查找爬取内容")
        target_object = self.wait.until(
            EC.presence_of_all_elements_located(tools.get_by(self.config["找到页面"]["scrape_list"]))
        )
        sleep(uniform(*self.WAIT_AFTER_SEARCH))
        return target_object

    def find_data(self) -> Optional[Dict]:
        # 默认设置
        position_data = {rule["name"]: "暂无数据" for rule in self.config["查找内容"]}
        self.logger.info("初始化爬取内容")
        for rule in self.config["查找内容"]:
            name = rule["name"]
            xpath = rule["xpath"]
            find_type = rule["find_type"]
            attr_name = rule.get("attr", "")
            data_clean = rule.get("data_clean", False)
            try:
                # 查找
                if find_type == "attr":
                    data = self.driver.find_element(By.XPATH, xpath).get_attribute(attr_name)
                elif find_type == "text":
                    element = self.driver.find_element(By.XPATH, xpath)
                    data = element.text
                elif find_type == "text_list":
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    data = " ".join([x.text for x in elements]) if elements else None
                else:
                    data = None
                if data is None:
                    self.logger.warning(f"{name}未找到")
                    continue
                # 数据清洗
                if data_clean:
                    data = tools.jcqx(data)
                position_data[name] = data
            except Exception as e:
                self.logger.error(f"获取其他错误：{type(e).__name__} - {e}", exc_info=True)
                continue
        return position_data

    def save_file(self, position_data: Dict) -> None:
        fold = tools.establish_folder_path(self.config["保存文件"]["fold_name"])
        file_name = self.config["保存文件"].get("file_name")
        if self.config["保存文件"]["file_name"]:
            base_name = position_data.get(file_name, "未命名")
        else:
            base_name = position_data[self.config["查找内容"][0]["name"]]
        file = tools.wjmz(base_name + self.config["保存文件"]["file_type"])
        path = os.path.join(fold, file)
        file_path = tools.file_duplication_process(path, 1)
        with open(file_path, mode="a", encoding="utf-8") as f:
            for i, j in position_data.items():
                f.write(f"{i}: {j}\n")
            self.logger.info(f"保存{file}文件成功")

    def find_save(self) -> None:
        try:
            tools.qhwy(self.driver)
            position_data = {}
            if self.config["func"]["find_data"]:
                position_data = self.find_data()
                self.logger.info(f"爬取{position_data[self.config['查找内容'][0]['name']]}成功")
            if self.config["func"]["save_file"] and position_data:
                self.save_file(position_data)
        except Exception as e:
            self.logger.error(f"查找保存阶段错误：{type(e).__name__} - {e}")
            return None

    def work_page(self) -> Optional[List]:
        try:
            if self.config["func"]["get_to_work_page"]:
                self.get_to_work_page()
            if self.config["func"]["find_target_object"]:
                target_object = self.find_target_object()
                return target_object
            return None
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

    def preserve_wait(self, target_object: List[object]) -> None:
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
        return None

    def search_for_page_numbers(self) -> Optional[int]:
        try:
            self.logger.info("查找最大页数")
            num = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.config["爬取页数"]["pages_num"]))
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
                EC.presence_of_element_located(tools.get_by(self.config["爬取页数"]["next_btn"]))
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
            num = 1
            if self.config["func"]["search_for_page_numbers"]:
                result = self.search_for_page_numbers()
                num = result if result else 1
            for i in range(1, num + 1):
                if self.config["func"]["work_page"]:
                    target_object = self.work_page()
                    if self.config["func"]["preserve_wait"]:
                        self.preserve_wait(target_object)
                if i != num:
                    self.logger.info("下一页")
                    if self.config["func"]["next_page"]:
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
            return None