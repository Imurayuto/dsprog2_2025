import sqlite3

path = ''
db_name = 'weather.db'

# ステップ1: areasテーブル作成
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


# ステップ2: weather_forecastsテーブル作成
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


# ステップ3: warningsテーブル作成
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


# ステップ4: forecast_historyテーブル作成
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


# メイン処理
if __name__ == '__main__':
    create_areas_table()
    create_weather_forecasts_table()
    create_warnings_table()
    create_forecast_history_table()  # ← 新しく追加