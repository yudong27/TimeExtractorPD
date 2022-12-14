
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'BLUR_DAY_STRING BLUR_MONTH_STRING CENTURY_YEAR_PATTERN DAY_STRING LIMIT_MONTH_STRING LIMIT_SOLAR_SEASON_STRING LIMIT_YEAR_STRING MONTH_STRING REIGN_TITLE SEASON_STRING SEP_CHAR SOLAR_TERM_STRING SOLOR_SEASON_STRING SPAN_MONTH STANDARD_WEEK_DAY_PATTERN SUPER_BLUR_TWO_HMS_PATTERN SUPER_BLUR_TWO_YMD WEEK_SEQ_NO_STRING WEEK_STRING YEAR_STRINGterm : termymd\n    termymd : termyear termmonth termday\n               | termmonth termday\n    termday : DAY_STRING\n            | termday SEP_CHAR DAY_STRING\n    termyear : YEAR_STRING\n                | LIMIT_YEAR_STRING\n    termmonth : MONTH_STRING\n                | BLUR_MONTH_STRING\n                | LIMIT_MONTH_STRING\n    '
    
_lr_action_items = {'YEAR_STRING':([0,],[5,]),'LIMIT_YEAR_STRING':([0,],[6,]),'MONTH_STRING':([0,3,5,6,],[7,7,-6,-7,]),'BLUR_MONTH_STRING':([0,3,5,6,],[8,8,-6,-7,]),'LIMIT_MONTH_STRING':([0,3,5,6,],[9,9,-6,-7,]),'$end':([1,2,11,12,13,15,],[0,-1,-3,-4,-2,-5,]),'DAY_STRING':([4,7,8,9,10,14,],[12,-8,-9,-10,12,15,]),'SEP_CHAR':([11,12,13,15,],[14,-4,14,-5,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'term':([0,],[1,]),'termymd':([0,],[2,]),'termyear':([0,],[3,]),'termmonth':([0,3,],[4,10,]),'termday':([4,10,],[11,13,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> term","S'",1,None,None,None),
  ('term -> termymd','term',1,'p_term_ymday','timeyacc.py',29),
  ('termymd -> termyear termmonth termday','termymd',3,'p_term_ymd','timeyacc.py',36),
  ('termymd -> termmonth termday','termymd',2,'p_term_ymd','timeyacc.py',37),
  ('termday -> DAY_STRING','termday',1,'p_term_day','timeyacc.py',55),
  ('termday -> termday SEP_CHAR DAY_STRING','termday',3,'p_term_day','timeyacc.py',56),
  ('termyear -> YEAR_STRING','termyear',1,'p_term_year','timeyacc.py',75),
  ('termyear -> LIMIT_YEAR_STRING','termyear',1,'p_term_year','timeyacc.py',76),
  ('termmonth -> MONTH_STRING','termmonth',1,'p_term_month','timeyacc.py',81),
  ('termmonth -> BLUR_MONTH_STRING','termmonth',1,'p_term_month','timeyacc.py',82),
  ('termmonth -> LIMIT_MONTH_STRING','termmonth',1,'p_term_month','timeyacc.py',83),
]
