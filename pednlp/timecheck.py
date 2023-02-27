# -*- coding=utf-8 -*-
# library: pednlp
# author: yudong27
# license: Apache License 2.0
# Email: yuu1010@qq.com
# github: https://github.com/yudong27/TimeExtractorPD
# description: Time extractor for Chinese NLP


from .timelex import tokens,lexer
from .timeformat import TimeFormat
from .utils import register, convert_to_int
import cn2an

class TimeChecker(object):
    def __init__(self, debug=False):
        self.format_seq_max = 0 # 保存timeformat序列的最大值
        self.debug = debug
        #self.stack = []
        #self.maybe_wrong_time_format = []

    def add_time_format(self, time_format:TimeFormat):
        for tf in self.maybe_wrong_time_format:
            if tf.offset0 == time_format.offset0 and tf.offset1 == time_format.offset1:
                return
            elif tf.offset0 >= time_format.offset1 or tf.offset1 <= time_format.offset0:
                continue
            else:
                raise ValueError("offset:{}-{} has been saved".format(tf.offset0, tf.offset1))
        self.maybe_wrong_time_format.append(time_format)

    @register("YEAR_STRING")
    def c_year(self):
        tfm = self.stack[-1]
        info = convert_to_int(tfm.value[:-1].strip())
        for k,v in info.items():
            tfm.extra_info[k] = v
            if k== "val" and v > 2500:
                tfm.tips.append("年数字太大") 
                self.add_time_format(tfm)

    @register("SUI_STRING")
    def c_year(self):
        tfm = self.stack[-1]
        info = convert_to_int(tfm.value[:-1].strip())
        for k,v in info.items():
            tfm.extra_info[k] = v
            if k== "val" and v > 120:
                tfm.tips.append("年龄数字太大") 
                self.add_time_format(tfm)

    @register("MONTH_STRING")
    def c_month(self):
        tfm = self.stack[-1]
        info = convert_to_int(tfm.value[:-1].strip())
        for k,v in info.items():
            tfm.extra_info[k] = v
            if k== "val" and v > 12:
                tfm.tips.append("月份大于12") 
                self.add_time_format(tfm)

    @register("DAY_STRING")
    def c_day(self):
        tfm = self.stack[-1]
        # 特殊规则，如果只有"xx号"，前面没有月份，可能是地址
        if tfm.value[-1] == "号":
            if len(self.stack) < 2 or self.stack[-2].token_type != "MONTH_STRING":
                return
        info = convert_to_int(tfm.value[:-1].strip())
        for k,v in info.items():
            tfm.extra_info[k] = v
            if k== "val" and v > 31:
                tfm.tips.append("日期大于31") 
                self.add_time_format(tfm)

    @register("REIGN_TITLE YEAR_STRING")
    def c_reign_title(self):
        title = self.stack[-2]
        year = self.stack[-1]
        info = convert_to_int(year.value[:-1])
        year_wrong = False
        assert 'val' in year.extra_info
        for k,v in info.items():
            year.extra_info[k] = v
            if k== "val" and v > 100:
                year.tips.append("皇帝纪元数字太大") 
                year_wrong = True
            if k == 'type' and v == 'digit':
                year.tips.append("应当改成汉字格式：{}{}年".format(title.value, cn2an.an2cn(info['val'])))
                year_wrong = True
        if year_wrong:
            self.add_time_format(year)

    @register("MONTH_STRING DAY_STRING")
    def c_month_day(self):
        month = self.stack[-2]
        day = self.stack[-1]
        day_wrong = False
        assert 'val' in month.extra_info, "run c_month first"
        assert 'val' in day.extra_info, "run c_day first"
        if month.extra_info['val'] in [2]:
            if day.extra_info['val'] > 29:
                day.tips.append("2月的天数不超过29")
                day_wrong = True
        elif month.extra_info['val'] in [4,6,9,11]:
            if day.extra_info['val'] > 30:
                day.tips.append("{}月的天数不超过30".format(month.extra_info['val']))
                day_wrong = True
        if month.extra_info['type'] != day.extra_info['type']:
            day.tips.append("月份与日期数字形式不一致")
            day_wrong = True
        if day_wrong:
            self.add_time_format(day)
            
    @register("DAY_STRING SEP_CHAR DAY_STRING")
    def c_day_seqs(self):
        day1 = self.stack[-3]
        day2 = self.stack[-1]
        day_wrong = False
        assert 'type' in day1.extra_info, "run c_day first"
        assert 'type' in day2.extra_info, "run c_day first"
        if day1.extra_info["type"] != day2.extra_info["type"]:
            day_wrong = True
            day2.tips.append("和前面日期的数字形式不一致")
        if day1.value[-1] != day2.value[-1]:
            day_wrong = True
            day2.tips.append("前面用了{}，此处用了{}， 不一致".format(day1.value[-1], day2.value[-1]))
        if day1.extra_info["val"] >= day2.extra_info['val']:
            day_wrong = True
            day2.tips.append("此日期≤前面日期")
        if day_wrong:
            self.add_time_format(day2)




    def c_error(self):
        self.stack = []

    def apply(self):
        # 查看栈顶的几个元素是否符合注册结果，符合即调用对应函数
        # * 表示wild pattern, 目前的pattern不支持套嵌
        for i in range(min(register.mlen(), len(self.stack))):
            #print(self.stack)
            pl = [j.token_type for j in self.stack[-i-1:]]
            ps = " ".join(pl)
            for ks, func in register.items():
                kl = ks.split(' ')
                if len(kl) != len(pl):
                    continue
                matched = True
                for i in range(len(kl)):
                    if kl[i] == '*' or kl[i] == pl[i]:
                        continue
                    else:
                        matched = False
                        break
                if matched:
                    if self.debug:
                        print("pattern:{} func:{}".format(ps, ks))
                    func(self)

    
    def parse(self, text):
        lexer.input(text)
        self.stack = []
        self.maybe_wrong_time_format = []
        for tok in lexer:
            if self.debug:
                print(tok)
            self.stack.append(tok.value)
            if tok.type == 'error':
                self.c_error()
            else:
                self.apply()
        return self.maybe_wrong_time_format
    
    #def maybe_wrong(self):
    #    return self.maybe_wrong_time_format

