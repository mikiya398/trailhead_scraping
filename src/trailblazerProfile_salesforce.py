from simple_salesforce import Salesforce
import json

# 環境変数から当該組織へアクセスできるユーザー名/パスワードを読み込み
USERNAME = 'mkitamura@sfdc.0'
PASSWORD = 'Salesforce01'
TOKEN = 'v290FvnColqOzZFmD351PlmN'

# 接続実施
# Sandbox に接続する場合は引数に domain='test' を加える
sf = Salesforce(username=USERNAME, password=PASSWORD, security_token=TOKEN)

# JSONファイルを読み込む
with open('./data/output/trailhead.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
sf.bulk.Trailhead__c.insert(data, batch_size=10000,use_serial=True)