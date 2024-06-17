import time
import datetime
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from trailblazerProfile_scraping_util import ScrapingUtil
import trailblazerProfile_scraping_prop


class Scraping(ScrapingUtil):
    def __init__(self):
        self.change_language_Flg = True
        self.cookie_Flg = True
        self.access_page_flg = True
        self.terminate_existing_chrome_processes()
        self.options = self.configure_chrome_options()
        self.driver = webdriver.Chrome(options=self.options)
        self.url = 'https://www.salesforce.com/trailblazer/'
        self.now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        self.wait = WebDriverWait(self.driver, 10)
        self.trailhead_dict = self.create_dict_from_csv(trailblazerProfile_scraping_prop.input_trailhead_file, 0)

    def terminate_existing_chrome_processes(self):
        """既存のChromeプロセスを終了して競合を避ける。"""
        for proc in psutil.process_iter(['pid', 'name']):
            if 'chrome' in proc.info['name'].lower():
                proc.kill()

    def configure_chrome_options(self):
        """WebDriverのChromeオプションを設定する。"""
        options = Options()
        options.add_argument("--user-data-dir={}".format(trailblazerProfile_scraping_prop.user_data_dir))
        options.add_argument("--profile-directory={}".format(trailblazerProfile_scraping_prop.profile_directory))
        options.add_argument("--lang=ja-JP")
        return options

    def access_page(self, trailblazerId):
        """指定されたTrailblazerプロフィールページにアクセスする。"""
        print('***** ' + trailblazerId + ' *****')
        url = self.url + trailblazerId
        self.driver.get(url)
        self.handle_cookie_consent()

    def handle_cookie_consent(self):
        """クッキー同意ボタンが表示された場合に処理する。"""
        if self.cookie_Flg:
            try:
                button_element = self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
                button_element.click()
                self.cookie_Flg = False
            except:
                self.cookie_Flg = False

    def scraping_trailhead_badge(self, trailblazerId):
        """指定されたTrailblazer IDのTrailheadバッジをスクレイピングする。"""
        output = []
        tbme_profile_badges = self.driver.find_element(By.TAG_NAME, 'tbme-profile-badges').shadow_root
        self.click_show_more(tbme_profile_badges)
        badge_list = [i.text for i in tbme_profile_badges.find_elements(By.CSS_SELECTOR, '*') if i.tag_name == 'lwc-tbui-badge']
        badge_number = len(badge_list)
        output = self.create_badge_dict_list(trailblazerId, badge_list, badge_number)
        return output

    def click_show_more(self, tbme_profile_badges):
        """「さらに表示」ボタンが表示されている場合にクリックして、すべてのバッジをロードする。"""
        while True:
            time.sleep(1)
            show_more_button_section = tbme_profile_badges.find_elements(By.CSS_SELECTOR, '*')[-1].shadow_root.find_elements(By.CSS_SELECTOR, '*')
            show_more_button_label = show_more_button_section[1].text
            if show_more_button_label in ['さらに表示', 'Show More']:
                show_more_button_section[0].click()
            else:
                break

    def create_badge_dict_list(self, trailblazerId, badge_list, badge_number):
        """バッジごとの辞書リストを作成する。"""
        output = []
        for i, badge in enumerate(badge_list):
            temp_dict = {
                "TrailblazerId__c": trailblazerId,
                "TrailheadBadgeName__c": badge,
                "ClearedOrder__c": badge_number - i,
                "TrailheadCode__c": self.trailhead_dict.get(badge, {}).get('TRAILHEADCODE__C', ''),
                "ScrapingExecutionDate__c": self.now
            }
            output.append(temp_dict)
        return output

    def scraping_salesforce_certification(self, trailblazerId):
        """指定されたTrailblazer IDのSalesforce資格をスクレイピングする。"""
        certification_list = []
        certifications_element = self.driver.find_element(By.TAG_NAME, 'tbme-certifications')
        shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", certifications_element)
        lwc_tbui_certification_item = [i for i in shadow_root.find_elements(By.CSS_SELECTOR, '*') if i.tag_name == 'lwc-tbui-certification-item']
        certifications = [i.text.split('\n')[1] for i in lwc_tbui_certification_item]
        for certification in certifications:
            temp_dict = {
                "TrailblazerId__c": trailblazerId,
                "CertificationName__c": certification
            }
            certification_list.append(temp_dict)
        return certification_list
    def scraping_all_trailhead(self):
        if (not(trailblazerProfile_scraping_prop.get_all_trailhead_flg)):
            return
        
            
        
    def main(self):
        """すべてのTrailblazer IDに対してスクレイピングを実行するメインメソッド。"""
        trailblazerIds = self.read_csv(trailblazerProfile_scraping_prop.input_trailblazerId_file)
        badge_dict_list = []
        certification_dict_list = []
        for trailblazerId in trailblazerIds:
            self.access_page(trailblazerId)
            badge_dict_list += self.scraping_trailhead_badge(trailblazerId)
            certification_dict_list += self.scraping_salesforce_certification(trailblazerId)
        self.save_json(badge_dict_list, 'badge_' + str(self.now))
        self.save_json(certification_dict_list, 'certification_' + str(self.now))


if __name__ == "__main__":
    scraper = Scraping()
    scraper.main()
