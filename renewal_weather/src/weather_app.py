import flet as ft
import requests
import sqlite3
import json
from datetime import datetime

# === データベース関連の関数 ===

path = ''
db_name = 'weather.db'

def init_database():
    """データベース初期化"""
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        # areasテーブル
        cur.execute('''
            CREATE TABLE IF NOT EXISTS areas (
                area_code TEXT PRIMARY KEY,
                area_name TEXT NOT NULL,
                center_code TEXT,
                center_name TEXT,
                area_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # weather_forecastsテーブル
        cur.execute('''
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
        ''')
        
        # インデックス
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_weather_area_date 
            ON weather_forecasts(area_code, forecast_date, fetched_at DESC);
        ''')
        
        # warningsテーブル
        cur.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT NOT NULL,
                warning_name TEXT NOT NULL,
                status TEXT,
                issued_at TIMESTAMP,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (area_code) REFERENCES areas(area_code)
            );
        ''')
        
        # forecast_historyテーブル
        cur.execute('''
            CREATE TABLE IF NOT EXISTS forecast_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT NOT NULL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_json TEXT,
                FOREIGN KEY (area_code) REFERENCES areas(area_code)
            );
        ''')
        
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_area_date 
            ON forecast_history(area_code, fetched_at DESC);
        ''')
        
        conn.commit()
        print('✅ データベース初期化完了')
    
    except sqlite3.Error as e:
        print('❌ データベース初期化エラー:', e)
    
    finally:
        conn.close()


def save_areas_to_db(areas_data):
    """地域データをDBに保存"""
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        for center_code, center_data in areas_data.items():
            cur.execute('''
                INSERT OR REPLACE INTO areas 
                (area_code, area_name, area_type, center_code, center_name)
                VALUES (?, ?, ?, ?, ?);
            ''', (center_code, center_data["name"], "center", center_code, center_data["name"]))
            
            for office in center_data["offices"]:
                cur.execute('''
                    INSERT OR REPLACE INTO areas 
                    (area_code, area_name, area_type, center_code, center_name)
                    VALUES (?, ?, ?, ?, ?);
                ''', (office["code"], office["name"], "office", center_code, center_data["name"]))
        
        conn.commit()
        print('✅ 地域データをDBに保存しました')
    
    except sqlite3.Error as e:
        print('❌ 地域データ保存エラー:', e)
    
    finally:
        conn.close()


def get_areas_from_db():
    """DBから地域データを取得"""
    try:
        conn = sqlite3.connect(path + db_name)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('SELECT area_code, area_name FROM areas WHERE area_type = "center" ORDER BY area_code')
        centers = cur.fetchall()
        
        result = {}
        for center in centers:
            center_code = center["area_code"]
            center_name = center["area_name"]
            
            cur.execute('SELECT area_code, area_name FROM areas WHERE area_type = "office" AND center_code = ? ORDER BY area_code', (center_code,))
            offices = cur.fetchall()
            
            result[center_code] = {
                "name": center_name,
                "offices": [{"code": o["area_code"], "name": o["area_name"]} for o in offices]
            }
        
        return result
    
    except sqlite3.Error as e:
        print('❌ 地域データ取得エラー:', e)
        return {}
    
    finally:
        conn.close()


def save_weather_forecast_to_db(area_code, weather_data):
    """天気予報をDBに保存"""
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        fetched_at = datetime.now().isoformat()
        
        # 履歴保存
        cur.execute('INSERT INTO forecast_history (area_code, fetched_at, data_json) VALUES (?, ?, ?);',
                   (area_code, fetched_at, json.dumps(weather_data, ensure_ascii=False)))
        
        # 天気予報を解析して保存
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
                            
                            cur.execute('''
                                INSERT INTO weather_forecasts 
                                (area_code, area_detail_name, forecast_date, weather, wind, wave, temperature, time_define, fetched_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                            ''', (area_code, area_detail_name, forecast_date,
                                 weathers[i] if i < len(weathers) else None,
                                 winds[i] if i < len(winds) else None,
                                 waves[i] if i < len(waves) else None,
                                 temps[i] if i < len(temps) else None,
                                 time_def, fetched_at))
                        except:
                            pass
        
        conn.commit()
        print(f'✅ {area_code}の天気予報をDBに保存しました')
    
    except sqlite3.Error as e:
        print('❌ 天気予報保存エラー:', e)
    
    finally:
        conn.close()


def save_warnings_to_db(area_code, warning_data):
    """警報・注意報をDBに保存"""
    try:
        conn = sqlite3.connect(path + db_name)
        cur = conn.cursor()
        
        fetched_at = datetime.now().isoformat()
        
        # 既存削除
        cur.execute('DELETE FROM warnings WHERE area_code = ?;', (area_code,))
        
        # 新規保存
        for area_key, area_warning in warning_data.items():
            if isinstance(area_warning, dict):
                warnings = area_warning.get("warnings", [])
                for warning in warnings:
                    if isinstance(warning, dict):
                        cur.execute('''
                            INSERT INTO warnings (area_code, warning_name, status, fetched_at)
                            VALUES (?, ?, ?, ?);
                        ''', (area_code, warning.get("name", ""), warning.get("status", ""), fetched_at))
        
        conn.commit()
    
    except sqlite3.Error as e:
        print('❌ 警報保存エラー:', e)
    
    finally:
        conn.close()


def get_forecast_history_dates(area_code):
    """予報履歴の日時リストを取得"""
    try:
        conn = sqlite3.connect(path + db_name)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('SELECT DISTINCT fetched_at FROM weather_forecasts WHERE area_code = ? ORDER BY fetched_at DESC;', (area_code,))
        results = cur.fetchall()
        
        return [row['fetched_at'] for row in results]
    
    except sqlite3.Error as e:
        print('❌ 履歴取得エラー:', e)
        return []
    
    finally:
        conn.close()


def get_weather_by_date(area_code, fetched_at):
    """指定日時の天気予報を取得"""
    try:
        conn = sqlite3.connect(path + db_name)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('''
            SELECT * FROM weather_forecasts 
            WHERE area_code = ? AND fetched_at = ?
            ORDER BY forecast_date, area_detail_name;
        ''', (area_code, fetched_at))
        
        return cur.fetchall()
    
    except sqlite3.Error as e:
        print('❌ 予報取得エラー:', e)
        return []
    
    finally:
        conn.close()


def get_latest_warnings(area_code):
    """最新の警報・注意報を取得"""
    try:
        conn = sqlite3.connect(path + db_name)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM warnings WHERE area_code = ? ORDER BY fetched_at DESC;', (area_code,))
        
        return cur.fetchall()
    
    except sqlite3.Error as e:
        print('❌ 警報取得エラー:', e)
        return []
    
    finally:
        conn.close()


# === 以下、Fletアプリのコード（次のステップで追加） ===

# === Fletアプリのコード ===

class WeatherApp:
    def __init__(self):
        self.areas = {}
        
    def fetch_area_list(self):
        """地域リストを取得（DBまたはAPI）"""
        try:
            # まずDBから取得
            self.areas = get_areas_from_db()
            if self.areas:
                print('✅ DBから地域データを取得しました')
                return True
            
            # DBになければAPIから取得
            url = "http://www.jma.go.jp/bosai/common/const/area.json"
            data_json = requests.get(url).json()
            
            centers = data_json.get("centers", {})
            offices = data_json.get("offices", {})
            
            for center_code, center_data in centers.items():
                center_name = center_data.get("name", "")
                children = center_data.get("children", [])
                
                self.areas[center_code] = {
                    "name": center_name,
                    "offices": []
                }
                
                for office_code in children:
                    if office_code in offices:
                        office_data = offices[office_code]
                        self.areas[center_code]["offices"].append({
                            "code": office_code,
                            "name": office_data.get("name", "")
                        })
            
            # DBに保存
            save_areas_to_db(self.areas)
            print('✅ APIから地域データを取得してDBに保存しました')
            return True
        
        except Exception as e:
            print(f'❌ 地域リスト取得エラー: {e}')
            return False


def main(page: ft.Page):
    page.title = "気象庁天気予報アプリ（DB対応）"
    page.padding = 0
    page.window_width = 1200
    page.window_height = 800
    
    # データベース初期化
    init_database()
    
    app = WeatherApp()
    current_area_code = None
    current_area_name = None
    
    # 天気予報表示エリア
    weather_display = ft.Column(
        controls=[
            ft.Text("地域を選択してください", size=20, weight=ft.FontWeight.BOLD)
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    
    # 履歴選択ドロップダウン
    history_dropdown = ft.Dropdown(
        label="予報取得日時を選択",
        width=250,
        visible=False,
    )
    
    def get_weather_emoji(weather):
        """天気に応じた絵文字を返す"""
        if not weather:
            return "🌤️"
        if "晴" in weather:
            return "☀️"
        elif "曇" in weather:
            return "☁️"
        elif "雨" in weather:
            return "☔"
        elif "雪" in weather:
            return "❄️"
        else:
            return "🌤️"
    
    def display_weather_from_db(area_code, area_name, fetched_at=None):
        """DBから天気予報を表示"""
        weather_display.controls.clear()
        
        # 履歴ドロップダウンを更新
        history_dates = get_forecast_history_dates(area_code)
        if history_dates:
            history_dropdown.options = []
            for date_str in history_dates:
                try:
                    dt = datetime.fromisoformat(date_str)
                    label = dt.strftime('%Y年%m月%d日 %H:%M')
                    history_dropdown.options.append(ft.dropdown.Option(date_str, label))
                except:
                    history_dropdown.options.append(ft.dropdown.Option(date_str, date_str))
            
            if not fetched_at:
                fetched_at = history_dates[0]
            history_dropdown.value = fetched_at
            history_dropdown.visible = True
        
        # 天気予報取得
        forecasts = get_weather_by_date(area_code, fetched_at)
        
        if not forecasts:
            weather_display.controls.append(
                ft.Text("❌ 天気予報データがありません", color="#f44336", size=16)
            )
            page.update()
            return
        
        # ヘッダー
        try:
            fetch_dt = datetime.fromisoformat(fetched_at)
            fetch_str = fetch_dt.strftime('%Y年%m月%d日 %H:%M')
        except:
            fetch_str = fetched_at
        
        weather_display.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"📍 {area_name}",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#1976d2"
                    ),
                    ft.Text(
                        f"予報取得: {fetch_str}",
                        size=14,
                        color="#616161"
                    ),
                ]),
                padding=20,
                bgcolor="#e3f2fd",
                border_radius=10,
                margin=ft.margin.only(bottom=20)
            )
        )
        
        # 警報・注意報表示
        warnings = get_latest_warnings(area_code)
        if warnings:
            warning_chips = []
            for w in warnings:
                if w["status"] in ["発表", "継続"]:
                    if "警報" in w["warning_name"]:
                        bg_color = "#ef5350"
                        icon = "⚠️"
                    else:
                        bg_color = "#ffa726"
                        icon = "⚡"
                    
                    warning_chips.append(
                        ft.Container(
                            content=ft.Text(
                                f"{icon} {w['warning_name']}",
                                color="#ffffff",
                                weight=ft.FontWeight.BOLD,
                                size=14
                            ),
                            bgcolor=bg_color,
                            padding=10,
                            border_radius=20,
                        )
                    )
            
            if warning_chips:
                weather_display.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "⚠️ 警報・注意報",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#d32f2f"
                            ),
                            ft.Row(
                                controls=warning_chips,
                                wrap=True,
                                spacing=10,
                            )
                        ]),
                        padding=15,
                        bgcolor="#ffebee",
                        border_radius=10,
                        border=ft.border.all(2, "#ef5350"),
                        margin=ft.margin.only(bottom=20)
                    )
                )
        
        # 地域ごとにグループ化（天気データがあるもののみ）
        area_groups = {}
        for forecast in forecasts:
            if forecast["weather"]:  # 天気データがある場合のみ
                detail_name = forecast["area_detail_name"] or "全域"
                if detail_name not in area_groups:
                    area_groups[detail_name] = []
                area_groups[detail_name].append(forecast)
        
        # 天気予報カード表示
        for detail_name, forecasts_list in area_groups.items():
            cards = []
            
            for forecast in forecasts_list:
                try:
                    dt = datetime.fromisoformat(forecast["time_define"].replace('Z', '+00:00'))
                    date_str = dt.strftime('%m月%d日')
                    day_str = ['月', '火', '水', '木', '金', '土', '日'][dt.weekday()]
                except:
                    date_str = forecast["forecast_date"]
                    day_str = ""
                
                weather = forecast["weather"] or "不明"
                emoji = get_weather_emoji(weather)
                
                card_content = [
                    ft.Text(
                        f"{date_str}({day_str})",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#212121"
                    ),
                    ft.Text(emoji, size=50),
                    ft.Text(
                        weather,
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                        color="#424242"
                    ),
                ]
                
                # 気温表示
                if forecast["temperature"]:
                    try:
                        temp_val = int(forecast["temperature"])
                        if temp_val >= 30:
                            temp_color = "#d32f2f"
                        elif temp_val >= 25:
                            temp_color = "#f57c00"
                        elif temp_val >= 15:
                            temp_color = "#388e3c"
                        elif temp_val >= 5:
                            temp_color = "#1976d2"
                        else:
                            temp_color = "#0d47a1"
                        
                        card_content.append(
                            ft.Text(
                                f"🌡️ {forecast['temperature']}℃",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=temp_color
                            )
                        )
                    except:
                        pass
                
                card_content.append(ft.Divider(height=1))
                
                if forecast["wind"]:
                    card_content.append(
                        ft.Text(f"💨 {forecast['wind']}", size=12, color="#616161")
                    )
                
                if forecast["wave"]:
                    card_content.append(
                        ft.Text(f"🌊 {forecast['wave']}", size=12, color="#616161")
                    )
                
                card = ft.Container(
                    content=ft.Column(
                        card_content,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5
                    ),
                    width=200,
                    padding=15,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e0e0e0"),
                    border_radius=10,
                )
                cards.append(card)
            
            weather_display.controls.append(
                ft.Column([
                    ft.Text(
                        detail_name,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#0d47a1"
                    ),
                    ft.Row(
                        controls=cards,
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                    ),
                ], spacing=10)
            )
            weather_display.controls.append(ft.Divider(height=20))
        
        page.update()
    
    def on_history_select(e):
        """履歴選択時の処理"""
        if history_dropdown.value and current_area_code:
            display_weather_from_db(current_area_code, current_area_name, history_dropdown.value)
    
    history_dropdown.on_change = on_history_select
    
    def display_weather(area_code, area_name):
        """天気予報を表示（API取得→DB保存→表示）"""
        nonlocal current_area_code, current_area_name
        current_area_code = area_code
        current_area_name = area_name
        
        weather_display.controls.clear()
        weather_display.controls.append(ft.ProgressRing())
        page.update()
        
        try:
            # 警報・注意報取得
            url_warning = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
            warning_data = requests.get(url_warning).json()
            save_warnings_to_db(area_code, warning_data)
        except:
            pass
        
        try:
            # 天気予報取得してDB保存
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
            weather_data = requests.get(url).json()
            save_weather_forecast_to_db(area_code, weather_data)
            
            display_weather_from_db(area_code, area_name)
        except Exception as e:
            weather_display.controls.clear()
            weather_display.controls.append(
                ft.Text(f"❌ 天気予報の取得に失敗しました: {e}", color="#f44336", size=16)
            )
            page.update()
    
    # 以下のcreate_area_list()と初期化部分はそのまま
    
    def create_area_list():
        """地域リストを作成"""
        area_tiles = []
        
        for center_code, center_data in app.areas.items():
            office_tiles = []
            
            for office in center_data["offices"]:
                office_tile = ft.ListTile(
                    title=ft.Text(office["name"], color="#424242"),
                    on_click=lambda e, code=office["code"], name=office["name"]: display_weather(code, name),
                )
                office_tiles.append(office_tile)
            
            expansion_tile = ft.ExpansionTile(
                title=ft.Text(
                    center_data["name"],
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#212121"
                ),
                controls=office_tiles,
                initially_expanded=False,
            )
            area_tiles.append(expansion_tile)
        
        return area_tiles
    
    # 初期化
    loading_text = ft.Text("読み込み中...", size=16)
    page.add(loading_text)
    page.update()
    
    if app.fetch_area_list():
        page.controls.clear()
        area_list = create_area_list()
        
        area_list_view = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "🗾 地域選択",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color="#1976d2"
                    ),
                    padding=10,
                    bgcolor="#e3f2fd",
                ),
                ft.Column(
                    controls=area_list,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
            ],
            expand=True,
        )
        
        # メインレイアウト
        page.add(
        ft.Row(
            controls=[
                ft.Container(
                    content=area_list_view,
                    width=300,
                    bgcolor="#fafafa",
                    border=ft.border.only(right=ft.border.BorderSide(1, "#e0e0e0")),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=history_dropdown,  # ← これを追加
                            padding=10,
                        ),
                        weather_display,
                    ]),
                    expand=True,
                    padding=20,
                ),
            ],
            expand=True,
            )
        )
    else:
        page.controls.clear()
        page.add(
            ft.Text("❌ 地域リストの取得に失敗しました", color="#f44336", size=16)
        )
    
    page.update()

ft.app(target=main)