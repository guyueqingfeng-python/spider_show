import os
import json
from time import sleep
from random import uniform
from random import random
from typing import List, Callable, Tuple, Optional, Dict

from aiohttp.client_exceptions import ssl_errors
from selenium.webdriver.common.by import By
from selenium.webdriver.common.devtools.v143.browser import close
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


class PageNavigator(object):
    WAIT_AFTER_SEARCH: Tuple[float, ...] = (0.5, 2.0)

    def __init__(self, driver: object, config: Dict, logger: object, wait: object):
        self.logger = logger
        self.driver = driver
        self.wait = wait
        self.config_go = config

    def get_to_work_page(self) -> None:
        self.logger.info("查找搜索框")
        inputs = self.wait.until(
            EC.presence_of_element_located(tools.get_by(self.config_go["search_box"]))
        )
        sleep(uniform(*self.WAIT_AFTER_SEARCH))
        inputs.clear()
        tools.install_intervals_input()
        self.logger.info(f"输入{self.config_go['search_input']}")
        inputs.intervals_input(self.config_go["search_input"])
        sleep(uniform(*self.WAIT_AFTER_SEARCH))
        seek = self.wait.until(
            EC.presence_of_element_located(tools.get_by(self.config_go["search_btn"]))
        )
        self.logger.info("点击搜索")
        seek.click()
        sleep(uniform(*self.WAIT_AFTER_SEARCH))

    def search_for_page_numbers(self) -> Optional[int]:
        try:
            self.logger.info("查找最大页数")
            num = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.config_go["爬取页数"]["pages_num"]))
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
                EC.presence_of_element_located(tools.get_by(self.config_go["爬取页数"]["next_btn"]))
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

    def prepare_page(self) -> Optional[int]:
        self.get_to_work_page()
        return self.search_for_page_numbers()


class DataFetcher(object):
    WAIT_AFTER_SEARCH: Tuple[float, ...] = (0.5, 2.0)

    def __init__(self, driver: object, config: Dict, logger: object, wait: object):
        self.logger = logger
        self.driver = driver
        self.wait = wait
        self.config_find = config

    def find_target_object(self) -> list:
        self.logger.info("查找爬取内容")
        target_object = self.wait.until(
            EC.presence_of_all_elements_located(tools.get_by(self.config_find["scrape_list"]))
        )
        sleep(uniform(*self.WAIT_AFTER_SEARCH))
        return target_object

    def find_data(self) -> Optional[Dict]:
        # 默认设置
        position_data = {rule["name"]: "暂无数据" for rule in self.config_find}
        self.logger.info("初始化爬取内容")
        for rule in self.config_find:
            name = rule["name"]
            xpath = rule["xpath"]
            find_type = rule["find_type"]
            attr_name = rule.get("attr", "")
            data_clean = rule.get("data_clean", False)
            try:
                # 查找
                if find_type == "attr":
                    data = self.driver.find_element(tools.get_by(xpath)).get_attribute(attr_name)
                elif find_type == "text":
                    element = self.driver.find_element(tools.get_by(xpath))
                    data = element.text
                elif find_type == "text_list":
                    elements = self.driver.find_elements(tools.get_by(xpath))
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

    def work_page(self):
        target_object = self.find_target_object()
        length = len(target_object)
        for num, target in enumerate(target_object, start=1):
            target.click()
            yield self.find_data()
            tools.qhwy(self.driver)
            tools.preserve_wait()
            self.driver.close()
            tools.qhwy(self.driver)
            if num != length:
                self.logger.info("下一个职位")

class FileSaver(object):

    def __init__(self, config: Dict, logger: object):
        self.config_save = config
        self.logger = logger

    def save_file(self, position_data: Dict) -> None:
        fold = tools.establish_folder_path(self.config_save["fold_name"])
        file_name = self.config_save.get("file_name")
        base_name = position_data.get(file_name, "未命名")
        file = tools.wjmz(base_name + self.config_save["file_type"])
        path = os.path.join(fold, file)
        file_path = tools.file_duplication_process(path, 1)
        with open(file_path, mode="a", encoding="utf-8") as f:
            for i, j in position_data.items():
                f.write(f"{i}: {j}\n")
            self.logger.info(f"保存{file}文件成功")


class SpiderController(object):
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.driver = None
        self.wait = None
        self.page_navigator = None
        self.data_fetcher = None
        self.file_saver = None

    def prepare(self) -> None:
        with open(self.config_path, "r", encoding="UTF-8") as f:
            self.config = json.load(f)
        base_information = self.config
        self.logger = tools.logging_configuration(base_information["logger_name"])
        self.driver = tools.huoqu2(base_information["url"])
        if not self.driver:
            self.logger.critical("driver连接超时")
            raise RuntimeError("driver连接超时")

        self.wait = WebDriverWait(self.driver, base_information["wait"]["EC_wait"])
        self.driver.implicitly_wait(base_information["wait"]["find_element_wait"])

        self.page_navigator = PageNavigator(self.driver, self.config["找到页面"], self.logger, self.wait)
        self.data_fetcher = DataFetcher(self.driver, self.config["查找内容"], self.logger, self.wait)
        self.file_saver = FileSaver(self.config["保存文件"], self.logger)



    def run(self):
        max_page_number = self.page_navigator.prepare_page() or 1
        for page in range(1, max_page_number + 1):
            for data in self.data_fetcher.work_page():
                self.file_saver.save_file(data)
            if page != max_page_number:
                self.page_navigator.next_page()
                self.logger.info("下一页")

    def start(self):
        try:
            self.run()
        except Exception as e:
            self.logger.error(f"其他错误：{type(e).__name__} - {e}", exc_info=True)
            return None
        finally:
            self.driver.quit()
            self.logger.info("浏览器已关闭")
            return None