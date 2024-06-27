from simple_salesforce import Salesforce
import json

# 環境変数から当該組織へアクセスできるユーザー名/パスワードを読み込み
USERNAME = 'mkitamura@sfdc.0'
PASSWORD = 'Salesforce01'
TOKEN = 'v290FvnColqOzZFmD351PlmN'

def upsert():
    # 接続実施
    # Sandbox に接続する場合は引数に domain='test' を加える
    sf = Salesforce(username=USERNAME, password=PASSWORD, security_token=TOKEN)

    # JSONファイルを読み込む
    with open('./data/output/badge/CompletedTrailheadWK__c.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    sf.bulk.CompletedTrailheadWK__c.upsert(data,'ForeignKey__c',batch_size=1000,use_serial=True)

if __name__ == "__main__":
    upsert()