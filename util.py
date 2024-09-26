import re  # 创建一个字典，将汉字数字映射到阿拉伯数字

hanzi_to_arabic = {
    "零": "0",
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9"
}


# 定义一个函数，将汉字数字转换为阿拉伯数字
def convert_hanzi_to_arabic(hanzi_num):
    return ''.join(hanzi_to_arabic[char] for char in hanzi_num)


# 定义一个函数，从字符串中提取汉字数字并转换
def extract_and_convert(text):
    # 使用正则表达式匹配汉字数字
    match = re.search(r'[零一二三四五六七八九]+', text)
    if match:
        hanzi_num = match.group(0)
        arabic_num = convert_hanzi_to_arabic(hanzi_num)
        return arabic_num
    return None


# 中文数字字典
chinese_num_dict = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
}

# 正则表达式模式
pattern = r"第([\u4e00-\u9fff]+)次命中"


def find_chinese_hits(text):
    """
    查找并返回文本中所有“第x次命中”的匹配项，其中x是中文数字。

    :param text: 输入的文本
    :return: 包含所有匹配项的列表
    """
    matches = re.findall(pattern, text)
    result = []
    for match in matches:
        if match in chinese_num_dict:
            result.append(f"第{chinese_num_dict[match]}次命中")
    return result


def find_first_chinese_hit(text):
    """
    查找并返回文本中第一个“第x次命中”的匹配项，其中x是中文数字。

    :param text: 输入的文本
    :return: 第一个匹配项的字符串，如果没有匹配项则返回 None
    """
    match = re.search(pattern, text)
    if match:
        chinese_num = match.group(1)
        if chinese_num in chinese_num_dict:
            return f"第{chinese_num_dict[chinese_num]}次命中"
    return None


def extract_number_from_string(text):
    # 使用正则表达式匹配数字
    match = re.search(r'\d+', text)
    if match:
        return match.group()
    else:
        return None


def contains_time(text):
    # 定义时间格式的正则表达式
    time_pattern = r'\b\d{2}:\d{2}\b'

    # 使用re.search()方法来查找匹配的时间格式
    match = re.search(time_pattern, text)

    # 如果找到匹配的时间格式，返回True，否则返回False
    return bool(match)


def remove_bubbles(text):
    # 使用正则表达式匹配并删除 "气泡x" 部分
    result = re.sub(r'气泡\d+', '', text)
    return result