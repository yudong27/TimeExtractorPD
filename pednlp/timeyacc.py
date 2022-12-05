# -*- coding=utf-8 -*-
# library: pednlp
# author: yudong27
# license: Apache License 2.0
# Email: yuu1010@qq.com
# github: https://github.com/yudong27/TimeExtractorPD
# description: Time extractor for Chinese NLP


import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from timelex import  tokens, timelexer


stack = []
#def p_expression_plus(p):
#    'expression : factor'
#    print(type(p))
#    #p[0] = p[1] + p[3]

#def p_factor_time(p):
#    'factor : term'
#    print(type(p))
#    #p[0] = p[1] + p[2]
        # 标准时间类型 `标准数字 年、月、日`：`2016-05-22`、`1987.12-3`, 数字-间隔符-数字-间隔符-数字
        #'STANDARD_YMD_PATTERN': r'\d+[\-./]\d+([\-./]\d+))?[ \t\u3000\-./]?|(\d+[·\-]\d+)'
def p_term_ymday(p):
    '''term : termymd
    '''
    #print(p.slice)
    p[0] = p[1]
    stack.append(p[0])

def p_term_ymd(p):
    '''termymd : termyear termmonth termday
               | termmonth termday
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 4:
        p[0] = p[1] + p[2] + p[3]
    print("term_ymd: ",p[0])
    if len(stack) == 0:
        stack.append(p[0])
    elif stack[-1].offset1 < p[0].offset0:
        stack.append(p[0])
    else:
        stack.pop()
        stack.append(p[0])
    
def p_term_day(p):
    '''termday : DAY_STRING
            | termday SEP_CHAR DAY_STRING
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 4:
        p[0] = p[1] + p[2] + p[3]
    print(p[0])
    if len(stack) == 0:
        stack.append(p[0])
    elif stack[-1].offset1 < p[0].offset0:
        stack.append(p[0])
    else:
        stack.pop()
        stack.append(p[0])
    #print(p[0])

def p_term_year(p):
    '''termyear : YEAR_STRING
                | LIMIT_YEAR_STRING
    '''
    p[0] = p[1]

def p_term_month(p):
    '''termmonth : MONTH_STRING
                | BLUR_MONTH_STRING
                | LIMIT_MONTH_STRING
    '''
    p[0] = p[1]
    print("term_month:", p[0])

# Error rule for syntax errors
def p_error(p):
    #print("Syntax error in input!")
    print("Error", p)
    #parser.restart()
    #parser.errok()

# Build the parser

parser = yacc.yacc(debug=True)

text = '''2021年中秋节是9月21日，9月18日（星期六）上班，9月19日至21日放假调休，2022年9月21日中秋节和10月1日、2日、3日均为法定假日，用人单位安排劳动者加班工作，应按照不低于劳动者本人日或小时工资的300%支付加班工资；
        9月19日、20日和10月4日、5日、6日、7 日'''
print(text)
result = parser.parse(text)
#print(result)

print(timelexer.error_count)
for i in stack:
    print(i)