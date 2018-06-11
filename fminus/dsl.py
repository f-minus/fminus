# coding=utf-8
import pyparsing as pp
from .exceptions.dsl import ListVariableAlphaError, ListVariableNumError
from .settings.dsl import FILE_STRING, DEFAULT_LAM_VAL, DEFAULT_FIRST_LAM_VAL


def suppress_kw(s):
    return pp.Suppress(pp.CaselessKeyword(s))


def var_hyphen_to_list(s, l, t):
    # 解析y1-y10
    start_alpha, start_num = t[0][0], int(t[0][1])
    end_alpha, end_num = t[1][0], int(t[1][1])
    if start_alpha != end_alpha:
        raise ListVariableAlphaError
    if start_num >= end_num:
        raise ListVariableNumError
    return ['{0}{1}'.format(start_alpha, i) for i in range(start_num, end_num + 1)]


def model_var_hyphen_to_list(s, l, t):
    new_list = []
    if not isinstance(t[-1], str):
        if t[-1][0] == '*':
            has_free = True
        elif t[-1][0] == '@':
            has_free = False
        val = t[-1][1] if len(t[-1]) == 2 else DEFAULT_LAM_VAL
        for each_t in t[:-1]:
            new_list.append({
                'name': each_t,
                'free': has_free,
                'value': val
            })
    else:
        for each_t in t:
            new_list.append({
                'name': each_t
            })
    return new_list


def model_var_to_dt(s, l, t):
    token = t[0]
    if len(token) == 2:
        if token[1][0] == '*':
            has_free = True
        elif token[1][0] == '@':
            has_free = False
        val = token[1][1] if len(token[1]) == 2 else DEFAULT_LAM_VAL
        return [{'name': token[0], 'value': val, 'free': has_free}]
    else:
        return [{'name': token[0]}]


def to_float(s, l, t):
    return [float(t[0])]


def to_check_n_set_fix(s, l, t):
    has_fix = False
    for i, each_t in enumerate(t[::-1]):
        if 'free' in each_t and not each_t['free']:
            has_fix = True
        if 'free' not in each_t and i != (len(t) - 1):
            each_t['free'] = True
            each_t['value'] = DEFAULT_LAM_VAL
        if 'free' not in each_t and i == (len(t) - 1) and not has_fix:
            each_t['free'] = False
            each_t['value'] = DEFAULT_FIRST_LAM_VAL
        if 'free' not in each_t and i == (len(t) - 1) and has_fix:
            each_t['free'] = True
            each_t['value'] = DEFAULT_LAM_VAL
    return t


# 通用符号
COLON = pp.Suppress(":").setName(':')
SEMI = pp.Suppress(";").setName(';')
HYPHEN = pp.Suppress("-").setName('-')
COMMA = pp.Suppress(",").setName(',')
STAR = pp.Literal('*')
AT = pp.Literal('@')

# 定义实数
point = pp.Literal('.')
number = pp.Word(pp.nums)
real = pp.Combine(number + pp.Optional(point + number)).setParseAction(to_float)

# file配置
DATA_KW = suppress_kw('data')
FILE_KW = suppress_kw('file')
IS_KW = suppress_kw('is')
FILE_NAME = pp.Word(FILE_STRING).setName('file_name').setResultsName('file_name')
DATA = (DATA_KW + COLON + FILE_KW + IS_KW + FILE_NAME + SEMI).setName('data').setResultsName('data')

# 变量配置
FREE = pp.Group(STAR + pp.Optional(real))
FIX = pp.Group(AT + pp.Optional(real))
FREE_OR_FIX = pp.Optional(FREE ^ FIX)
VARIABLE = pp.Word(pp.alphanums)
MODEL_VARIABLE = pp.Group(VARIABLE + FREE_OR_FIX).setParseAction(model_var_to_dt)
# 带-的变量，例如y1-y10, y1-y10*
VARIABLE_POSTFIX_NUM = pp.Group(pp.Word(pp.alphas) + pp.Word(pp.nums))
LIST_VARIABLE = (VARIABLE_POSTFIX_NUM + HYPHEN + VARIABLE_POSTFIX_NUM).setParseAction(var_hyphen_to_list)
MODEL_LIST_VARIABLE = (LIST_VARIABLE + FREE_OR_FIX).setParseAction(model_var_hyphen_to_list)
VARIABLE_OR_LIST = VARIABLE ^ LIST_VARIABLE
VARIABLES = VARIABLE_OR_LIST + pp.ZeroOrMore(COMMA + VARIABLE_OR_LIST)
MODEL_VARIABLE_OR_LIST = MODEL_VARIABLE ^ MODEL_LIST_VARIABLE
MODEL_VARIABLES = MODEL_VARIABLE_OR_LIST + pp.ZeroOrMore(COMMA + MODEL_VARIABLE_OR_LIST)

# 观察变量配置
VARIABLE_KW = suppress_kw('variable')
NAMES_KW = suppress_kw('names')
ARE_KW = suppress_kw('are')
OBSERVED_VARIABLE = (VARIABLE_KW +
                     COLON +
                     NAMES_KW +
                     ARE_KW +
                     VARIABLES.setResultsName('observed') +
                     SEMI).setName('observed_variable').setResultsName('observed_variable')

# 模型配置
MODEL_KW = suppress_kw('model')
BY = suppress_kw('by')
FACTOR_BY = (VARIABLE.setResultsName('latent') +
             BY +
             MODEL_VARIABLES.setResultsName('observes').setParseAction(to_check_n_set_fix) +
             SEMI).setResultsName('factor_by', True)
ON = suppress_kw('on')
REGRESSION_ON = (VARIABLE.setResultsName('latent') +
                 ON +
                 MODEL_VARIABLES.setResultsName('latents') +
                 SEMI).setResultsName('regression_on', True)
WITH = suppress_kw('w')
CORR_WITH = pp.Group(VARIABLE + WITH + VARIABLE) + SEMI
MODEL = (MODEL_KW +
         COLON +
         pp.OneOrMore(FACTOR_BY ^ REGRESSION_ON) +
         pp.ZeroOrMore(CORR_WITH)
         ).setName('model').setResultsName('model')


# 注释
COMMENT = pp.Literal('!') + pp.restOfLine


LAN = OBSERVED_VARIABLE & DATA & MODEL
LAN.ignore(COMMENT)
