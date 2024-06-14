import unittest
import trailblazerProfile_scraping as tp
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

class trailblazerProfileTest(unittest.TestCase):
    def setUp(self):
        # 初期化処理
        pass

    def tearDown(self):
        # 終了処理
        pass

    def test_read_csv(self):    
        self.assertEqual(['daoki2008c01'], tp.csv_file_operations.read_csv('./data/input/trailblazerIdsTest.csv'))
        
    def test_access_page(self):
        fetcher = tp.fetch_trailhead_info()
        fetcher.options = Options()
        fetcher.driver = webdriver.Chrome(options=fetcher.options)
        fetcher.access_page('daoki2008c01')
        time.sleep(30)
        

if __name__ == "__main__":
    unittest.main()