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
    def __init__(self):
        self.format_seq_max = 0 # 保存timeformat序列的最大值
        self.stack = []
        self.maybe_wrong_time_format = []

    def add_time_format(self, time_format:TimeFormat):
        for tf in self.maybe_wrong_time_format:
            if tf.offset0 == time_format.offset0 and tf.offset1 == time_format.offset1:
                break
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
                    func(self)

    
    def parse(self, text):
        lexer.input(text)
        for tok in lexer:
            self.stack.append(tok.value)
            if tok.type == 'error':
                self.c_error()
            else:
                self.apply()
        return self.maybe_wrong_time_format
    
    #def maybe_wrong(self):
    #    return self.maybe_wrong_time_format

if __name__ == "__main__":
    text = '''20211年中秋节是15 月31日，九月18日（星期六）上班，
        9月19日至21日放假调休，2022年9月21日中秋节和10月1日、2日、3日均为法定假日，
        用人单位安排劳动者加班工作，应按照不低于劳动者本人日或小时工资的300%支付加班工资
        正德20000年隆庆二年彭祖800岁
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
    import time
    #text = text*100
    print(len(text))
    time_checker = TimeChecker()
    #print(register)
    a = time.time()
    r = time_checker.parse(text)
    b = time.time()
    print("TIME:", b-a)
    for k in r:
        print(k)