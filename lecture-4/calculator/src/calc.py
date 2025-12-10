import flet as ft
import math

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE

class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE

class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK

class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.INDIGO_700
        self.color = ft.Colors.WHITE

class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.angle_mode = "DEG"  # DEG or RAD
        self.power_mode = False  # 累乗入力モード
        
        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.angle_indicator = ft.Text(value="DEG", color=ft.Colors.AMBER, size=14)
        
        self.width = 550  # 幅を広げる
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[self.angle_indicator, self.result], 
                    alignment="spaceBetween"
                ),
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
                ft.Row(
                    controls=[
                        ScientificButton(text="log", button_clicked=self.button_clicked),
                        ScientificButton(text="ln", button_clicked=self.button_clicked),
                        ScientificButton(text="eˣ", button_clicked=self.button_clicked),
                        ScientificButton(text="10ˣ", button_clicked=self.button_clicked),
                        ScientificButton(text="π", button_clicked=self.button_clicked),
                        ExtraActionButton(text="DEG/RAD", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
            self.power_mode = False

        elif data == "DEG/RAD":
            self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
            self.angle_indicator.value = self.angle_mode

        elif data == "π":
            self.result.value = self.format_number(math.pi)
            self.new_operand = True

        elif data == "√":
            try:
                value = float(self.result.value)
                if value < 0:
                    self.result.value = "Error"
                else:
                    self.result.value = self.format_number(math.sqrt(value))
                self.reset()
            except:
                self.result.value = "Error"
                self.reset()

        elif data == "x²":
            try:
                value = float(self.result.value)
                self.result.value = self.format_number(value ** 2)
                self.reset()
            except:
                self.result.value = "Error"
                self.reset()

        elif data == "xʸ":
            # 累乗モードを開始
            self.power_mode = True
            self.operand1 = float(self.result.value)
            self.operator = "^"
            self.new_operand = True

        elif data == "eˣ":
            try:
                value = float(self.result.value)
                self.result.value = self.format_number(math.exp(value))
                self.reset()
            except:
                self.result.value = "Error"
                self.reset()

        elif data == "10ˣ":
            try:
                value = float(self.result.value)
                self.result.value = self.format_number(10 ** value)
                self.reset()
            except:
                self.result.value = "Error"
                self.reset()

        elif data in ("sin", "cos", "tan", "log", "ln"):
            try:
                value = float(self.result.value)
                
                if data == "sin":
                    if self.angle_mode == "DEG":
                        value = math.radians(value)
                    self.result.value = self.format_number(math.sin(value))
                
                elif data == "cos":
                    if self.angle_mode == "DEG":
                        value = math.radians(value)
                    self.result.value = self.format_number(math.cos(value))
                
                elif data == "tan":
                    if self.angle_mode == "DEG":
                        value = math.radians(value)
                    self.result.value = self.format_number(math.tan(value))
                
                elif data == "log":
                    if value <= 0:
                        self.result.value = "Error"
                    else:
                        self.result.value = self.format_number(math.log10(value))
                
                elif data == "ln":
                    if value <= 0:
                        self.result.value = "Error"
                    else:
                        self.result.value = self.format_number(math.log(value))
                
                self.reset()
            except:
                self.result.value = "Error"
                self.reset()

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        elif data in ("+", "-", "*", "/"):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True
            self.power_mode = False

        elif data in ("="):
            self.result.value = self.calculate(
                self.operand1, float(self.result.value), self.operator
            )
            self.reset()
            self.power_mode = False

        elif data in ("%"):
            self.result.value = float(self.result.value) / 100
            self.reset()

        elif data in ("+/-"):
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)
            elif float(self.result.value) < 0:
                self.result.value = str(
                    self.format_number(abs(float(self.result.value)))
                )

        self.update()
            
    def format_number(self, num):
        if abs(num) > 1e10 or (abs(num) < 1e-10 and num != 0):
            # 非常に大きい数や小さい数は指数表記
            return f"{num:.6e}"
        elif num % 1 == 0:
            return int(num)
        else:
            return round(num, 10)  # 浮動小数点の精度を制限

    def calculate(self, operand1, operand2, operator):
        try:
            if operator == "+":
                return self.format_number(operand1 + operand2)
            elif operator == "-":
                return self.format_number(operand1 - operand2)
            elif operator == "*":
                return self.format_number(operand1 * operand2)
            elif operator == "/":
                if operand2 == 0:
                    return "Error"
                else:
                    return self.format_number(operand1 / operand2)
            elif operator == "^":
                # 累乗計算
                return self.format_number(operand1 ** operand2)
        except:
            return "Error"

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True

def main(page: ft.Page):
    page.title = "Scientific Calculator"
    calc = CalculatorApp()
    page.add(calc)

ft.app(main)