import json

import logging
import time
import requests
import os
import hashlib
from typing import List, Callable, Tuple, Optional, Dict
import re
import random

from lxml import etree
import pandas as pd
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException
)

logger = logging.getLogger("tool")


def bass_logging():
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)


def logging_configuration(name, level=logging.INFO, error=True, log_dir="logging", fmt=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.handlers:
        return logger
    log_dir = establish_folder_path(log_dir)
    log_file = os.path.join(log_dir, f"{name}.log")
    normal_handler = logging.FileHandler(log_file, encoding="UTF-8")
    console = logging.StreamHandler()
    if fmt is None:
        fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s'
        )
    normal_handler.setFormatter(fmt)
    console.setFormatter(fmt)
    normal_handler.setLevel(level)
    console.setLevel(level)
    logger.addHandler(normal_handler)
    logger.addHandler(console)
    logger.info("日志已开启")

    def add_error_handler():
        log_file = os.path.join(log_dir, f"error{name}.log")
        error_handler = logging.FileHandler(log_file, encoding="UTF-8")
        error_handler.setFormatter(fmt)
        error_handler.setLevel(logging.WARNING)
        logger.addHandler(error_handler)
        logger.info("错误日志已开启")

    if error:
        add_error_handler()
        return logger


def huoqu1(url, tim=3, picture=False, custom_headers=None):
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    if custom_headers:
        default_headers.update(custom_headers)
    with requests.Session() as session:
        session.headers.update(default_headers)
        for i in range(tim):
            try:
                logger.info(f"开始进行请求:{url}")
                response = session.get(url, timeout=(3, 9))
                logger.info(f"请求成功:{url}")
                response.raise_for_status()
                if not picture:
                    return etree.HTML(response.text)
                else:
                    return response.content

            except requests.exceptions.RequestException as e:
                logger.warning("错误：{}".format(e), exc_info=True)
                if i < (tim - 1):
                    time.sleep(4)
                else:
                    logger.error("尝试{}次放弃".format(tim))
                    return None
        return None


def huoqu2(url, tim=3, lazy=0, yes=0):
    """
    count = 请求次数
    lazy_loading: 0 = 禁止懒加载, 2 = 懒加载
    headless: 0 = 不是无头, 1 = 无头
    """
    options = Options()
    if yes:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-blink-features=AutomationControlled')
    prefs = {
        "profile.managed_default_content_settings.images": lazy,
        'profile.managed_default_content_settings.stylesheets': 0,
        'profile.managed_default_content_settings.javascript': 0,
        'profile.managed_default_content_settings.popups': 2,
        'profile.managed_default_content_settings.notifications': 2
    }
    options.add_experimental_option('prefs', prefs)
    service = Service(ChromeDriverManager().install())
    for i in range(tim):
        try:
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("浏览器已打开")
            driver.set_page_load_timeout(20)
            break
        except WebDriverException as e:
            logger.warning("浏览器连接超时：{}".format(e))
            if i < (tim - 1):
                time.sleep(4)
            else:
                logger.error("尝试{}次放弃".format(tim))
                return None
    for i in range(tim):
        try:
            logger.info(f"开始进行请求网址:{url}")
            driver.get(url)
            logger.info(f"请求网址成功:{url}")
            return driver
        except WebDriverException as e:
            logger.warning("网址请求超时：{}".format(e), exc_info=True)
            if i < (tim - 1):
                driver.quit()
                time.sleep(4)
            else:
                logger.error("尝试{}次放弃".format(tim))
                driver.quit()
                return None


def jcqx(shuju):
    if isinstance(shuju, str):
        return " ".join(shuju.split())
    elif isinstance(shuju, list):
        liebiao = [jcqx(itme) for itme in shuju if itme and str(itme).strip()]
        return " ".join(liebiao)
    return str(shuju).strip()


def wjmz(filename):
    filename = filename.replace('..', '')
    file = re.sub(r'[<>:"/\\\'|?*]', '_', filename)
    file = file.strip().rstrip('.')
    name_part = file.split('.')[0].upper()
    if name_part in ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3',
                     'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                     'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']:
        logger.info(f"含有特殊名字{name_part}")
        file = '_' + file
    if not file:
        logger.info("文件名为空，使用默认名'unnamed'")
        return 'unnamed'
    return file


def shru(css, hua):
    hua = list(hua)
    while hua:
        i = hua.pop(0)
        css.send_keys(i)
        if not hua:
            break
        else:
            if '\u4e00' <= hua[0] <= '\u9fff':
                time.sleep(random.uniform(0.5, 2.0))
            elif 'a' <= hua[0].lower() <= 'z':
                time.sleep(random.uniform(0.1, 0.5))
            else:
                time.sleep(random.uniform(0.2, 0.8))


def install_intervals_input():
    if hasattr(WebElement, 'intervals_input'):
        logger.info("已有方法intervals_input")
        return

    def intervals_input(self, sentence):
        sentence = list(sentence)
        while sentence:
            i = sentence.pop(0)
            self.send_keys(i)
            if not sentence:
                break
            else:
                if '\u4e00' <= sentence[0] <= '\u9fff':
                    time.sleep(random.uniform(0.5, 2.0))
                elif 'a' <= sentence[0].lower() <= 'z':
                    time.sleep(random.uniform(0.1, 0.5))
                else:
                    time.sleep(random.uniform(0.2, 0.8))

    WebElement.intervals_input = intervals_input
    logger.info("添加intervals_input方法成功")


def qhwy(driver):
    i = driver.window_handles
    driver.switch_to.window(i[-1])
    logger.info("已切换句柄致最新页面")


class RuntimeError(Exception):
    def __init__(self, value):
        self.value = value


class NopathError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.message


def establish_folder_path(name):
    path = [
        ("D盘", r"D:\pycharm"),
        ("桌面文件夹", os.path.expanduser(r"~\Desktop\args, kwargs")),
        ("程序目录", os.path.dirname(__file__))
    ]
    for i, l in path:
        try:
            if os.access(l, os.W_OK):
                os.makedirs(l, exist_ok=True)
                try:
                    ise = shutil.disk_usage(l)
                    free_gb = ise.free / (1024 ** 3)
                    if free_gb <= 0.1:
                        logger.warning(f"{i}磁盘空间不足, 还有{free_gb:.2f}GB")
                        continue
                except Exception as e:
                    logger.warning(f"未知错误：{type(e).__name__} - {e}", exc_info=True)
                    continue
                fold = os.path.join(l, name)
                os.makedirs(fold, exist_ok=True)
                logger.info(f"写入{i}路径文件夹")
                return fold
            else:
                logger.warning(f"{i}无写入权限")
        except Exception as e:
            logger.warning(f"未知错误：{type(e).__name__} - {e}", exc_info=True)
            continue
    logger.warning("目前适合路径都不可用")
    end = os.getcwd()
    logger.info(f"使用{end}")
    try:
        if os.access(end, os.W_OK):
            ise = shutil.disk_usage(end)
            free_gb = ise.free / (1024 ** 3)
            if free_gb <= 0.1:
                logger.warning(f"{end}磁盘空间不足, 还有{free_gb:.2f}GB")
                logger.error("目前文件内存没有空余")
                raise NopathError("目前文件内存没有空余")
            logger.info(f"写入{end}路径文件夹")
            return os.path.join(end, name)
        else:
            logger.warning(f"运行目录无写入权限")
    except Exception as e:
        logger.warning(f"未知错误：{type(e).__name__} - {e}", exc_info=True)
    logger.error("目前无写入文件权限")
    raise NopathError("目前无写入文件权限")


def wait_page_form(wait, by, value, max_attempts):
    """
        等待容器加载
        :param wait: WebDriverWait对象
        :param by: By.ID, By.CLASS_NAME, By.XPATH 等
        :param value: 定位值
        :param max_attempts: 最大尝试次数
        """
    for i in range(1, max_attempts + 1):
        try:
            logger.info("等待页面加载")
            wait.until(
                EC.presence_of_element_located((by, value))
            )
            logger.info("页面加载成功")
            return True
        except TimeoutException as e:
            logger.warning(f"第{i}次加载超时")
            if i < max_attempts:
                time.sleep(4)
            else:
                logger.error(f"尝试{i}次后放弃")
        except Exception as e:
            logger.warning(f"获取其他错误：{type(e).__name__} - {e}", exc_info=True)
    logger.error("页面加载错误")
    raise NoSuchElementException("页面加载错误")


def get_by(config):
    by_map = {
        "id": By.ID,
        "class_name": By.CLASS_NAME,
        "xpath": By.XPATH,
        "name": By.NAME,
        "css": By.CSS_SELECTOR,
        "tag_name": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
    }

    by_type = by_map.get(config["by"])
    if not by_type:
        raise ValueError(f"不支持的定位方式: {config['by']}")
    return by_type, config["value"]


def preserve_wait(
        wait_normally: Tuple[float, ...] = (5.0, 9.0),
        wait_long: Tuple[float, ...] = (15.0, 25.0),
        wait_quick: Tuple[float, ...] = (3.0, 5.0)
):
    wait_time = random.random()
    lose_interest = 0.2
    # 0.3比0.2大0.1实际上就是0.1
    interest = 0.3
    # 剩下的0.7为正常时间
    if wait_time < lose_interest:
        time.sleep(random.uniform(*wait_quick))
    elif wait_time < interest:
        time.sleep(random.uniform(*wait_long))
    else:
        time.sleep(random.uniform(*wait_normally))


def file_duplication_process(path, start_num=1):
    fold = os.path.dirname(path)
    file = os.path.basename(path)
    name, ext = os.path.splitext(file)
    file = f"{name}.{start_num}{ext}"
    path1 = os.path.join(fold, file)
    if os.path.exists(path1):
        path = path1
    elif os.path.exists(path):
        os.rename(path, path1)
        path = path1
    while True:
        if not os.path.exists(path):
            logger.info(f"存入{file}文件")
            return path
        else:
            name, ext = os.path.splitext(file)
            versions = int(name.split(".")[-1])
            versions += 1
            name = "".join(name.split(".")[:-1])
            file = f"{name}.{versions}{ext}"
            path = os.path.join(fold, file)


def save_excel(data, file_path, sheet_name="Sheet1", excel="csv"):
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, list) and all(isinstance(itme, dict) for itme in data):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError(logger.error(f"数据类型错误，不支持:{type(data)}"))
    if excel == "csv":
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
    elif excel == "xlsx":
        df.to_excel(file_path, index=False, sheet_name=sheet_name)
    else:
        raise ValueError(logger.error(f"参数输入错误, 不是可储存文件类型"))
    return None


def save_txt(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:

        def save(data, f, indent_level=0):
            indent = "    " * indent_level

            if isinstance(data, dict):
                for key, value in data.items():
                    f.write(f"{indent}{key}:\n")
                    if isinstance(value, (dict, list)):
                        save(value, f, indent_level + 1)
                    else:
                        if value is None:
                            f.write(f"None\n")
                        else:
                            f.write(f"{value}\n")

            elif isinstance(data, list):
                if not data:
                    f.write("None\n")
                else:
                    for content in data:
                        if isinstance(content, (dict, list)):
                            save(content, f, indent_level)
                        else:
                            f.write(f"{indent}- {content}\n")
            elif isinstance(data, str):
                f.write(f"{indent}{data}\n")

            elif data is None:
                f.write(f"None\n")

            else:
                f.write(f"{indent}{data}\n")

        save(data, f)
    return None


def save_binary(data, file_path):
    with open(file_path, "wb") as f:
        f.write(data)


def save_json(data, file_path):
    if isinstance(data, dict) or (isinstance(data, list) and all(isinstance(item, dict) for item in data)):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError(logger.error(f"数据类型错误，不支持:{type(data)}"))


def file_save_type(data, file_path, file_type: str = "txt", sheet_name="Sheet1"):
    file_type_list = ["csv", "txt", "jnp", "log", "xlsx", "json"]
    file_type = file_type.lower()
    if file_type in file_type_list:
        if file_type == "csv":
            save_excel(data, file_path, excel="csv")
        elif file_type in ("txt", "log"):
            save_txt(data, file_path)
        elif file_type == "jnp":
            save_binary(data, file_path)
        elif file_type == "xlsx":
            save_excel(data, file_path, sheet_name, excel="xlsx", )
        elif file_type == "json":
            save_json(data, file_path)
        else:
            raise ValueError(f"不支持的格式: {file_type}")


def ljcd(path):
    path = os.path.normpath(path)
    path = os.path.abspath(path)
    if len(path) >= 250:
        pathl = os.path.dirname(path)
        pathw = os.path.basename(path)
        name, ext = os.path.splitext(pathw)
        filename = hashlib.md5(pathw.encode()).hexdigest()[:8]
        if ext.lower() in [".jpg", ".jpeg", ".png"]:
            nfilename = f"book_pic_{filename}.jpg"
        elif ext.lower() == ".txt":
            nfilename = f"book_info_{filename}.txt"
        elif ext:
            nfilename = f"file_{filename}{ext}"
        else:
            nfilename = f"file_{filename}"
        npath = os.path.join(pathl, nfilename)
        return npath
    else:
        return path


def mllj(path):
    path = os.path.normpath(path)
    path = os.path.abspath(path)
    if len(path) >= 200:
        pathl = os.path.dirname(path)
        pathw = os.path.basename(path)
        filename = hashlib.md5(pathw.encode()).hexdigest()[:6]
        dfilename = os.path.join(pathl, filename)
        return dfilename
    else:
        return path