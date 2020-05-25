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
сумма = r"(\d+([\.,]\d+)?)"
валюта = r"(грн|грв|хрн|грив|хривен|UAH|гривен|гривні(в)?|к\b|k\b|usd|дол((л)?ар(ов)?)?|\$|(у\.?(\s{0,30})е\.?))"
сумма_валюта = сумма + r"(\s+)?" + валюта
валюта_сумма = валюта + r"(\s+)?" + сумма
продам = r"([по][рт][оаі]да([мю]|[её]тся))"

слова = r"(([а-яa-z]+(\s{1,30}))+)"
что_угодно = r"(.+)?"

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

def is_match_ad(text):  
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
        self.count = None
        self.children : FilterNode  = []
        self.__dict__.update(iterable, **kwargs)

    def is_match_scheme(self, text):
        self_test = True
        children_test = True

        if self.rx and self.mode:
            res = re.findall(self.rx, text, AD_FILTER_FLAGS)
            if (self.mode == Mode.INCLUDE):
                if not res:
                    self_test = False
                else:
                    needed_count = self.count if self.count else 1
                    self_test = len(res) >= needed_count
            else: # Mode.EXCLUDE:
                if res:
                    self_test = False
                else:
                    pass
                

        if self.logic and len(self.children) > 0:
            if self.logic == Logic.OR:
                or_child_test = False
                for child in self.children:
                    if child.is_match_scheme(text):
                        or_child_test = True
                        break
                children_test = or_child_test
            else: # AND
                and_child_test = True
                for child in self.children:
                    if not child.is_match_scheme(text):
                        and_child_test = False
                children_test = and_child_test
        
        return self_test & children_test
        
AD_PATTERN_TREE = {'logic': Logic.OR, 'children': [
    FilterNode({'mode': Mode.INCLUDE, 'rx': r"(.+)?auto\.ria\.com(.+)?"}),
    FilterNode({'mode': Mode.INCLUDE,'rx': r"([по][рт][оаі]да([мю]|[её]тся))", 'logic': Logic.AND, 'children': [
        FilterNode({'mode': Mode.INCLUDE, 'rx': r"(\d+([\.,]\d+)?)"}),
        FilterNode({'mode': Mode.INCLUDE, 'rx': r"(грн|грв|хрн|грив|хривен|UAH|гривен|гривні(в)?|к\b|k\b|usd|дол((л)?ар(ов)?)?|\$|(у\.?(\s{0,30})е\.?))"}),
        FilterNode({'mode': Mode.EXCLUDE, 'rx': r"магия"})
    ]}),
    FilterNode({'logic': Logic.OR, 'children': [
        FilterNode({'mode': Mode.INCLUDE, 'count': 2, 'rx': r"(\d+([\.,]\d+)?)(\s+)?(грн|грв|хрн|грив|хривен|UAH|гривен|гривні(в)?|к\b|k\b|usd|дол((л)?ар(ов)?)?|\$|(у\.?(\s{0,30})е\.?))"}),
        FilterNode({'mode': Mode.INCLUDE, 'count': 2, 'rx': r"(грн|грв|хрн|грив|хривен|UAH|гривен|гривні(в)?|к\b|k\b|usd|дол((л)?ар(ов)?)?|\$|(у\.?(\s{0,30})е\.?))(\s+)?(\d+([\.,]\d+)?)"}),
    ]})
]}

ads = [
        [True,  "auto.ria.com"],
        [False, "Продам два крыла под реставрацию 1000грн магия"],
        [True,  "Продам два крыла под реставрацию 1000грн"],
        [True,  "Продам Ford Fusion Titanium\nЧистый 2018 год\nПробег 8100 км\nVIN 3FA6P0K96JR281035\n\n20500 долларов\nТорг на быстрое переоформление"],
        [True,  "Залишки після ремонту (все оигінал) :\n1.  Декоративна накладка з фіксатором кочерги 900 грн\n2.  Замок капота лівий 1200 грн\n3.  Приборна панель на 2 екрани 80 дол\n4.  Блоки розжига галогенових фар з рестайлінга по 50 дол за шт"],
        [False, "1 прода(м) плюс сумма\n2 кнесколько сумм без продам"],
        [True,  "Продам колеса за 100 грн"],
        [False, "Продам колеса за грн"],
        [False, "колеса за 100 грн"],
        [True,  "Продам колеса за 100 $"],
        [True,  "Продам колеса за 100$"],
        [True,  "Продам колеса за 100 грн"],
        [False, "100 грн за колеса"],
    ]

if "__main__" == __name__:
    print("Testing...")
    filter = FilterNode(AD_PATTERN_TREE)
    
    single_test = False
    single_idx = 2

    if single_test: # For debugging is useful to specify the string and debug it
        result1 = filter.is_match_scheme(ads[single_idx][1]) #new way
        result2 = is_match_ad(ads[single_idx][1]) #old way
        print(f"Test: {result1} | {result2} on text: \"{ads[single_idx][1]}\"")
    else: # Something like a tests ;)
        for i in range(len(ads)):
            result1 = filter.is_match_scheme(ads[i][1])
            result2 = is_match_ad(ads[i][1])
            print(f"Test [{i}]: {'Pass' if result1 == ads[i][0] else 'Fail'} | { 'Pass' if result2 is ads[i][0] else 'Fail'}")