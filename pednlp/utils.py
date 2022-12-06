# -*- coding=utf-8 -*-
# library: pednlp
# author: yudong27
# license: Apache License 2.0
# Email: yuu1010@qq.com
# github: https://github.com/yudong27/TimeExtractorPD
# description: Time extractor for Chinese NLP

import cn2an    
import json
import os
from ply.lex import TOKEN
from functools import wraps
from .timeformat import TimeFormat
from types import FunctionType


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
GRAND_DIR_PATH = os.path.dirname(DIR_PATH)

code_template = '''
def foo(self, t):
    {}
    offset0 = t.lexpos
    offset1 = t.lexpos + len(t.value)
    #print(t)
    t.value = TimeFormat(t.lexer.lexdata[offset0:offset1], offset0, offset1, t.type)
    return t
'''

def create_func(doc_string):
    foo_code = compile(code_template.format(doc_string), "<string>", "exec")
    foo_func = FunctionType(foo_code.co_consts[0], globals(), "foo")
    return foo_func

'''
# 废弃
def MAKEFUNC(func):
    @wraps(func)
    def wrapper(self, t):
        #func()
        offset0 = t.lexpos
        offset1 = t.lexpos + len(t.value)
        t.value = TimeFormat([t.lexer.lexdata[offset0:offset1]], offset0, offset1, [t.type])
        return t
        
    return wrapper
'''


def convert_to_int(s):
    try:
        val = int(s)
        return {"val": val, "type":"digit"}
    except:
        pass
    try:
        val = cn2an.cn2an(s, mode='smart')
        return {"val": val, "type": "cn"}
    except:
        pass
    raise ValueError("{} can not be converted to integer".format(s))

def load_reign_title():
    reign_title = {}
    path = os.path.join(DIR_PATH, "data", "china_reign_title.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    return data.keys()


class Register(dict):
    def __init__(self, *args, **kwargs):
        super(Register, self).__init__(*args, **kwargs)
        self._dict = {}
        self.param_max_length = 0
    
    def register(self, param, target):
        def add_register_item(key, value):
            if not callable(value):
                raise Exception(f"register object must be callable! But receice:{value} is not callable!")
            if key in self._dict:
                print(f"warning: \033[33m{value.__name__} has been registered before, so we will overriden it\033[0m")
                raise ValueError("Error registering")
            self[key] = value
            return value

        if callable(target):            # 如果传入的目标可调用，说明之前没有给出注册名字，我们就以传入的函数或者类的名字作为注册名
            return add_register_item(param, target)
        else:                           # 如果不可调用，说明额外说明了注册的可调用对象的名字
            return lambda x : add_register_item(target, x)
    
    def __call__(self, param):
        assert isinstance(param, str), "param must be a string"
        self.param_max_length = max(self.param_max_length, len(param.split()))
        def wrap(func):
            return self.register(param, func)
        return wrap
    
    def __setitem__(self, key, value):
        self._dict[key] = value

    def __getitem__(self, key):
        return self._dict[key]
    
    def __contains__(self, key):
        return key in self._dict
    
    def __str__(self):
        return str(self._dict)
    
    def keys(self):
        return self._dict.keys()
    
    def values(self):
        return self._dict.values()
    
    def items(self):
        return self._dict.items()
    
    def mlen(self):
        return self.param_max_length

register = Register()

def register_test():
    @register("ADD")
    def add(a : int, b : int):
        return a + b

    @register("my multiply")
    def multiply(a : int, b : int):
        return a * b

    @register
    def minus(a : int, b : int):
        return a - b

    print(register_functions)
    print(register_functions["ADD"](1, 2))

if __name__ == "__main__":
    import cProfile
    cProfile.run("cn2an.cn2an('一九九八', mode='smart')")