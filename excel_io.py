import pandas as pd
import os
from datetime import datetime

from knowledge import Knowledge

def knowledge_to_new_row(knowledge):
    return {
        '知识编号': knowledge.id,
        '买家问法': knowledge.title,
        '答案类型': knowledge.ans_type,
        '文字答案': knowledge.ans_text,
        '图片答案': None,
        '绑定商品': None,
        '关联订单状态': None,
        '关联时效': None,
        '命中次数': knowledge.hits,
        '是否发送转人工入口': '是' if knowledge.is_transfer_human else '否',
        '一级知识分类': knowledge.ans_type_first,
        '二级知识分类': knowledge.ans_type_second,
        '区分全自动/智能辅助': knowledge.intelligent_type,
        '智能辅助回复方式': knowledge.intelligent_reply,
        '自动回复是否灭灯': knowledge.is_turn_off_light,
        '精准关键词': knowledge.triggers,
        '答案关联知识id': None
    }

def append_rows_to_excel(file_path, knowledge_list, backup_interval=5):
    # 尝试读取现有的 Excel 文件，如果没有则创建一个新的 DataFrame
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        # 如果文件不存在，创建一个新的 DataFrame 并写入文件
        df = pd.DataFrame(columns=[
            '知识编号', '买家问法', '答案类型', '文字答案', '图片答案', '绑定商品', '关联订单状态', '关联时效',
            '命中次数', '是否发送转人工入口', '一级知识分类', '二级知识分类', '区分全自动/智能辅助', '智能辅助回复方式',
            '自动回复是否灭灯', '精准关键词', '答案关联知识id'
        ])
        df.to_excel(file_path, index=False)

    # 记录初始 DataFrame 的长度
    initial_length = len(df)

    # 将 Knowledge 对象解构为 new_row 并添加到 DataFrame
    for knowledge in knowledge_list:
        new_row = knowledge_to_new_row(knowledge)
        df.loc[len(df)] = new_row

    # 保存更新后的 DataFrame 到 Excel 文件
    df.to_excel(file_path, index=False)
    # print(str((len(df) - initial_length) % backup_interval))
    # 检查是否需要保存备份文件
    if (len(df) - initial_length) >= backup_interval:
        # 检查并创建 ./backup 文件夹
        backup_folder = './backup'
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        # 生成备份文件路径
        backup_file_path = f"{backup_folder}/{os.path.splitext(os.path.basename(file_path))[0]}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(backup_file_path, index=False)
        print(f"备份文件已保存到: {backup_file_path}")

def _test_feishu():
    df = pd.read_excel("./飞鸽批量导入新增自定义知识模版.xlsx")

    # 获取列标题
    column_titles = df.columns

    print(column_titles)

    new_row = {
        '知识编号': '12345',
        '买家问法': '如何退货',
        '答案类型': '文字',
        '文字答案': '请联系客服进行退货',
        '图片答案': None,
        '绑定商品': '商品A',
        '关联订单状态': '已完成',
        '关联时效': '7天',
        '命中次数': 10,
        '是否发送转人工入口': '是',
        '一级知识分类': '售后',
        '二级知识分类': '退货',
        '区分全自动/智能辅助': '全自动',
        '智能辅助回复方式': '自动回复',
        '自动回复是否灭灯': '否',
        '精准关键词': '退货',
        '答案关联知识id': '54321'
    }

    df.loc[len(df)] = new_row

    print(df)
    df.to_excel('updated_file.xlsx', index=False)

if __name__ == '__main__':
    knowledge1 = Knowledge()
    knowledge1.id = 12345
    knowledge1.title = "如何退货"
    knowledge1.ans_type = Knowledge.ANS_TYPE_TEXT
    knowledge1.ans_text = "请联系客服进行退货"
    knowledge1.hits = 10
    knowledge1.is_transfer_human = True
    knowledge1.ans_type_first = "售后"
    knowledge1.ans_type_second = "退货"
    knowledge1.intelligent_type = Knowledge.INTELLIGENT_TYPE_FULL
    knowledge1.intelligent_reply = Knowledge.INTELLIGENT_TYPE_AUTO_SEND
    knowledge1.is_turn_off_light = Knowledge.IS_NOT_TURN_OFF_LIGHT
    knowledge1.triggers = "退货"

    knowledge2 = Knowledge()
    knowledge2.id = 67890
    knowledge2.title = "如何换货"
    knowledge2.ans_type = Knowledge.ANS_TYPE_TEXT
    knowledge2.ans_text = "请联系客服进行换货"
    knowledge2.hits = 5
    knowledge2.is_transfer_human = True
    knowledge2.ans_type_first = "售后"
    knowledge2.ans_type_second = "换货"
    knowledge2.intelligent_type = Knowledge.INTELLIGENT_TYPE_FULL
    knowledge2.intelligent_reply = Knowledge.INTELLIGENT_TYPE_AUTO_SEND
    knowledge2.is_turn_off_light = Knowledge.IS_NOT_TURN_OFF_LIGHT
    knowledge2.triggers = "换货"

    # 调用函数，传入一个包含多个 Knowledge 对象的列表
    append_rows_to_excel('./飞鸽批量导入新增自定义知识模版.xlsx', [knowledge1, knowledge2], backup_interval=1)