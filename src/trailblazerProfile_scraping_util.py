import csv
import json
import datetime

class ScrapingUtil():
    def read_csv(self, csv_file_path):
        """
        TrailheadIdが格納されているCSVファイルを取得し、リストで出力する関数
        Parameters
        ----------
        csv_file_path : String
            TrailheadIdが格納されているCSVファイルのパス

        Returns
        -------
        trailblazerIds: List<String>
            TrailheadIdが格納されているリスト
        """
        
        trailblazerIds = [] # 格納するための空のリストを作成
        with open(csv_file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                trailblazerIds.append(row[0])
        return trailblazerIds
    

    def csv_to_dict(self, csv_file):
        data = []
        with open(csv_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                temp_dict = {
                    "trailblazerId": row["trailblazerId"],
                    "trailheadName": row["trailheadName"],
                    "clearedOrder": row["clearedOrder"],
                    "pfCode": row["pfCode"],
                    "clearedDate": row["clearedDate"]
                }
                data.append(temp_dict)
        return data
    
    
    def list_to_dict(self, headers, records):
        """
        ヘッダーとレコードのリストを辞書型に変換する関数
        Parameters:
            headers (list): ヘッダーのリスト
            records (list): レコードのリスト
        Returns:
            list: 辞書型に変換されたレコードのリスト
        """
        
        result = []
        for record in records:
            record_dict = {}
            for i in range(len(headers)):
                record_dict[headers[i]] = record[i]
            result.append(record_dict)
        return result

    def save_json(self, data, file_name):
        """
        リストをJSON形式のファイルとして保存する関数
        Args:
        - data: 保存したいデータ（リスト）
        - file_path: 保存先のファイルパス
        """
        with open('./data/output/{}.json'.format(file_name), 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
    


    def create_dict_from_csv(self, file_path, key_index):
        """指定されたcsvファイルの各行を読み込み、指定られた列をKeyとする辞書を返す。

        Args:
            file_path (String): csvファイルパス
            key_column (Integer): Keyにする列

        Returns:
            Dict: 
        """
        result_dict = {}
        header_list = []
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for i, row in enumerate(csv_reader):
                if i == 0:
                    header_list = row
                    continue
                temp_dict = {}
                for j, header in enumerate(header_list):
                    temp_dict[header] = row[j]
                result_dict[row[key_index]] = temp_dict
        return result_dict
