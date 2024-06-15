・プログラムの概要（trailblazerProfile_scraping.py）
    ・./data/input/フォルダに格納された「各行が一つのTrainblazerId値を持つ」csvファイルと「Trailhead__cオブジェクトをエクスポートした」csvファイルを元に、各ユーザのTrailheadバッチと資格をスクレイピングによって取得し、./data/output/フォルダに保存する。


・必要ライブラリ
    ・selenium
    ・psutil
・仮想環境のアクティブ化
    ・ターミナルで「. enviroment/bin/activate」または、「source enviroment/bin/activate」を実行


・設定ファイル（trailblazerProfileProperty.py）
    ・トレイルヘッドプロファイルページを日本語にする設定（google にログインしたのちに、chrome://version にアクセスし、表示されているプロファイル情報の値を入れる。）
        ・user_data_dir：
        ・user_data_dir：

    ・trailblazerIdを格納しているファイル
        ・input_trailblazerId_file = "./data/input/trailblazerIds.csv"

    ・salesforceからTrailhead__cレコードのエクスポートしたファイル
        ・input_trailhead_file = './data/input/extract.csv'