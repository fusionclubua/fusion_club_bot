import unittest
from parameterized import parameterized
from ad_filter_table import AdFilter

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



class TestSequence(unittest.TestCase):

    def __init__(self, name):
        super().__init__(name)
        self.filter = AdFilter

    def execute(self, idx):
        text = ads[idx]['text']
        return self.filter.is_match_scheme(text), ads[idx]['expect']

    def exec(self, text):
        return self.filter.is_match_scheme(text)

    @parameterized.expand(ads)
    def test_sequence(self, expect, text):
        result = self.exec(text)
        self.assertEqual(expect, result)