import unittest
from ad_filter_table import FilterNode, AD_PATTERN_TREE

ads = [
        {"expect": True,  "text": "auto.ria.com"},
        {"expect": True,  "text": "Продам два крыла под реставрацию 1000грн"},
        {"expect": False, "text": "Продам два крыла под реставрацию 1000грн магия"},
        {"expect": True,  "text": "Продам Ford Fusion Titanium\nЧистый 2018 год\nПробег 8100 км\nVIN 3FA6P0K96JR281035\n\n20500 долларов\nТорг на быстрое переоформление"},
        {"expect": True,  "text": "Залишки після ремонту (все оигінал) :\n1.  Декоративна накладка з фіксатором кочерги 900 грн\n2.  Замок капота лівий 1200 грн\n3.  Приборна панель на 2 екрани 80 дол\n4.  Блоки розжига галогенових фар з рестайлінга по 50 дол за шт"},
        {"expect": False, "text": "1 прода(м) плюс сумма\n2 кнесколько сумм без продам"},
        {"expect": True,  "text": "Продам колеса за 100 грн"},
        {"expect": False, "text": "Продам колеса за грн"},
        {"expect": False, "text": "колеса за 100 грн"},
        {"expect": True,  "text": "Продам колеса за 100 $"},
        {"expect": True,  "text": "Продам колеса за 100$"},
        {"expect": True,  "text": "Продам колеса за 100 грн"},
        {"expect": False, "text": "100 грн за колеса"},
    ]



class AdDetectionTree(unittest.TestCase):

    def __init__(self, name):
        super().__init__(name)
        self.filter = FilterNode(AD_PATTERN_TREE)

    
    def execute(self, idx):
        text = ads[idx]['text']
        return self.filter.is_match_scheme(text), ads[idx]['expect']

    def test0(self):
        result, expect = self.execute(0)
        self.assertEqual(result, expect)
    
    def test1(self):
        result, expect = self.execute(1)
        self.assertEqual(result, expect)
    
    def test2(self):
        result, expect = self.execute(2)
        self.assertEqual(result, expect)
    
    def test3(self):
        result, expect = self.execute(3)
        self.assertEqual(result, expect)
    
    def test4(self):
        result, expect = self.execute(3)
        self.assertEqual(result, expect)
    
    def test5(self):
        result, expect = self.execute(5)
        self.assertEqual(result, expect)
    
    def test6(self):
        result, expect = self.execute(6)
        self.assertEqual(result, expect)

    def test7(self):
        result, expect = self.execute(7)
        self.assertEqual(result, expect)

    def test8(self):
        result, expect = self.execute(8)
        self.assertEqual(result, expect)

    def test9(self):
        result, expect = self.execute(9)
        self.assertEqual(result, expect)

    def test10(self):
        result, expect = self.execute(10)
        self.assertEqual(result, expect)

    def test11(self):
        result, expect = self.execute(11)
        self.assertEqual(result, expect)

    def test12(self):
        result, expect = self.execute(12)
        self.assertEqual(result, expect)
