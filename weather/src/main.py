import flet as ft
import requests
from datetime import datetime

class WeatherApp:
    def __init__(self):
        self.areas = {}
        self.selected_area_code = None
        self.weather_data = None
        
    def fetch_area_list(self):
        """気象庁APIから地域リストを取得"""
        try:
            url = "http://www.jma.go.jp/bosai/common/const/area.json"
            data_json = requests.get(url).json()
            
            # 地域データを階層構造で整理
            centers = data_json.get("centers", {})
            offices = data_json.get("offices", {})
            
            # 地方ごとに整理
            for center_code, center_data in centers.items():
                center_name = center_data.get("name", "")
                children = center_data.get("children", [])
                
                self.areas[center_code] = {
                    "name": center_name,
                    "offices": []
                }
                
                # 各地方配下の気象台を追加
                for office_code in children:
                    if office_code in offices:
                        office_data = offices[office_code]
                        self.areas[center_code]["offices"].append({
                            "code": office_code,
                            "name": office_data.get("name", "")
                        })
            
            return True
        except Exception as e:
            print(f"地域リスト取得エラー: {e}")
            return False
    
    def fetch_weather_data(self, area_code):
        """指定地域の天気予報を取得"""
        try:
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
            self.weather_data = requests.get(url).json()
            return True
        except Exception as e:
            print(f"天気予報取得エラー: {e}")
            return False

def main(page: ft.Page):
    page.title = "気象庁天気予報アプリ"
    page.padding = 0
    page.window_width = 1200
    page.window_height = 800
    
    app = WeatherApp()
    
    # 天気予報表示エリア
    weather_display = ft.Column(
        controls=[
            ft.Text("地域を選択してください", size=20, weight=ft.FontWeight.BOLD)
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    
    def get_weather_emoji(weather):
        """天気に応じた絵文字を返す"""
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
    
    def display_weather(area_code, area_name):
        """天気予報を表示"""
        weather_display.controls.clear()
        weather_display.controls.append(
            ft.ProgressRing()
        )
        page.update()
        
        if app.fetch_weather_data(area_code):
            weather_display.controls.clear()
            
            # ヘッダー
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
                            f"更新: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
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
            
            # 天気予報データを表示
            for forecast in app.weather_data:
                time_series = forecast.get("timeSeries", [])
                
                for series in time_series:
                    time_defines = series.get("timeDefines", [])
                    areas = series.get("areas", [])
                    
                    for area in areas:
                        area_name_detail = area.get("area", {}).get("name", "")
                        
                        # 天気情報
                        weathers = area.get("weathers", [])
                        winds = area.get("winds", [])
                        waves = area.get("waves", [])
                        
                        if weathers:
                            cards = []
                            for i, (time_def, weather) in enumerate(zip(time_defines, weathers)):
                                # 日付をパース
                                try:
                                    dt = datetime.fromisoformat(time_def.replace('Z', '+00:00'))
                                    date_str = dt.strftime('%m月%d日')
                                    day_str = ['月', '火', '水', '木', '金', '土', '日'][dt.weekday()]
                                except:
                                    date_str = time_def[:10]
                                    day_str = ""
                                
                                # 天気絵文字を取得
                                emoji = get_weather_emoji(weather)
                                
                                wind_text = winds[i] if i < len(winds) else ""
                                wave_text = waves[i] if i < len(waves) else ""
                                
                                card_content = [
                                    ft.Text(
                                        f"{date_str}({day_str})",
                                        size=16,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        emoji,
                                        size=50,
                                    ),
                                    ft.Text(
                                        weather,
                                        size=14,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Divider(height=1),
                                ]
                                
                                if wind_text:
                                    card_content.append(
                                        ft.Text(
                                            f"💨 {wind_text}",
                                            size=12,
                                            color="#616161"
                                        )
                                    )
                                
                                if wave_text:
                                    card_content.append(
                                        ft.Text(
                                            f"🌊 {wave_text}",
                                            size=12,
                                            color="#616161"
                                        )
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
                                        area_name_detail,
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color="#0d47a1"
                                    ),
                                    ft.Row(
                                        controls=cards,
                                        scroll=ft.ScrollMode.AUTO,
                                        spacing=10,
                                    ),
                                ],
                                spacing=10)
                            )
                            weather_display.controls.append(ft.Divider(height=20))
            
            page.update()
        else:
            weather_display.controls.clear()
            weather_display.controls.append(
                ft.Text("❌ 天気予報の取得に失敗しました", color="#f44336", size=16)
            )
            page.update()
    
    def create_area_list():
        """地域リストを作成"""
        area_tiles = []
        
        for center_code, center_data in app.areas.items():
            office_tiles = []
            
            for office in center_data["offices"]:
                office_tile = ft.ListTile(
                    title=ft.Text(office["name"]),
                    on_click=lambda e, code=office["code"], name=office["name"]: display_weather(code, name),
                )
                office_tiles.append(office_tile)
            
            expansion_tile = ft.ExpansionTile(
                title=ft.Text(
                    center_data["name"],
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                controls=office_tiles,
                initially_expanded=False,
            )
            area_tiles.append(expansion_tile)
        
        return area_tiles
    
    # 初期化: 地域リストを取得
    loading_text = ft.Text("読み込み中...", size=16)
    page.add(loading_text)
    page.update()
    
    if app.fetch_area_list():
        page.controls.clear()
        area_list = create_area_list()
        
        # 地域リスト表示エリア
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
                        content=weather_display,
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