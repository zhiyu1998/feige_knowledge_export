import time
import copy

from knowledge import Knowledge

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

from utils import find_first_chinese_hit, extract_number_from_string, contains_time, remove_bubbles
from excel_io import append_rows_to_excel

# 从第几个一分类开始获取（从1开始）
START_ONE_CATEGORY = 1
# 从第几个二分类开始获取 （从0开始）
START_SECOND_TYPE = 0

if __name__ == '__main__':
    brave_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    options = webdriver.EdgeOptions()
    # options.binary_location = brave_path
    # 加载已有的用户数据目录
    options.add_argument(r"--user-data-dir=C:\Users\Administrator\AppData\Local\Microsoft\Edge\User Data")
    options.add_argument(r"--profile-directory=Default")  # 加载默认的用户配置文件

    service = webdriver.EdgeService(executable_path=r"C:\Users\Administrator\Desktop\Migration\msedgedriver.exe")

    driver = webdriver.Edge(options=options, service=service)
    # 打开网页
    driver.get('https://im.jinritemai.com/pc_seller_v2/main/setting/robot/knowledge')

    # 设置隐式等待 10 秒
    driver.implicitly_wait(10)
    # 获取分类/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/div[1]
    category = driver.find_elements(By.XPATH,
                                    '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/div')

    knowledge_only_id = 1

    for category_index, child in enumerate(category[START_ONE_CATEGORY:8], start=1):
        print(child.text)
        # 点击分类
        time.sleep(1)
        if child.is_displayed() and child.is_enabled():
            child.click()
            time.sleep(1)

        # 二级分类
        second_type_knowledge = driver.find_elements(By.XPATH,
                                                     '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[1]/div/div')
        for second_type in second_type_knowledge[START_SECOND_TYPE:]:
            if second_type.is_displayed() and second_type.is_enabled():
                second_type.click()
                time.sleep(1)

            # 自定义知识
            custom_knowledge = driver.find_element(By.XPATH,
                                                   '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[4]/div[1]/div[1]/div/label[2]').click()
            time.sleep(1)

            # 获取页面列表
            item_list = driver.find_elements(By.XPATH,
                                             '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[4]/div[2]/div/section/div')
            # 找不到数据就下一个知识
            if not item_list:
                continue
            # 获取到页末的所有按钮
            select_page = item_list[-1].find_elements(By.XPATH, "./ul/li")
            # 选择每页显示100条
            all_page_select_list = select_page[-1].find_element(By.XPATH, './div/div[1]/span[2]')
            all_page_select_list.click()
            time.sleep(1)
            # 点击每页100条
            try:
                handred_in_select_list = select_page[-1].find_element(By.XPATH,
                                                                      './div/div[2]/div/div/div/div[2]/div/div/div/div[4]')
                handred_in_select_list.click()
                time.sleep(1)

                # 获取共有多少数据
                total_data = driver.find_element(By.XPATH,
                                                 '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[4]/div[2]/div/section/span').text
                total_page_data = int(extract_number_from_string(total_data))
            except NoSuchElementException:
                # 如果元素不存在，打印日志并跳过当前循环
                print(f"当前页不存在任何元素, 即将跳过...")
                continue
            except ElementClickInterceptedException as e:
                # 处理点击被拦截的情况
                print(f"元素点击被拦截: {e}")
                # 在这里添加处理逻辑，例如等待一段时间后重试
                time.sleep(2)

            # 重置页码
            page_index = 1
            # input("调试使用，请输入任意键继续....")

            # 计算总页数 (如果没有页码就遍历一次试一下)
            total_pages = (total_page_data + 100 - 1) // 100 if total_page_data else 1

            next_page_is_available = True
            while page_index <= total_pages:
                # 每一个知识点
                knowledge_list = []

                # 重置foreach_data
                # 计算当前页的起始和结束索引
                start_index = (page_index - 1) * 100
                end_index = min(start_index + 100, total_page_data)
                current_page_data_count = end_index - start_index
                print(f"======================日志：当前页有{current_page_data_count}数据")
                # input("调试使用，请输入任意键继续....")

                for i in range(2, current_page_data_count * 2 + 2, 2):  # 假设最大到100
                    knowledge_one = Knowledge()
                    # 设置id
                    knowledge_one.id = knowledge_only_id

                    title_xpath = f'/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[4]/div[2]/div/section/div[{i}]/div[2]/div[1]/div/div[2]/span'
                    info_xpath = f'/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[4]/div[2]/div/section/div[{i}]/div[2]/div[2]'
                    editor_xpath = f'/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/div/div/div[1]/div/div/div/div[2]/div/div[1]/div[4]/div[2]/div/section/div[{i}]/div[2]/div[1]/div/div[1]/div/button[1]'
                    try:
                        # 一级知识分类
                        knowledge_one.ans_type_first = child.text
                        # 二级知识分类
                        knowledge_one.ans_type_second = second_type.text

                        # 标题
                        title_element = driver.find_element(By.XPATH, title_xpath)
                        knowledge_one.title = title_element.text + "\n"
                        # 获取其他主要问法
                        editor = driver.find_element(By.XPATH, editor_xpath).click()
                        time.sleep(1)
                        # 获取其他主要问法长度 方便下一步操作
                        editor_question_len = driver.find_element(By.XPATH,
                                                                  '/html/body/div[6]/div/div[2]/div/div/div[2]/div/form/div[3]/div[2]/div[1]/div[1]/div[1]/span')
                        editor_question_len = editor_question_len.text.split("/")[0]

                        for editor_index in range(int(editor_question_len)):
                            editor_main_question = driver.find_element(By.CSS_SELECTOR,
                                                                       f'#questionWhitelist_{editor_index}')
                            knowledge_one.title += editor_main_question.get_attribute('value') + "\n"
                            # print(editor_main_question.get_attribute('value'))
                        # 点击取消跳出其他主要问法
                        driver.find_element(By.XPATH,
                                            '/html/body/div[6]/div/div[2]/div/div/div[3]/div/div[2]/button[2]/span').click()
                        # input("点击继续（调试使用）...")

                        info_element = driver.find_element(By.XPATH, info_xpath)
                        # ./div/div[1]
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
                            ans_text_index = -1
                            ans_text_array = reply.split("\n")
                            # 获取最后一个，也就是回复
                            ans_text = ans_text_array[ans_text_index]
                            # 处理气泡问题
                            if ans_text.startswith("气泡"):
                                while ans_text.startswith("气泡"):
                                    ans_text_all = ans_text + "|" + ans_text_all
                                    ans_text_index -= 1
                                    ans_text = ans_text_array[ans_text_index]
                                # 去除ans_text_all最后一个| && 去除气泡x
                                ans_text_all = remove_bubbles(ans_text_all[:-1])
                            else:
                                ans_text_all = ans_text
                                # 如果包含视频时间就再往上层寻找
                                if contains_time(ans_text_all):
                                    ans_text_all = ans_text_array[ans_text_index - 1]

                            knowledge_item.ans_text = ans_text_all
                            if "不转人工" in reply:
                                knowledge_item.is_transfer_human = False
                                knowledge_item.ans_type = Knowledge.ANS_TYPE_TEXT
                            else:
                                knowledge_item.is_transfer_human = True
                                knowledge_item.ans_type = Knowledge.ANS_TYPE_HUMAN

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

                            if "不提醒" in reply:
                                knowledge_item.is_turn_off_light = Knowledge.IS_TURN_OFF_LIGHT
                            else:
                                knowledge_item.is_turn_off_light = Knowledge.IS_NOT_TURN_OFF_LIGHT
                            print(f"买家问法：{knowledge_item.title}")
                            print(f"回复类型：{knowledge_item.ans_type}")
                            print(f"回复内容：{knowledge_item.ans_text}")
                            print(f"命中次数：{str(knowledge_item.hits)}")
                            print(f"是否转人工：{knowledge_item.is_transfer_human}")
                            print(f"智能类型：{knowledge_item.intelligent_type}")
                            print(f"智能辅助回复方式：{knowledge_item.intelligent_reply}")
                            print(f"一级分类：{child.text}")
                            print(f"二级分类：{second_type.text}")
                            print(f"是否关灯：{knowledge_item.is_turn_off_light}")
                            print("----------------------------")
                            # 添加知识到列表
                            # input("点击继续（调试使用）...")
                            knowledge_list.append(knowledge_item)

                    except Exception as e:
                        print(f"未找到元素，停止查找: {title_xpath}, 错误信息: {e}")
                        break
                    # 知识点 + 1
                    knowledge_only_id += 1
                    # input("点击继续（调试使用）...")
                    # 这里重置是否可以下一页，driver.find_element后如果不可以下一页返回是True，可以下一页是False
                    time.sleep(1)

                # 重置index，进行下一页
                page_index += 1
                # 查看是否可以点击下一页
                next_page_is_available = not select_page[-2].find_element(By.XPATH, './button').get_attribute(
                    'disabled')
                print(f'=====================日志：是否还有下一页：{next_page_is_available}')
                # 一页一页保存到excel
                print(f"正在保存 {child.text}-{second_type.text} 类第 {page_index} 知识......")
                append_rows_to_excel('./飞鸽批量导入新增自定义知识模版.xlsx', knowledge_list, backup_interval=5)
                # input("点击继续（调试使用）...")

            print("这里即将进入下一个知识分类...")
            # input("这里即将进入第二个知识分类，点击继续（调试使用）...")
    # # 关闭浏览器
    input("完成备份，按 Enter 键关闭浏览器...")
    driver.quit()