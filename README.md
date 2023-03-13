## 安装
```bash
cd TimeExtractorPD
pip install .
```

## 使用
```python
import pednlp
text = "淳熙200年"
result = pednlp.parse(text)
for r in result:
    print(r)
```

## 结果
> [TimeFormat(value='200年', offset0=2, offset1=6, token_type='YEAR_STRING', extra_info={'val': 200, 'type': 'digit'}, tips=['皇帝纪元数字太大', '应当改成汉字格式：淳熙二百年'])]

类似于这样，会找到每个可能的错误时间格式。列表内是TimeFormat类型，offset0和offset1是错误文本在原始文本中的位置信息，tips里是错误的原因，可以作为结果提示