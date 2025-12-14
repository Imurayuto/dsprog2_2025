import flet as ft
import math

# ボタンの基本クラス（全てのボタンの元になる）
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text  # ボタンに表示される文字
        self.expand = expand  # ボタンの幅の比率
        self.on_click = button_clicked  # ボタンが押されたときに実行する関数
        self.data = text  # ボタンが押されたときに渡すデータ

# 数字ボタン用のクラス（0〜9と小数点）
class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24  # 背景色：薄い白
        self.color = ft.Colors.WHITE  # 文字色：白

# 演算子ボタン用のクラス（+、-、×、÷）
class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE  # 背景色：オレンジ
        self.color = ft.Colors.WHITE  # 文字色：白

# 特別な操作ボタン用のクラス（AC、+/-、%）
class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100  # 背景色：薄い青灰色
        self.color = ft.Colors.BLACK  # 文字色：黒

# 科学計算ボタン用のクラス（sin、cos、logなど）
class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.INDIGO_700  # 背景色：濃い藍色
        self.color = ft.Colors.WHITE  # 文字色：白

# 電卓のメインクラス
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()  # 計算機の内部状態を初期化
        self.angle_mode = "DEG"  # 角度モード（DEG=度、RAD=ラジアン）
        self.power_mode = False  # 累乗入力モードのフラグ
        
        # 計算結果を表示するテキスト（初期値は"0"）
        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        # 角度モードを表示するテキスト（左上に表示）
        self.angle_indicator = ft.Text(value="DEG", color=ft.Colors.AMBER, size=14)
        
        self.width = 550  # 電卓の幅を550ピクセルに設定
        self.bgcolor = ft.Colors.BLACK  # 背景色：黒
        self.border_radius = ft.border_radius.all(20)  # 角を丸くする
        self.padding = 20  # 内側の余白
        
        # 電卓のレイアウト（縦に並べる）
        self.content = ft.Column(
            controls=[
                # 一番上の行：角度モード表示と計算結果
                ft.Row(
                    controls=[self.angle_indicator, self.result], 
                    alignment="spaceBetween"  # 左右に配置
                ),
                # 科学計算ボタンの行1（三角関数と累乗）
                ft.Row(
                    controls=[
                        ScientificButton(text="sin", button_clicked=self.button_clicked),
                        ScientificButton(text="cos", button_clicked=self.button_clicked),
                        ScientificButton(text="tan", button_clicked=self.button_clicked),
                        ScientificButton(text="√", button_clicked=self.button_clicked),
                        ScientificButton(text="x²", button_clicked=self.button_clicked),
                        ScientificButton(text="xʸ", button_clicked=self.button_clicked),
                    ]
                ),
                # 科学計算ボタンの行2（対数、指数、階乗、円周率）
                ft.Row(
                    controls=[
                        ScientificButton(text="log", button_clicked=self.button_clicked),
                        ScientificButton(text="ln", button_clicked=self.button_clicked),
                        ScientificButton(text="eˣ", button_clicked=self.button_clicked),
                        ScientificButton(text="10ˣ", button_clicked=self.button_clicked),
                        ScientificButton(text="n!", button_clicked=self.button_clicked),
                        ScientificButton(text="π", button_clicked=self.button_clicked),
                    ]
                ),
                # 角度モード切り替えボタンの行
                ft.Row(
                    controls=[
                        ExtraActionButton(text="DEG/RAD", button_clicked=self.button_clicked),
                    ]
                ),
                # 特別操作と割り算の行
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                # 数字7〜9と掛け算の行
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                # 数字4〜6と引き算の行
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                # 数字1〜3と足し算の行
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                # 数字0、小数点、イコールの行
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),  # 0ボタンは2倍の幅
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    # ボタンが押されたときに実行される関数う
    def button_clicked(self, e):
        data = e.control.data  # 押されたボタンのデータ（文字）を取得
        print(f"Button clicked with data = {data}")  # デバッグ用：どのボタンが押されたか表示
        
        # エラー表示中か、ACボタンが押された場合
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"  # 表示を"0"にリセット
            self.reset()  # 内部状態をリセット
            self.power_mode = False  # 累乗モードを解除

        # 角度モード切り替えボタンが押された場合
        # 三角関数の入力を度数法（DEG）とラジアン（RAD）で切り替える
        elif data == "DEG/RAD":
            # 現在のモードがDEGならRADに、RADならDEGに切り替え
            self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
            self.angle_indicator.value = self.angle_mode  # 表示を更新

        # 円周率ボタンが押された場合
        elif data == "π":
            self.result.value = self.format_number(math.pi)  # πの値を表示
            self.new_operand = True  # 次の入力で上書きするフラグを立てる
        # operandとはex) 2 + 3 の場合の2や3のこと

        # 平方根ボタンが押された場合
        elif data == "√":
            try:
                value = float(self.result.value)  # 現在の表示を数値に変換
                if value < 0:  # 負の数の場合
                    self.result.value = "Error"  # エラー表示
                else:
                    self.result.value = self.format_number(math.sqrt(value))  # 平方根を計算
                self.reset()  # 内部をリセット
            except:  # エラーが発生した場合
                self.result.value = "Error"  # エラー表示
                self.reset()  # 内部をリセット

        # 2乗ボタンが押された場合
        elif data == "x²":
            try:
                value = float(self.result.value)  # 現在の表示を数値に変換
                self.result.value = self.format_number(value ** 2)  # 2乗を計算（value × value）
                self.reset()  # 内部をリセット
            except:  # エラーが発生した場合
                self.result.value = "Error"  # エラー表示
                self.reset()  # 内部をリセット

        # 累乗ボタンが押された場合
        elif data == "xʸ":
            self.power_mode = True  # 累乗モードを有効化
            self.operand1 = float(self.result.value)  # 現在の値を底として保存
            self.operator = "^"  # 演算子を累乗に設定
            self.new_operand = True  # 次の入力を指数として受け取る準備
        # operandの説明は164行目参照

        # 自然指数ボタンが押された場合
        elif data == "eˣ":
            try:
                value = float(self.result.value)  # 現在の表示を数値に変換
                self.result.value = self.format_number(math.exp(value))  # e^value を計算
                self.reset()  # 内部をリセット
            except:  # エラーが発生した場合
                self.result.value = "Error"  # エラー表示
                self.reset()  # 内部をリセット

        # 10の累乗ボタンが押された場合
        elif data == "10ˣ":
            try:
                value = float(self.result.value)  # 現在の表示を数値に変換
                self.result.value = self.format_number(10 ** value)  # 10^value を計算
                self.reset()  # 内部をリセット
            except:  # エラーが発生した場合
                self.result.value = "Error"  # エラー表示
                self.reset()  # 内部をリセット

        # 階乗ボタンが押された場合
        elif data == "n!":
            try:
                value = float(self.result.value)  # 現在の表示を数値に変換
                # 階乗は0以上の整数でないと計算できない
                if value < 0 or value != int(value):  # 負の数または小数の場合
                    self.result.value = "Error"  # エラー表示
                else:
                    # math.factorial()で階乗を計算
                    self.result.value = self.format_number(math.factorial(int(value)))
                self.reset()  # 内部をリセット
            except:  # エラーが発生した場合
                self.result.value = "Error"  # エラー表示
                self.reset()  # 内部をリセット

        # 三角関数・対数関数ボタンが押された場合
        elif data in ("sin", "cos", "tan", "log", "ln"):
            try:
                value = float(self.result.value)  # 現在の表示を数値に変換する
                
                # sinが押された場合
                if data == "sin":
                    if self.angle_mode == "DEG":  # 度モードの場合
                        value = math.radians(value)  # 度をラジアンに変換
                    self.result.value = self.format_number(math.sin(value))  # sinを計算
                
                # cosが押された場合
                elif data == "cos":
                    if self.angle_mode == "DEG":  # 度モードの場合
                        value = math.radians(value)  # 度をラジアンに変換
                    self.result.value = self.format_number(math.cos(value))  # cosを計算
                
                # tanが押された場合
                elif data == "tan":
                    if self.angle_mode == "DEG":  # 度モードの場合
                        value = math.radians(value)  # 度をラジアンに変換
                    self.result.value = self.format_number(math.tan(value))  # tanを計算
                
                # 常用対数があ押された場合
                elif data == "log":
                    if value <= 0:  # 0以下の場合
                        self.result.value = "Error"  # エラー表示（対数は正の数でしか計算できない）
                    else:
                        self.result.value = self.format_number(math.log10(value))  # log10を計算
                
                # 自然対数が押された場合
                elif data == "ln":
                    if value <= 0:  # 0以下の場合
                        self.result.value = "Error"  # エラー表示（対数は正の数でしか計算できない）
                    else:
                        self.result.value = self.format_number(math.log(value))  # 自然対数を計算
                
                self.reset()  # 内部状態をリセット
            except:  # エラーが発生した場合
                self.result.value = "Error"  # エラー表示
                self.reset()  # 内部状態をリセット

        # 数字ボタン（0〜9）または小数点が押された場合
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            # 現在の表示が"0"または新しい数値の入力開始の場合
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data  # 押された数字で上書き
                self.new_operand = False  # 入力継続をオフ
            else:
                self.result.value = self.result.value + data  # 既存の表示に数字を追加
        # operandの説明は164行目参照

        # 四則演算ボタン（+、-、×、÷）が押された場合
        elif data in ("+", "-", "*", "/"):
            # 前の計算があれば実行（例：5 + 3 + の2回目の+を押したとき、5+3=8を計算）
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.operator = data  # 新しい演算子を保存
            if self.result.value == "Error":  # エラーの場合
                self.operand1 = "0"  # 第1operandを0にリセット
            else:
                self.operand1 = float(self.result.value)  # 計算結果を第1operandとして保存
            self.new_operand = True  # 次の入力を新しい数値として受け取る
            self.power_mode = False  # 累乗モードを解除
        # operandの説明は164行目参照

        # イコールボタンが押された場合
        elif data in ("="):
            # 保存されている計算を実行（例：5 + 3 = の場合、5+3を計算）
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.reset()  # 内部状態をリセット
            self.power_mode = False  # 累乗モードを解除

        # パーセントボタンが押された場合
        elif data in ("%"):
            self.result.value = float(self.result.value) / 100  # 現在の値を100で割る
            self.reset()  # 内部状態をリセット

        # 正負切り替えボタンが押された場合
        elif data in ("+/-"):
            if float(self.result.value) > 0:  # 正の数の場合
                self.result.value = "-" + str(self.result.value)  # マイナスを付ける
            elif float(self.result.value) < 0:  # 負の数の場合
                # マイナスを取って絶対値にする
                self.result.value = str(
                    self.format_number(abs(float(self.result.value)))
                )

        self.update()  # 画面を更新して変更を反映
            
    # 数値を見やすい形式に整形する関数
    def format_number(self, num):
        # 非常に大きい数（100億以上）または非常に小さい数（0.0000000001未満）の場合
        if abs(num) > 1e10 or (abs(num) < 1e-10 and num != 0):
            return f"{num:.6e}"  # 指数表記で表示（例：1.23e+10）
        elif num % 1 == 0:  # 小数部分が0の場合
            return int(num)  # 整数として表示
        else:
            return round(num, 10)  # 小数点以下10桁する

    # 四則演算と累乗を実際に計算する関数
    def calculate(self, operand1, operand2, operator):
        try:
            if operator == "+":  # 足し算
                return self.format_number(operand1 + operand2)
            elif operator == "-":  # 引き算
                return self.format_number(operand1 - operand2)
            elif operator == "*":  # 掛け算
                return self.format_number(operand1 * operand2)
            elif operator == "/":  # 割り算
                if operand2 == 0:  # 0で割ろうとした場合
                    return "Error"  # エラー表示
                else:
                    return self.format_number(operand1 / operand2)
            elif operator == "^":  # 累乗（x^yボタン用）
                return self.format_number(operand1 ** operand2)  # operand1のoperand2乗を計算
        except:  # 何らかのエラーが発生した場合
            return "Error"  # エラー表示
        # operandの説明は164行目参照

    # 計算機を初期化する
    def reset(self):
        self.operator = "+"  # 演算子を初期化（+で初期化すると最初の計算が0+数値になる）
        self.operand1 = 0  # 第1operandを0にリセット
        self.new_operand = True  # 次の入力を新しい数値として受け取るフラグ
    # operandの説明は164行目参照

# アプリを起動する
def main(page: ft.Page):
    page.title = "Scientific Calculator"  # タイトルを設定
    calc = CalculatorApp()  # 電卓を作成
    page.add(calc)  # ページに電卓を追加

# アプリを実行
ft.app(main)