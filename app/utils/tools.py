import datetime
import random
import string

UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')

NUMBERS = '12345679'
IMAGE_MODE = 'RGBA'
BACKGROUND_COLOR = (255, 255, 255, 0)


def get_task_number(mode):
    return "{}-{}-{}".format(mode, datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                             ''.join(random.sample(string.digits, 4)))


def iter_items(items, interval, total=None):
    """
    :param items: 要遍历的集合
    :param interval: 每次遍历的元素的数量
    :return:
    """
    if interval < 1:
        return

    start = 0
    if total is None:
        total = len(items)
    while True:
        if start >= total:
            break
        yield items[start:start + interval]
        start += interval


def now_time(seconds: int = 0) -> datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=8, seconds=seconds)


def generate_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    """Generates a non-guessable OAuth token
    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))


def generate_captcha_code(length=4):
    return ''.join([random.choice(NUMBERS) for _ in range(length)])


class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    TODO: 字典内置保留字无法复制
    """

    def __getattr__(self, name):
        # type: (str) -> Any
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        # type: (str, Any) -> None
        self[name] = value


def generate_upc(project, customer, order):
    """订单号

    Args:
        project: 项目ID[00~99]  # 同商户号多个项目
        customer: 客户ID[0000~9999]
        order: 订单ID[000,000,000~999,999,999]

    return:
        订单号里的无效0，全部用随机大写字符串替换后的字符串
        eg: G1,FV10,IMP,ORT,100

    """

    def string_fill_zero(num, length=0):
        return '{}{}'.format(''.join(random.sample(string.ascii_uppercase, length - len(str(num)))), num)

    return '{}{}{}'.format(string_fill_zero(project, 2), string_fill_zero(customer, 4), string_fill_zero(order, 9))
