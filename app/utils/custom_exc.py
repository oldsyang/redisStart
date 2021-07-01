"""

自定义异常

"""


class ResponseCode:
    SUCCESS_CODE = 2000

    SYSTEM_ERROR = 1000

    NOT_FOUND = 10002
    PWD_ERROR = 10003
    REPEAT_CUSTOMR = 20001
    PARAMS_NOT_VALID = 40001
    WEIXIN_SIGN_ERROR = 30001
    PERMISSION_DENY = 30002
    TOKEN_NOT_VALID = 40007
    ACCESS_TOKEN_ERROR = 40002

    IMAGE_VERIFY_ERROR = 40003
    SMS_TOO_FREQUENTLY = 40004
    SMS_OUT_DAILY_NUMBER_LIMIT = 40005
    SMS_MISMATCH = 40006
    NOT_AUTH = 50001

    CMS_LOGIN_ERROR = 50002
    ILLEGAL_ATTACK = 50003
    PAY_PARAM_INCORRECT = 50004
    ORDER_EXCEPTION = 50005
    ORDER_DONE = 50006
    PROJECT_PARAMS_INVALID = 50007
    REPEAT_TX = 50008
    TX_AMOUNT_NOT_ENOUGH = 50009

    TOKEN_FORMAT_VALID = 60001
    TOKEN_INVALID = 60003
    BR_API_ERROR = 70001
    VERIFY_PWD_DENY = 70002
    ORDER_REFUND_ERROR = 70003


class PostParamsError(Exception):
    def __init__(self, err_desc: str = "POST请求参数错误", field: str = ""):
        self.err_desc = err_desc
        self.field = field


class TokenAuthError(Exception):
    def __init__(self, err_desc: str = "token认证失败"):
        self.err_desc = err_desc


class UserTokenError(Exception):
    def __init__(self, err_desc: str = "用户认证异常"):
        self.err_desc = err_desc


class UserNotFound(Exception):
    def __init__(self, err_desc: str = "没有此用户"):
        self.err_desc = err_desc


class WxErrorFound(Exception):
    def __init__(self, err_desc: str = "微信服务器连接失败"):
        self.err_desc = err_desc


class Error(Exception):
    def __init__(self, code: int = ResponseCode.SYSTEM_ERROR, message: str = "微信服务器连接失败"):
        self.message = message
        self.code = code
