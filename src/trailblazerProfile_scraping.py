from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import psutil
import trailblazerProfile_scraping_prop
from trailblazerProfile_scraping_util import ScrapingUtil
import datetime

    
class Scraping(ScrapingUtil):
    def __init__(self):
        self.change_language_Flg = True
        self.coockie_Flg = True
        self.access_page_flg = True
        # Chromeのプロセスを検索し、終了する
        for proc in psutil.process_iter(['pid', 'name']):
            if 'chrome' in proc.info['name'].lower():
                proc.kill()
        self.options = Options()
        # self.options.add_argument("--headless")
        self.options.add_argument("--user-data-dir={}".format(trailblazerProfile_scraping_prop.user_data_dir))
        self.options.add_argument("--profile-directory={}".format(trailblazerProfile_scraping_prop.profile_directory))
        self.options.add_argument("--lang=ja-JP")
        self.driver = webdriver.Chrome(options=self.options)
        self.url = 'https://www.salesforce.com/trailblazer/'
        self.now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        self.wait = WebDriverWait(self.driver, 10)
        self.trailhead_dict = self.create_dict_from_csv(trailblazerProfile_scraping_prop.input_trailhead_file, 0)
        
    # def change_language(self):
    #     footer_element = self.driver.find_element(By.TAG_NAME, "wes-footer")
    #     select_element = footer_element.shadow_root.find_element(By.CSS_SELECTOR, "lwc-wes-select")
    #     select_shadow_root = select_element.shadow_root
    #     select_tag = select_shadow_root.find_element(By.ID, "select")
    #     select = Select(select_tag)
    #     select.select_by_value("ja")
    #     WebDriverWait(self.driver, 10).until(EC.staleness_of(footer_element))

        
    def access_page(self, trailblazerId):
        print('***** ' + trailblazerId + ' *****')
        url = self.url + trailblazerId
        self.driver.get(url)

        # salesforce.com/trailblazerにアクセスをした時「すべてのCookieを受け入れる」ボタンが出現するかチェック
        if self.coockie_Flg:
            try:
                self.coockie_Flg = False
                buttonElement = self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
                buttonElement.click()
                
            except:
                self.coockie_Flg = False
            
    def scraping_trailhead_badge(self, trailblazerId):
        """
        TrailblazerIdに対応するユーザが持つTrailheadバッチの名称を辞書リストで取得する。
        Parameters
        ----------
        trailblazerId: 取得したいTrailhead情報のTrailheadId

        Returns:List型
        -------
        Trailhead_badge
        """
        #「さらに表示」が表示されているかチェックし、表示されている場合は「さらに表示」ボタンを押下する。
        output = []
        tbme_profile_badges = self.driver.find_element(By.TAG_NAME, 'tbme-profile-badges').shadow_root
        while True:
            time.sleep(1)
            show_more_button_section = tbme_profile_badges.find_elements(By.CSS_SELECTOR,'*')[-1].shadow_root.find_elements(By.CSS_SELECTOR,'*')
            show_more_button_label = show_more_button_section[1].text
            if show_more_button_label == 'さらに表示' or show_more_button_label == 'Show More':
                show_more_button_section[0].click()
            else:
                break
        badge_list = [i.text for i in tbme_profile_badges.find_elements(By.CSS_SELECTOR,'*') if i.tag_name == 'lwc-tbui-badge']
        badge_number = len(badge_list)
        for i, badge in enumerate(badge_list):
            temp_dict = {
                "TrailblazerId__c" : "",
                "TrailheadBadgeName__c" : "",
                "ClearedOrder__c" : -1,
                "TrailheadCode__c" : "",
                "ScrapingExecutionDate__c": ""
            }
            temp_dict["TrailblazerId__c"] = trailblazerId
            temp_dict["TrailheadBadgeName__c"] = badge
            temp_dict["ClearedOrder__c"] = badge_number - i
            try:
                temp_dict["TrailheadCode__c"] = self.trailhead_dict[badge]['TRAILHEADCODE__C']
            except KeyError:
                pass
            temp_dict["scrapingExecutionDate"] = self.now
            output.append(temp_dict)
            
        return output
    
    def scraping_salesforce_certification(self, trailblazerId):
        """
        webスクレイピングを行い、所有salesforce資格を取得する。
        Parameters
        ----------
        trailblazerId: 取得したい所有salesforce資格のTrailheadId

        Returns:ListList型
        -------
        １要素が[trailheadId,salesforce資格]であるリスト
        """
        certification_list =[]
        certifications_element = self.driver.find_element(By.TAG_NAME, 'tbme-certifications')
        shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", certifications_element)
        lwc_tbui_certification_item = [i for i in shadow_root.find_elements(By.CSS_SELECTOR,'*') if i.tag_name == 'lwc-tbui-certification-item']
        certifications = [i.text.split('\n')[1] for i in lwc_tbui_certification_item]
        for certification in certifications:
            temp_dict = {
                "TrailblazerId__c" : "",
                "CertificationName__c" : ""
            }
            temp_dict["TrailblazerId__c"] = trailblazerId
            temp_dict["CertificationName__c"] = certification
            certification_list.append(temp_dict)
        return certification_list

    def main(self):
        trailblazerIds = self.read_csv(trailblazerProfile_scraping_prop.input_trailblazerId_file)
        badge_dict_list = []
        certification_dict_list = []
        for trailblazerId in trailblazerIds:
            self.access_page(trailblazerId)
            badge_dict_list += self.scraping_trailhead_badge(trailblazerId)
            certification_dict_list += self.scraping_salesforce_certification(trailblazerId)
        self.save_json(badge_dict_list,'badge_'+str(self.now))
        self.save_json(certification_dict_list, 'certification_'+str(self.now))


if __name__ == "__main__":
    badge = Scraping()
    badge.main()


