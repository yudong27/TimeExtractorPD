# -*- coding=utf-8 -*-
# library: pednlp
# author: yudong27
# license: Apache License 2.0
# Email: yuu1010@qq.com
# github: https://github.com/yudong27/TimeExtractorPD
# description: Time extractor for Chinese NLP


from dataclasses import dataclass, field

@dataclass(repr=True, frozen=True)
class TimeFormat:
    value: str
    offset0: int
    offset1: int
    token_type: str
    extra_info: dict = field(default_factory=dict)
    tips: list = field(default_factory=list)

if __name__ == "__main__":
    a = TimeFormat("a", 0, 1, "type")
    a.extra_info['1'] = 1
    print(a)

