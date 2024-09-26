class Knowledge:
    # 一些常量
    ANS_TYPE_TEXT = "文字答案"
    ANS_TYPE_HUMAN = "直连人工客服"
    INTELLIGENT_TYPE_FULL = "全自动"
    INTELLIGENT_TYPE_AUXILIARY = "智能辅助"
    INTELLIGENT_TYPE_GENERAL = "通用"

    INTELLIGENT_TYPE_JUDGMENT = "智能判断"
    INTELLIGENT_TYPE_RECOMMADN = "仅做推荐"
    INTELLIGENT_TYPE_AUTO_SEND = "自动发送"

    IS_TURN_OFF_LIGHT = "灭灯"
    IS_NOT_TURN_OFF_LIGHT = "亮灯"

    def __init__(self):
        # 知识库ID
        self._id = 0
        # 买家问法
        self._title = ""
        # 答案类型
        self._ans_type = ""
        # 文字答案
        self._ans_text = ""
        # 命中次数
        self._hits = 1
        # 是否转人工客服
        self._is_transfer_human = False
        # 一级类型
        self._ans_type_first = ""
        # 二级类型
        self._ans_type_second = ""
        # 智能类型
        self._intelligent_type = ""
        # 智能回复
        self._intelligent_reply = ""
        # 是否灭灯
        self._is_turn_off_light = ""
        # 触发词
        self._triggers = ""

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def ans_type(self):
        return self._ans_type

    @ans_type.setter
    def ans_type(self, value):
        self._ans_type = value

    @property
    def ans_text(self):
        return self._ans_text

    @ans_text.setter
    def ans_text(self, value):
        self._ans_text = value

    @property
    def hits(self):
        return self._hits

    @hits.setter
    def hits(self, value):
        self._hits = value

    @property
    def is_transfer_human(self):
        return self._is_transfer_human

    @is_transfer_human.setter
    def is_transfer_human(self, value):
        self._is_transfer_human = value

    @property
    def ans_type_first(self):
        return self._ans_type_first

    @ans_type_first.setter
    def ans_type_first(self, value):
        self._ans_type_first = value

    @property
    def ans_type_second(self):
        return self._ans_type_second

    @ans_type_second.setter
    def ans_type_second(self, value):
        self._ans_type_second = value

    @property
    def intelligent_type(self):
        return self._intelligent_type

    @intelligent_type.setter
    def intelligent_type(self, value):
        self._intelligent_type = value

    @property
    def intelligent_reply(self):
        return self._intelligent_reply

    @intelligent_reply.setter
    def intelligent_reply(self, value):
        self._intelligent_reply = value

    @property
    def is_turn_off_light(self):
        return self._is_turn_off_light

    @is_turn_off_light.setter
    def is_turn_off_light(self, value):
        self._is_turn_off_light = value

    @property
    def triggers(self):
        return self._triggers

    @triggers.setter
    def triggers(self, value):
        self._triggers = value