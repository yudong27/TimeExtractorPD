# -*- coding=utf-8 -*-
# library: pednlp
# author: yudong27
# license: Apache License 2.0
# Email: yuu1010@qq.com
# github: https://github.com/yudong27/TimeExtractorPD
# description: Time extractor for Chinese NLP

# 很多算法是用非常复杂的正则去匹配文本，可能会有10多个，在抽取的时候不断去剪短候选项，进行匹配
# 这种方法非常耗时，效率很低，扩展性也差，出现bug不好解决
# 我们可以对正则项做一些抽象，比如数字，数字前后扩展词，扩展词的扩展词都写成类似于lex，yacc的形式

import ply.lex as lex
from ply.lex import TOKEN
import re
from .utils import *
from .timeformat import TimeFormat


class TimeLexer:
    def __init__(self, **kwargs):
        self.error_count = 0

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'
    NUMBER_PATTERN = r'(\d+|[一二三四五六七八九零〇十百千万]+)'
    IGNORE_PATTERN = '[ \t\n]*'
    WEEK_STRING = r'(周|星期|礼拜)'
    SOLAR_TERMS = ['立春','雨水','惊蛰','春分','清明','谷雨', \
                   '立夏','小满','芒种','夏至','小暑','大暑', \
                   '立秋','处暑','白露','秋分','寒露','霜降', \
                   '立冬','小雪','大雪','冬至','小寒','大寒']

    tokens_and_pattern = [
        # 某年类型
        ('YEAR_STRING', NUMBER_PATTERN+IGNORE_PATTERN+"年"),
        # 某岁类型
        ('SUI_STRING', NUMBER_PATTERN+IGNORE_PATTERN+"岁"),
        # 某月类型
        ('MONTH_STRING', NUMBER_PATTERN+IGNORE_PATTERN+"月(份)?"),
        # 某日类型
        ('DAY_STRING', NUMBER_PATTERN+IGNORE_PATTERN+"[日号]"),
        # 超级模糊类型
        ('SUPER_BLUR_TWO_YMD', '前两(天|(个)?月|年)'),
        ('SUPER_BLUR_TWO_HMS_PATTERN', '前两((个)?(小时|钟头)|分钟|秒(钟)?)'),
        # 模糊时间段
        ('BLUR_MONTH_STRING', r'(初|[一]开年|伊始|末|尾|终|底|[上下]半年|[暑寒][假期]|[前中后]期)'),
        # 模糊日类型
        ('BLUR_DAY_STRING', r'([上中下]旬|初|中|底|末)'),
        # 限定季度
        ('LIMIT_SOLAR_SEASON_STRING', r'([上下](个)?|本|这)季度[初中末]?'),
        # 皇帝年号类型
        ('REIGN_TITLE', "|".join(load_reign_title())),
        # 分隔符类型
        ('SEP_CHAR', r'[,，、和]'),
        # 24节气
        ('SOLAR_TERM_STRING', "|".join(SOLAR_TERMS)),
        # 春夏秋冬四季
        ('SEASON_STRING', r'[春夏秋冬][季天]?'),
        # 相对年
        ('LIMIT_YEAR_STRING', r'(前(一)?|今|明|去|同|当|后|大前|本|次|上(一)?|这(一)?)年'),
        # 相对月
        ('LIMIT_MONTH_STRING', r'([下上]((一)?个)?|同|本|当|次|这)月'),
        # 季度
        ('SOLOR_SEASON_STRING', r'[第前后头]?(\d+|[一二三四五六七八九零〇十百千万]+|首)(个)?季度[初中末]?'),
        # `世纪、年代`：`20世纪二十年代`
        ('CENTURY_YEAR_PATTERN',
            r'(公元(前)?)?(\d{1,2}|((二)?十)?[一二三四五六七八九]|(二)?十|上)世纪'
            r'((\d0|[一二三四五六七八九]十)年代)?([初中末](期)?|前期|后期)?|'
            r'(\d0|[一二三四五六七八九]十)年代([初中末](期)?|前期|后期)?'),
        # 范围月
        ('SPAN_MONTH', r'(([第前后头]' + NUMBER_PATTERN + r'|首)(个)?月(份)?)'),
        # 星期匹配
        ('WEEK_STRING', WEEK_STRING + NUMBER_PATTERN),
        # 星期序号匹配
        ('WEEK_SEQ_NO_STRING', '第'+ NUMBER_PATTERN + WEEK_STRING+'[一二三四五六日末天1-7]'),
        # 标准星期模式，不与年月日连着
        ('STANDARD_WEEK_DAY_PATTERN','(上上|上|下下|下|本|这)?(一)?(个)?(周)?' 
            + WEEK_STRING + '[一二三四五六日末天1-7]'),
        # 纯数字
        #('NUMBER', r'\d+'),
    ]
    # List of token names.   This is always required
    tokens = tuple(k for k,v in tokens_and_pattern)

    # Regular expression rules for simple tokens
    #literals = ['+', '-','*','/','(',')']

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)


    # Error handling rule
    def t_error(self, t):
        #print("Illegal character {}".format(t.value))
        t.lexer.skip(1)
        t.value = t.value[0]
        #t.type = "OTHER"
        offset0 = t.lexpos
        offset1 = t.lexpos + 1
        t.value = TimeFormat(t.lexer.lexdata[offset0:offset1], offset0, offset1, t.type)
        self.error_count += 1
        return t

    # Build the lexer
    def build(self,**kwargs):
        
        self.lexer = lex.lex(module=self, reflags=re.UNICODE, **kwargs)
        # Build the lexer
        # 在优化模式下执行，需要注意的是lex会被禁用大多数的错误检查。
        # 因此，建议只在确保万事俱备准备发布最终代码时使用。
        # lexer = lex.lex(optimize=1)
        return self.lexer

    # Test it output
    def test(self, data):
        if not hasattr(self, 'lexer'):
            self.build(debug=1)
        self.lexer.input(data)
        for tok in self.lexer:
            print("var_type={} tok_type={:<12} pos={:<3} lineno={:<3} value={} ".format(
                type(tok), tok.type, tok.lexpos, tok.lineno, tok.value
            ))
        print("error_count:", self.error_count)

# 动态添加函数
for k,v in TimeLexer.tokens_and_pattern:
    setattr(TimeLexer, 't_'+k, create_func(repr(v))) # repr可以不转义\t\n等，直接传给create_func

tokens = TimeLexer.tokens
timelexer = TimeLexer()
timelexer.build()
lexer = lex.lex(object=timelexer)

if __name__ == "__main__":
    import time
    # Test it out
    data = '''
        3 + 4 * 10年
        + -20 *\t2
        一三五七+234
        我们兰拉风老年康熙卡乾隆庆 佛哦哦佛山房东123-一三五
        一九九八年
        一万三千年
        12月
        12月份
        19号
    '''
    text = '''2021年中秋节前两天来大寒的我们兰拉风老年康熙八年卡乾隆庆4年 佛哦哦佛山房东123-一三五Abc13春天上旬第一二三十个季度下旬
        8月临近尾声，中秋、国庆两个假期已在眼前。2021年中秋节是9月21日，星期二。 有不少小伙伴翻看放假安排后，发现中秋节前后两个周末都要"补"假。
        记者注意到，根据放假安排，9月18日（星期六）上班，9月19日至21日放假调休，也就是从周日开始放假3天。由于中秋节后上班不到 10天，又将迎来一个黄金周—国庆长假，因此工作也就"安排"上了。
        双节来袭，仍有人要坚守岗位。加班费怎么算？记者为辛勤的小伙伴们算了一笔账。今年中秋加上国庆，两个假日加在一起共有10个加班日，如果全部加班，则可以拿到相当于24天的日工资。
        根据规定，9月21日中秋节和10月1日、2日、3日均为法定假日，用人单位安排劳动者加班工作，应按照不低于劳动者本人日或小时工资的300%支付加班工资；
        9月19日、20日和10月4日、5日、6
        日、7 日，用人单位可选择给予补休或按照不低于劳动者本人日或小时工资的200%支付加班工资。也就是说，如果10天全部加班，就可以拿到24天的日工资收入。
        人社部门提醒，当然这只是按照最低工资标准算的最低加班费，实际情况中，加班工资应该与个人实际工资挂钩。
        前两天前两分钟
        第二个季度中
        第八个星期五
        上上周星期7
        第13个月份
        '''
    text = '''2021年中秋节是9月21日，9月18日（星期六）上班，9月19日至21日放假调休，2022年9月21日中秋节和10月1日、2日、3日均为法定假日，用人单位安排劳动者加班工作，应按照不低于劳动者本人日或小时工资的300%支付加班工资；
        9月19日、20日和10月4日、5日、6日、7 日'''
    #print(text)
    #text = text*100
    r = []
    a = time.time()
    lexer.input(text)
    for tok in lexer:
        #if tok.type != 'error':
        print(tok)
        #    r.append(tok)
    b = time.time()
    print(len(text), b-a, len(r))
    #print(timelexer.error_count)