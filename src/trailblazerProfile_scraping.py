import time
import datetime
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import concurrent.futures
import queue
from trailblazerProfile_scraping_util import ScrapingUtil
import trailblazerProfile_scraping_prop
from trailblazerProfile_salesforce import upsert

class Scraping(ScrapingUtil):
    def __init__(self):
        self.terminate_existing_chrome_processes()
        self.now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000")

    def terminate_existing_chrome_processes(self):
        """既存のChromeプロセスを終了して競合を避ける。"""
        for proc in psutil.process_iter(['pid', 'name']):
            if 'chrome' in proc.info['name'].lower():
                proc.kill()

    def create_webdriver(self, trailblazerId):
        """新しいWebDriverインスタンスを作成する。"""
        options = Options()
        options.add_argument("--lang=ja-JP")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        driver.get(trailblazerProfile_scraping_prop.trailblazer_url + trailblazerId)
        self.handle_cookie_consent(driver)
        return driver

    def handle_cookie_consent(self, driver):
        """クッキー同意ボタンが表示された場合に処理する。"""
        try:
            button_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            button_element.click()
        except Exception as e:
            print(f"Cookie consent handling error: {e}")

    def scraping_trailhead_badge(self, driver, trailblazerId):
        """指定されたTrailblazer IDのTrailheadバッジをスクレイピングする。"""
        output = []
        tbme_profile_badges = driver.find_element(By.TAG_NAME, 'tbme-profile-badges').shadow_root
        self.click_show_more(tbme_profile_badges)

        lwc_tbui_badge = [i for i in tbme_profile_badges.find_elements(By.CSS_SELECTOR, '*') if i.tag_name == 'lwc-tbui-badge']
        lwc_tbui_badge_shadow = [i.shadow_root for i in lwc_tbui_badge]
        badge_list = [i.text for i in lwc_tbui_badge]

        trailhead_code_list = self.extract_trailhead_codes(lwc_tbui_badge_shadow)
        badge_number = len(badge_list)

        output = self.create_badge_dict_list(trailhead_code_list, trailblazerId, badge_list, badge_number)
        return output
    
    def click_show_more(self, tbme_profile_badges):
        """「さらに表示」ボタンが表示されている場合にクリックして、すべてのバッジをロードする。"""
        while True:
            try:
                show_more_button_section = tbme_profile_badges.find_elements(By.CSS_SELECTOR, '*')[-1].shadow_root.find_elements(By.CSS_SELECTOR, '*')
                show_more_button = show_more_button_section[0]
                if show_more_button.text in ['さらに表示', 'Show More']:
                    show_more_button.click()
                    time.sleep(1)  # 必要最低限の待ち時間を設定
                else:
                    break
            except Exception as e:
                print(f"Show more button error: {e}")
                break
            
    def extract_trailhead_codes(self, badge_shadows):
        """バッジのshadow rootからTrailheadコードを抽出する。"""
        trailhead_code_list = []
        for shadow_root in badge_shadows:
            trailhead_code = ''
            try:
                href = [i for i in shadow_root.find_elements(By.CSS_SELECTOR, '*') if i.tag_name == 'a'][0].get_attribute('href')
                trailhead_code = href.split('/')[-2] + '_' + href.split('/')[-1]
            except Exception as e:
                pass
            trailhead_code_list.append(trailhead_code)
        return trailhead_code_list
    
    def create_badge_dict_list(self, trailhead_code_list, trailblazerId, badge_list, badge_number):
        """バッジごとの辞書リストを作成する。"""
        output = []
        for i, badge in enumerate(badge_list):
            if trailhead_code_list[i] != '':
                temp_dict = {
                    "ForeignKey__c": trailblazerId + '_' + trailhead_code_list[i],
                    "TrailheadCode__c": trailhead_code_list[i],
                    "TrailblazerId__c": trailblazerId,
                    "TrailheadName__c": badge,
                    "ClearedOrder__c": badge_number - i,
                    "ScrapingExecutionDate__c": self.now
                }
                output.append(temp_dict)
        return output   
            
    def scraping_salesforce_certification(self, driver, trailblazerId):
        """指定されたTrailblazer IDのSalesforce認定資格をスクレイピングする。"""
        certification_list = []
        certifications_element = driver.find_element(By.TAG_NAME, 'tbme-certifications')
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", certifications_element)
        lwc_tbui_certification_item = [i for i in shadow_root.find_elements(By.CSS_SELECTOR, '*') if i.tag_name == 'lwc-tbui-certification-item']
        certifications = [i.text.split('\n')[1] for i in lwc_tbui_certification_item]
        for certification in certifications:
            temp_dict = {
                "TrailblazerId__c": trailblazerId,
                "CertificationName__c": certification
            }
            certification_list.append(temp_dict)
        return certification_list

    def main(self):
        """すべてのTrailblazer IDに対してスクレイピングを実行するメインメソッド。"""
        trailblazerIds = self.read_csv(trailblazerProfile_scraping_prop.input_trailblazerId_file)
        badge_dict_queue = queue.Queue()
        certification_dict_queue = queue.Queue()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.scrape_trailblazer, trailblazerId, badge_dict_queue, certification_dict_queue): trailblazerId for trailblazerId in trailblazerIds}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error scraping Trailblazer ID {futures[future]}: {e}")

        badge_dict_list = []
        while not badge_dict_queue.empty():
            badge_dict_list.extend(badge_dict_queue.get())
            
        certification_dict_list = []
        while not certification_dict_queue.empty():
            certification_dict_list.extend(certification_dict_queue.get())
        self.save_json(badge_dict_list, 'badge/CompletedTrailheadWK__c_' + self.now)
        self.save_json(certification_dict_list, 'certification/Certification__c_' + self.now)

    def scrape_trailblazer(self, trailblazerId, badge_dict_queue, certification_dict_queue):
        print(trailblazerId)
        driver = self.create_webdriver(trailblazerId=trailblazerId)
        try:
            badges = self.scraping_trailhead_badge(driver, trailblazerId)
            certifications = self.scraping_salesforce_certification(driver, trailblazerId)
            badge_dict_queue.put(badges)
            certification_dict_queue.put(certifications)
        finally:
            driver.quit()

if __name__ == "__main__":
    scraper = Scraping()
    scraper.main()
    upsert()
