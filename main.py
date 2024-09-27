import time
import copy
import logging

from knowledge import Knowledge
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException

from utils import find_first_chinese_hit, extract_number_from_string, contains_time, remove_bubbles
from excel_io import append_rows_to_excel

# 从第几个一分类开始获取（从1开始）
START_ONE_CATEGORY = 6
# 从第几个二分类开始获取 （从0开始）
START_SECOND_TYPE = 13
# 单页分页的总数据
PAGE_DATA_COUNT = 100
# 是否只完成单个模块（某个一级分类的二级分类）
IS_ONLY_ONE_MODULE = True


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 常量定义
BRAVE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
USER_DATA_DIR = r"--user-data-dir=C:\Users\Administrator\AppData\Local\Microsoft\Edge\User Data"
PROFILE_DIRECTORY = r"--profile-directory=Default"
EXECUTABLE_PATH = r"C:\Users\Administrator\Desktop\迁移\msedgedriver.exe"
URL = 'https://im.jinritemai.com/pc_seller_v2/main/setting/robot/knowledge'

# XPath前缀
XPATH_PREFIX = '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div'
# 一级知识分类
CATEGORY_XPATH = f'{XPATH_PREFIX}[2]/div/div[1]/div[1]/div/div'
# 二级知识分类
SECOND_TYPE_XPATH = f'{XPATH_PREFIX}[3]/div/div[1]/div[1]/div/div'
# 自定义知识
CUSTOM_KNOWLEDGE_XPATH = f'{XPATH_PREFIX}[4]/div[1]/div[1]/div/label[2]'
# 知识列表
ITEM_LIST_XPATH = f'{XPATH_PREFIX}[4]/div[2]/div/section/div'
# 知识总数
TOTAL_DATA_XPATH = f'{XPATH_PREFIX}[4]/div[2]/div/section/span'

def setup_driver():
    """
    设置并返回Edge浏览器驱动
    """
    options = webdriver.EdgeOptions()
    options.add_argument(USER_DATA_DIR)
    options.add_argument(PROFILE_DIRECTORY)  # 加载默认的用户配置文件

    service = webdriver.EdgeService(executable_path=EXECUTABLE_PATH)
    driver = webdriver.Edge(options=options, service=service)
    driver.implicitly_wait(10)
    return driver

def click_element(driver, xpath, timeout=10):
    """
    点击指定的元素
    """
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        return element
    except (TimeoutException, ElementClickInterceptedException) as e:
        logging.error(f"点击元素失败: {xpath}, 错误信息: {e}")
        return None

def get_elements(driver, xpath, timeout=10):
    """
    获取指定的元素列表
    """
    try:
        elements = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        return elements
    except TimeoutException as e:
        logging.error(f"获取元素失败: {xpath}, 错误信息: {e}")
        return []

def process_knowledge(driver, knowledge_only_id, child, second_type):
    """
    处理知识点并返回知识点列表
    """
    knowledge_list = []
    click_element(driver, CUSTOM_KNOWLEDGE_XPATH)
    time.sleep(1)

    item_list = get_elements(driver, ITEM_LIST_XPATH)
    if not item_list:
        return knowledge_list

    select_page = item_list[-1].find_elements(By.XPATH, "./ul/li")
    all_page_select_list = select_page[-1].find_element(By.XPATH, './div/div[1]/span[2]')
    all_page_select_list.click()
    time.sleep(1)

    try:
        handred_in_select_list = select_page[-1].find_element(By.XPATH, './div/div[2]/div/div/div/div[2]/div/div/div/div[4]')
        handred_in_select_list.click()
        time.sleep(1)

        total_data = driver.find_element(By.XPATH, TOTAL_DATA_XPATH).text
        total_page_data = int(extract_number_from_string(total_data))
    except NoSuchElementException:
        logging.warning("当前页不存在任何元素, 即将跳过...")
        return knowledge_list

    total_pages = (total_page_data + PAGE_DATA_COUNT - 1) // PAGE_DATA_COUNT if total_page_data else 1
    page_index = 1

    while page_index <= total_pages:
        start_index = (page_index - 1) * PAGE_DATA_COUNT
        end_index = min(start_index + PAGE_DATA_COUNT, total_page_data)
        current_page_data_count = end_index - start_index
        logging.info(f"当前页有 {current_page_data_count} 数据")

        for i in range(2, current_page_data_count * 2 + 2, 2):
            knowledge_one = Knowledge()
            knowledge_one.id = knowledge_only_id

            base_xpath = f'{XPATH_PREFIX}[4]/div[2]/div/section/div[{i}]'
            title_xpath = f'{base_xpath}/div[2]/div[1]/div/div[2]/span'
            info_xpath = f'{base_xpath}/div[2]/div[2]'
            editor_xpath = f'{base_xpath}/div[2]/div[1]/div/div[1]/div/button[1]'

            try:
                # 一级知识分类
                knowledge_one.ans_type_first = child.text
                # 二级知识分类
                knowledge_one.ans_type_second = second_type.text

                # 标题
                title_element = driver.find_element(By.XPATH, title_xpath)
                knowledge_one.title = title_element.text + "\n"
                click_element(driver, editor_xpath)
                time.sleep(1)

                # 获取其他主要问法长度 方便下一步操作
                editor_question_len_xpath = '/html/body/div[6]/div/div[2]/div/div/div[2]/div/form/div[3]/div[2]/div[1]/div[1]/div[1]/span'
                editor_question_len = driver.find_element(By.XPATH, editor_question_len_xpath).text.split("/")[0]

                for editor_index in range(int(editor_question_len)):
                    editor_main_question = driver.find_element(By.CSS_SELECTOR, f'#questionWhitelist_{editor_index}')
                    knowledge_one.title += editor_main_question.get_attribute('value') + "\n"

                # 点击取消跳出其他主要问法
                cancel_button_xpath = '/html/body/div[6]/div/div[2]/div/div/div[3]/div/div[2]/button[2]/span'
                click_element(driver, cancel_button_xpath)

                info_element = driver.find_element(By.XPATH, info_xpath)
                # 触发条件
                triggers = info_element.find_elements(By.XPATH, "./div/div[1]/div[1]")
                # 回复内容
                return_content = info_element.find_elements(By.XPATH, "./div/div[1]/div[2]")

                for item in range(len(triggers)):
                    # ！！！进行浅拷贝，防止出现引用问题
                    knowledge_item = copy.copy(knowledge_one)
                    trigger = triggers[item].text.replace("触发条件\n", "")
                    hits = find_first_chinese_hit(trigger)
                    knowledge_item.hits = hits

                    reply = return_content[item].text
                    ans_text_all = ""

                    for ans_text in reversed(reply.split("\n")):
                        # 如果遇到气泡
                        if ans_text.startswith("气泡"):
                            ans_text_all = ans_text + "|" + ans_text_all
                        else:
                            # 如果包含视频时间就再往上层寻找
                            ans_text_all = ans_text
                            if not contains_time(ans_text_all):
                                break
                    # 去除气泡
                    ans_text_all = remove_bubbles(ans_text_all.rstrip("|"))
                    knowledge_item.ans_text = ans_text_all
                    knowledge_item.is_transfer_human = "不转人工" not in reply
                    knowledge_item.ans_type = Knowledge.ANS_TYPE_TEXT if "不转人工" in reply else Knowledge.ANS_TYPE_HUMAN

                    if "智能辅助" in reply and "全自动" not in reply:
                        knowledge_item.intelligent_type = Knowledge.INTELLIGENT_TYPE_AUXILIARY
                    elif "全自动" in reply and "智能辅助" not in reply:
                        knowledge_item.intelligent_type = Knowledge.INTELLIGENT_TYPE_FULL
                    elif "智能辅助" in reply and "全自动" in reply:
                        knowledge_item.intelligent_type = Knowledge.INTELLIGENT_TYPE_GENERAL

                    if "智能判断" in reply:
                        knowledge_item.intelligent_reply = Knowledge.INTELLIGENT_TYPE_JUDGMENT
                    elif "仅做推荐" in reply:
                        knowledge_item.intelligent_reply = Knowledge.INTELLIGENT_TYPE_RECOMMADN
                    elif "自动发送" in reply:
                        knowledge_item.intelligent_reply = Knowledge.INTELLIGENT_TYPE_AUTO_SEND

                    knowledge_item.is_turn_off_light = Knowledge.IS_TURN_OFF_LIGHT if "不提醒" in reply else Knowledge.IS_NOT_TURN_OFF_LIGHT

                    logging.info(f"买家问法：{knowledge_item.title}")
                    logging.info(f"回复类型：{knowledge_item.ans_type}")
                    logging.info(f"回复内容：{knowledge_item.ans_text}")
                    logging.info(f"命中次数：{str(knowledge_item.hits)}")
                    logging.info(f"是否转人工：{knowledge_item.is_transfer_human}")
                    logging.info(f"智能类型：{knowledge_item.intelligent_type}")
                    logging.info(f"智能辅助回复方式：{knowledge_item.intelligent_reply}")
                    logging.info(f"一级分类：{child.text}")
                    logging.info(f"二级分类：{second_type.text}")
                    logging.info(f"是否关灯：{knowledge_item.is_turn_off_light}")
                    logging.info("----------------------------")

                    knowledge_list.append(knowledge_item)

            except Exception as e:
                logging.error(f"未找到元素，停止查找: {title_xpath}, 错误信息: {e}")
                break

            knowledge_only_id += 1
            time.sleep(1)

        page_index += 1
        next_page = select_page[-2].find_element(By.XPATH, './button')
        next_page_is_available = not next_page.get_attribute('disabled')
        logging.info(f'是否还有下一页：{next_page_is_available}')
        # 点击下一页
        if next_page_is_available:
            next_page.click()
        logging.info(f"正在保存 {child.text}-{second_type.text} 类第 {page_index} 知识......")
        append_rows_to_excel('./飞鸽批量导入新增自定义知识模版.xlsx', knowledge_list, backup_interval=5)
        time.sleep(1)

    return knowledge_list

if __name__ == '__main__':
    driver = setup_driver()
    # 打开网页
    driver.get(URL)

    # 获取分类
    category = get_elements(driver, CATEGORY_XPATH)

    knowledge_only_id = 1

    for category_index, child in enumerate(category[START_ONE_CATEGORY:8], start=1):
        logging.info(child.text)
        time.sleep(1)
        if child.is_displayed() and child.is_enabled():
            child.click()
            time.sleep(1)

        # 二级分类
        second_type_knowledge = get_elements(driver, SECOND_TYPE_XPATH)
        for second_type in second_type_knowledge[START_SECOND_TYPE:]:
            if second_type.is_displayed() and second_type.is_enabled():
                second_type.click()
                time.sleep(1)

            knowledge_list = process_knowledge(driver, knowledge_only_id, child, second_type)
            knowledge_only_id += len(knowledge_list)
            # 如果只需要一个模块，就直接退出循环
            if IS_ONLY_ONE_MODULE:
                break

        logging.info("这里即将进入下一个知识分类...")

    input("完成备份，按 Enter 键关闭浏览器...")
    driver.quit()