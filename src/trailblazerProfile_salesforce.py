import os
import pprint
from simple_salesforce import Salesforce

# 環境変数から当該組織へアクセスできるユーザー名/パスワードを読み込み
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

# 接続実施
# Sandbox に接続する場合は引数に domain='test' を加える
sf = Salesforce(username=USERNAME, password=PASSWORD, security_token='')

# 特定オブジェクトの項目情報を取得
# 次は取引先(Account)の項目。Account を Contact や Opportunity に変えることで他のオブエクトの項目情報を取得できる
fields = sf.Account.describe()['fields']

# 項目名と型を出力
for field in fields:
    print(f'{field["name"]} {field["type"]}')
