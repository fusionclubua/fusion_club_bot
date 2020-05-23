import re
from enum import Enum, auto

class AdMode(Enum):
     OR = auto()
     AND = auto()

class Logic(Enum): # Children logic
    OR     = auto()
    AND    = auto()

class Mode(Enum): # Pattern search mode
    INCLUDE     = auto()
    EXCLUDE     = auto()
    IGNORE      = auto()

AD_FILTER_FLAGS = re.IGNORECASE

autoria = r"(.+)?auto\.ria\.com(.+)?"
что_угодно = r"(.+)?"
сумма = r"(\d+([\.,]\d+)?)"
продам = r"([по][рт][оаі]да([мю]|[её]тся))"
слова = r"(([а-яa-z]+(\s{1,30}))+)"
валюта = r"(грн|грв|хрн|грив|хривен|UAH|гривен|гривні(в)?|usd|дол(л)?ар(ов)?|\$|(у\.?(\s{0,30})е\.?))"

AD_FILTERS = [
    # autoria
    { "mode": Logic.OR, "rxes" : [
                {'rx': r"(.+)?auto\.ria\.com(.+)?"}
            ]
    },
    # <что угодно>продам<слова><сумма><валюта><что_угодно>
    #r"([по][рт][оа]да([мю]|[её]тся)(\s+)?)(([а-яa-z]+(\s{1,30})?)+)(\d+([\.,]\d+)?\s{0,30})(([а-яa-z]+(\s{1,30}))+)?(грн|usd|грв|\$|UAH|хрн|гривен|грив|гривні(в)?|хривен|(у\.?(\s{1,30})?е\.?))(.+)?"
    { "mode": Logic.AND , "rxes": [
                {'rx': r"([по][рт][оа]да([мю]|[её]тся))"},
                {'rx': r"(грн|грв|хрн|грив|хривен|UAH|гривен|гривні(в)?|к\b|k\b|usd|дол((л)?ар(ов)?)?|\$|(у\.?(\s{0,30})е\.?))(\s+)?(\d+([\.,]\d+)?)"}
            ]
    },
    { "mode": Logic.AND , "rxes": [
                {'rx': r"([по][рт][оа]да([мю]|[её]тся))"},
                {'rx': r"(\d+([\.,]\d+)?)(\s+)?(грн|грв|хрн|грив|хривен|UAH|гривен|гривні(в)?|к\b|k\b|usd|дол((л)?ар(ов)?)?|\$|(у\.?(\s{0,30})е\.?))"}
            ]
    },
    #что_угодно + продам + слова + сумма + возможно(слова) + валюта + что_угодно
    # <сумма><валюта>продам<слова>
    #сумма + возможно(слова) + продам + слова
    { 'mode': Logic.AND , 'rxes': [
                {'count': 2, 'rx': r"(\d+([\.,]\d+)?)(\s+)?(грн|грв|хрн|грив|хривен|UAH|гривен|гривні(в)?|к\b|k\b|usd|дол((л)?ар(ов)?)?|\$|(у\.?(\s{0,30})е\.?))"}
            ]
    }
]

def is_match_ad0(text):  
    result = False
    for filter in AD_FILTERS:
        filter_result = False
        if filter['mode'] == Logic.OR:
            for rx in filter["rxes"]:
                need_to_find = rx.get('count', 1)
                m = re.findall(rx['rx'], text, AD_FILTER_FLAGS)
                if m and len(m) >= need_to_find: 
                    filter_result = True
                    break
        else:
            and_result = True
            for rx in filter["rxes"]:
                need_to_find = rx.get('count', 1)
                m = re.findall(rx['rx'], text, AD_FILTER_FLAGS)
                if not m or len(m) < need_to_find : 
                    and_result = False
                    break
            filter_result = and_result

        if filter_result:
            result = filter_result
            break

    return result



class FilterNode(object):
    def __init__(self, iterable=(), **kwargs):
        self.logic = None
        self.mode = None
        self.rx = None
        self.children : FilterNode  = []
        self.__dict__.update(iterable, **kwargs)

    def is_match_scheme(self, text):

        self_test = False
        children_test = False

        if self.rx and self.mode:
            res = re.search(self.rx, text, AD_FILTER_FLAGS)
            if (self.mode == Mode.INCLUDE) and (not res):
                return False
            elif (self.mode == Mode.EXCLUDE) and (res):
                return False

        if not self.logic:
            return False

        if self.logic == Logic.OR:
            for child in self.children:
                if child.is_match_scheme(text):
                    return True
            return False
        else: # AND
            for child in self.children:
                if not child.is_match_scheme(text):
                    return False
            return True
        
        return self_test & children_test
        

AD_PATTERN_TREE = {'logic': Logic.OR, 'children': [
    FilterNode({'logic': Logic.OR, 'mode': Mode.INCLUDE, 'rx': r"(.+)?auto\.ria\.com(.+)?"}),
    FilterNode({'logic': Logic.AND, 'mode': Mode.INCLUDE,'rx': r"([по][рт][оаі]да([мю]|[её]тся))", 'children': [
        FilterNode({'logic': Logic.OR, 'mode': Mode.INCLUDE, 'rx': r"(\d+([\.,]\d+)?)"}),
        FilterNode({'logic': Logic.OR, 'mode': Mode.INCLUDE, 'rx': r"(грн|usd|грв|\$|UAH|хрн|гривен|грив|гривні(в)?|хривен|(у\.?(\s{1,30})?е\.?))"})
    ] })
]}

if "__main__" == __name__:
    print("Starting...")
    tests = [
        "auto.ria.com",
        "Продам два крыла под реставрацию 1000грн",
        "Продам Ford Fusion Titanium\nЧистый 2018 год\nПробег 8100 км\nVIN 3FA6P0K96JR281035\n\n20500 долларов\nТорг на быстрое переоформление",
        'Залишки після ремонту (все оигінал) :\n1.  Декоративна накладка з фіксатором кочерги 900 грн\n2.  Замок капота лівий 1200 грн\n3.  Приборна панель на 2 екрани 80 дол\n4.  Блоки розжига галогенових фар з рестайлінга по 50 дол за шт',
        '1 прода(м) плюс сумма\n2 кнесколько сумм без продам',
        "Продам колеса за 100 грн",
        "Продам колеса за грн",
        "колеса за 100 грн",
        "Продам колеса за 100 $",
        "Продам колеса за 100$",
        "Продам колеса за 100 грн",
        "100 грн за колеса",
    ]

    filter = FilterNode(AD_PATTERN_TREE)
    
    single_test = True
    single_idx = 4

    if single_test:
        result1 = filter.is_match_scheme(tests[single_idx])
        result2 = is_match_ad0(tests[single_idx])
        print(f"Filter result: {result1} | result2 {result2} on text: \"{tests[single_idx]}\"")
    else:
        for s in tests:
            result1 = filter.is_match_scheme(s)
            result2 = is_match_ad0(s)
            print(f"Filter result1: {result1} | result2 {result2} on text: \"{s}\"")

def возможно(arg):
    return arg + r"?"


