・プログラムの概要
    src/trailblazerProfile_scraping.py
        .各trailblazerIdのTrailheadバッチと資格をスクレイピングによって取得し、./data/output/フォルダにファイルを保存する。

    src/master_trailheadbadge_scraping.py
        .salesforceが提供するバッチを全て取得し、./data/output/フォルダにファイルを保存する。

・必要ライブラリ
    ・selenium
    ・psutil
・仮想環境のアクティブ化
    ・ターミナルで「. enviroment/bin/activate」または、「source enviroment/bin/activate」を実行

・設定ファイル（trailblazerProfileProperty.py）
    ・トレイルヘッドプロファイルページを日本語にする設定
        google にログインしたのちに、chrome://version にアクセスし、表示されているプロファイル情報の値を入れる。
            ・user_data_dir：
            ・user_data_dir：

    ・trailblazerIdを格納しているファイル
        ・input_trailblazerId_file = "./data/input/trailblazerIds.csv"
