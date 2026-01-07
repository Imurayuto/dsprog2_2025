import sqlite3
import requests
import json
from datetime import datetime

path = ''
db_name = 'weather.db'

# areasテーブル作成
def create_areas_table():
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        sql = '''
        CREATE TABLE IF NOT EXISTS areas (
            area_code TEXT PRIMARY KEY,
            area_name TEXT NOT NULL,
            center_code TEXT,
            center_name TEXT,
            area_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        
        cur.execute(sql)
        conn.commit()
        print('✅ areasテーブルを作成しました')
    
    except sqlite3.Error as e:
        print('❌ エラーが発生しました:', e)
    
    finally:
        conn.close()


# weather_forecastsテーブル作成
def create_weather_forecasts_table():
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        sql = '''
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            area_detail_name TEXT,
            forecast_date DATE NOT NULL,
            weather TEXT,
            wind TEXT,
            wave TEXT,
            temperature TEXT,
            time_define TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (area_code) REFERENCES areas(area_code)
        );
        '''
        
        cur.execute(sql)
        conn.commit()
        print('✅ weather_forecastsテーブルを作成しました')
    
    except sqlite3.Error as e:
        print('❌ エラーが発生しました:', e)
    
    finally:
        conn.close()


# warningsテーブル作成
def create_warnings_table():
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        sql = '''
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            warning_name TEXT NOT NULL,
            status TEXT,
            issued_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (area_code) REFERENCES areas(area_code)
        );
        '''
        
        cur.execute(sql)
        conn.commit()
        print('✅ warningsテーブルを作成しました')
    
    except sqlite3.Error as e:
        print('❌ エラーが発生しました:', e)
    
    finally:
        conn.close()


# forecast_historyテーブル作成
def create_forecast_history_table():
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        sql = '''
        CREATE TABLE IF NOT EXISTS forecast_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_json TEXT,
            FOREIGN KEY (area_code) REFERENCES areas(area_code)
        );
        '''
        
        cur.execute(sql)
        conn.commit()
        print('✅ forecast_historyテーブルを作成しました')
    
    except sqlite3.Error as e:
        print('❌ エラーが発生しました:', e)
    
    finally:
        conn.close()

# インデックス作成
def create_indexes():
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        # weather_forecastsテーブル用のインデックス
        sql1 = '''
        CREATE INDEX IF NOT EXISTS idx_weather_area_date 
        ON weather_forecasts(area_code, forecast_date, fetched_at DESC);
        '''
        cur.execute(sql1)
        
        # forecast_historyテーブル用のインデックス
        sql2 = '''
        CREATE INDEX IF NOT EXISTS idx_history_area_date 
        ON forecast_history(area_code, fetched_at DESC);
        '''
        cur.execute(sql2)
        
        conn.commit()
        print('✅ インデックスを作成しました')
    
    except sqlite3.Error as e:
        print('❌ エラーが発生しました:', e)
    
    finally:
        conn.close()

# 地域データをDBに保存
def save_areas_to_db():
    try:
        # 気象庁APIから地域リストを取得
        url = "http://www.jma.go.jp/bosai/common/const/area.json"
        response = requests.get(url)
        data_json = response.json()
        
        centers = data_json.get("centers", {})
        offices = data_json.get("offices", {})
        
        # DB接続
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        # centersデータを保存
        for center_code, center_data in centers.items():
            center_name = center_data.get("name", "")
            
            sql = '''
            INSERT OR REPLACE INTO areas 
            (area_code, area_name, area_type, center_code, center_name)
            VALUES (?, ?, ?, ?, ?);
            '''
            
            cur.execute(sql, (center_code, center_name, "center", center_code, center_name))
        
        # officesデータを保存
        for center_code, center_data in centers.items():
            center_name = center_data.get("name", "")
            children = center_data.get("children", [])
            
            for office_code in children:
                if office_code in offices:
                    office_data = offices[office_code]
                    office_name = office_data.get("name", "")
                    
                    sql = '''
                    INSERT OR REPLACE INTO areas 
                    (area_code, area_name, area_type, center_code, center_name)
                    VALUES (?, ?, ?, ?, ?);
                    '''
                    
                    cur.execute(sql, (office_code, office_name, "office", center_code, center_name))
        
        conn.commit()
        print('✅ 地域データをDBに保存しました')
    
    except sqlite3.Error as e:
        print('❌ DBエラーが発生しました:', e)
    except requests.RequestException as e:
        print('❌ API取得エラーが発生しました:', e)
    
    finally:
        conn.close()

# 天気予報データをDBに保存
def save_weather_forecast_to_db(area_code):
    try:
        # 気象庁APIから天気予報を取得
        url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
        response = requests.get(url)
        weather_data = response.json()
        
        # DB接続
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        fetched_at = datetime.now().isoformat()
        
        # forecast_historyに元のJSONを保存
        sql_history = '''
        INSERT INTO forecast_history (area_code, fetched_at, data_json)
        VALUES (?, ?, ?);
        '''
        cur.execute(sql_history, (area_code, fetched_at, json.dumps(weather_data, ensure_ascii=False)))
        
        # 天気予報を解析してweather_forecastsに保存
        for forecast in weather_data:
            time_series = forecast.get("timeSeries", [])
            
            for series in time_series:
                time_defines = series.get("timeDefines", [])
                areas = series.get("areas", [])
                
                for area in areas:
                    area_detail_name = area.get("area", {}).get("name", "")
                    weathers = area.get("weathers", [])
                    winds = area.get("winds", [])
                    waves = area.get("waves", [])
                    temps = area.get("temps", [])
                    
                    for i, time_def in enumerate(time_defines):
                        try:
                            dt = datetime.fromisoformat(time_def.replace('Z', '+00:00'))
                            forecast_date = dt.date().isoformat()
                            
                            sql_forecast = '''
                            INSERT INTO weather_forecasts 
                            (area_code, area_detail_name, forecast_date, weather, 
                            wind, wave, temperature, time_define, fetched_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                            '''
                            
                            cur.execute(sql_forecast, (
                                area_code,
                                area_detail_name,
                                forecast_date,
                                weathers[i] if i < len(weathers) else None,
                                winds[i] if i < len(winds) else None,
                                waves[i] if i < len(waves) else None,
                                temps[i] if i < len(temps) else None,
                                time_def,
                                fetched_at
                            ))
                        except Exception as e:
                            print(f'⚠️ 予報データ保存スキップ: {e}')
        
        conn.commit()
        print(f'✅ {area_code}の天気予報をDBに保存しました')
    
    except sqlite3.Error as e:
        print('❌ DBエラーが発生しました:', e)
    except requests.RequestException as e:
        print('❌ API取得エラーが発生しました:', e)
    
    finally:
        conn.close()

# 警報・注意報データをDBに保存
def save_warnings_to_db(area_code):
    try:
        # 気象庁APIから警報・注意報を取得
        url = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
        response = requests.get(url)
        warning_data = response.json()
        
        # DB接続
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        fetched_at = datetime.now().isoformat()
        
        # 既存の警報を削除（最新のみ保持）
        sql_delete = 'DELETE FROM warnings WHERE area_code = ?;'
        cur.execute(sql_delete, (area_code,))
        
        # 警報・注意報を保存
        warning_count = 0
        for area_key, area_warning in warning_data.items():
            if isinstance(area_warning, dict):
                warnings = area_warning.get("warnings", [])
                for warning in warnings:
                    if isinstance(warning, dict):
                        warning_name = warning.get("name", "")
                        status = warning.get("status", "")
                        
                        sql_insert = '''
                        INSERT INTO warnings 
                        (area_code, warning_name, status, fetched_at)
                        VALUES (?, ?, ?, ?);
                        '''
                        
                        cur.execute(sql_insert, (
                            area_code,
                            warning_name,
                            status,
                            fetched_at
                        ))
                        warning_count += 1
        
        conn.commit()
        
        if warning_count > 0:
            print(f'✅ {area_code}の警報・注意報を{warning_count}件保存しました')
        else:
            print(f'✅ {area_code}は警報・注意報なし')
    
    except sqlite3.Error as e:
        print('❌ DBエラーが発生しました:', e)
    except requests.RequestException as e:
        print('❌ API取得エラーが発生しました:', e)
    
    finally:
        conn.close()

# DBから最新の天気予報を取得
def get_latest_weather_from_db(area_code):
    try:
        # DB接続
        conn = sqlite3.connect(path + db_name)
        conn.row_factory = sqlite3.Row  # ← 辞書形式で取得
        cur = conn.cursor()
        
        # 最新の取得日時を取得
        sql_latest = '''
        SELECT DISTINCT fetched_at 
        FROM weather_forecasts 
        WHERE area_code = ?
        ORDER BY fetched_at DESC 
        LIMIT 1;
        '''
        cur.execute(sql_latest, (area_code,))
        result = cur.fetchone()
        
        if not result:
            print(f'⚠️ {area_code}の天気予報データがありません')
            return None
        
        latest_fetched = result['fetched_at']
        
        # 最新の天気予報を全て取得
        sql_forecasts = '''
        SELECT * FROM weather_forecasts 
        WHERE area_code = ? AND fetched_at = ?
        ORDER BY forecast_date, area_detail_name;
        '''
        cur.execute(sql_forecasts, (area_code, latest_fetched))
        forecasts = cur.fetchall()
        
        print(f'✅ {area_code}の天気予報を{len(forecasts)}件取得しました')
        print(f'   取得日時: {latest_fetched}')
        
        # 取得したデータを表示
        for forecast in forecasts:
            print(f'   {forecast["forecast_date"]} {forecast["area_detail_name"]}: {forecast["weather"]} (気温: {forecast["temperature"]}℃)')
        
        return forecasts
    
    except sqlite3.Error as e:
        print('❌ DBエラーが発生しました:', e)
        return None
    
    finally:
        conn.close()

# 予報履歴の日時リストを取得
def get_forecast_history_dates(area_code):
    try:
        # DB接続
        conn = sqlite3.connect(path + db_name)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # 予報取得履歴の日時リストを取得
        sql = '''
        SELECT DISTINCT fetched_at 
        FROM weather_forecasts 
        WHERE area_code = ?
        ORDER BY fetched_at DESC;
        '''
        cur.execute(sql, (area_code,))
        results = cur.fetchall()
        
        history_dates = [row['fetched_at'] for row in results]
        
        print(f'✅ {area_code}の予報履歴を{len(history_dates)}件取得しました')
        
        # 履歴を表示
        for i, date_str in enumerate(history_dates, 1):
            try:
                dt = datetime.fromisoformat(date_str)
                formatted = dt.strftime('%Y年%m月%d日 %H:%M:%S')
                print(f'   {i}. {formatted}')
            except:
                print(f'   {i}. {date_str}')
        
        return history_dates
    
    except sqlite3.Error as e:
        print('❌ DBエラーが発生しました:', e)
        return []
    
    finally:
        conn.close()

# 指定した日時の予報を取得
def get_weather_by_date(area_code, fetched_at):
    try:
        # DB接続
        conn = sqlite3.connect(path + db_name)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # 指定日時の天気予報を取得
        sql = '''
        SELECT * FROM weather_forecasts 
        WHERE area_code = ? AND fetched_at = ?
        ORDER BY forecast_date, area_detail_name;
        '''
        cur.execute(sql, (area_code, fetched_at))
        forecasts = cur.fetchall()
        
        if not forecasts:
            print(f'⚠️ {area_code}の{fetched_at}時点の予報データがありません')
            return None
        
        print(f'✅ {area_code}の予報を{len(forecasts)}件取得しました（取得日時: {fetched_at}）')
        
        # 取得したデータを表示
        for forecast in forecasts:
            weather = forecast["weather"] if forecast["weather"] else "データなし"
            temp = f'{forecast["temperature"]}℃' if forecast["temperature"] else "データなし"
            print(f'   {forecast["forecast_date"]} {forecast["area_detail_name"]}: {weather} (気温: {temp})')
        
        return forecasts
    
    except sqlite3.Error as e:
        print('❌ DBエラーが発生しました:', e)
        return None
    
    finally:
        conn.close()


# メイン処理
if __name__ == '__main__':
    create_areas_table()
    create_weather_forecasts_table()
    create_warnings_table()
    create_forecast_history_table()  
    create_indexes() 
    # 地域データを保存
    save_areas_to_db() 
    # 東京都（130000）の天気予報を保存
    save_weather_forecast_to_db('130000') 
    # 東京都（130000）の警報・注意報を保存
    save_warnings_to_db('130000')
    # DBから天気予報を取得して表示
    get_latest_weather_from_db('130000')
    # 予報履歴の日時リストを取得
    history_dates = get_forecast_history_dates('130000')
    # 2番目に古い予報を表示（もしあれば）
    if len(history_dates) >= 2:
        print('\n--- 過去の予報を表示 ---')
        get_weather_by_date('130000', history_dates[1]) 