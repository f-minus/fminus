# coding=utf-8


class ListVariableAlphaError(Exception):
    """
    # list变量名字符错误，例如x1-y6
    """


class ListVariableNumError(Exception):
    """
    # list变量名数字错误，例如y6-y1
    """
