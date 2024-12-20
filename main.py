import re
import sys

class ConfigParser:
    def __init__(self):
        self.variables = {}
        self.dictionaries = []
        self.errors = []

    def parse_file(self, filepath):
        try:
            with open(filepath, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            self.errors.append(f"Файл '{filepath}' не найден.")
            return

        content = re.sub(r'\|\|.*', '', content)
        content = re.sub(r'<#.*?#>', '', content, flags=re.DOTALL)
        
        lines = content.splitlines()
        current_dict = None

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            try:
                if line.lower() == "begin":
                    current_dict = {}
                elif line.lower() == "end":
                    if current_dict is not None:
                        self.dictionaries.append(current_dict)
                        current_dict = None
                    else:
                        self.errors.append(f"Строка {line_num}: 'end' без соответствующего 'begin'.")
                elif current_dict is not None:
                    self.process_dictionary_line(line, current_dict, line_num)
                else:
                    self.parse_line(line, line_num)
            except Exception as e:
                self.errors.append(f"Строка {line_num}: ошибка парсинга: {e}")

    def process_dictionary_line(self, line, current_dict, line_num):
        match = re.match(r'(\w+)\s*:\s*([\w.]+);', line)
        if match:
            key, value = match.groups()
            try:
                value = float(value) if '.' in value else int(value)
            except ValueError:
                self.errors.append(f"Строка {line_num}: некорректное значение '{value}' в словаре.")
                value = None
            current_dict[key] = value
        else:
            self.errors.append(f"Строка {line_num}: некорректный синтаксис словаря.")

    def parse_line(self, line, line_num):
        if line.startswith("var"):
            self.process_variable(line, line_num)
        elif ":=" in line:
            self.process_assignment(line, line_num)
        else:
            self.errors.append(f"Строка {line_num}: неизвестный синтаксис '{line}'.")

    def process_variable(self, line, line_num):
        match = re.match(r'var\s+(\w+)\s*:=\s*([\w\s+\-*/(),]+);', line)
        if match:
            name, expression = match.groups()
            value = self.evaluate_expression(expression, line_num)
            self.variables[name] = value
        else:
            self.errors.append(f"Строка {line_num}: некорректный синтаксис переменной.")

    def process_assignment(self, line, line_num):
        match = re.match(r'(\w+)\s*:=\s*([\w\s+\-*/(),]+);', line)
        if match:
            name, expression = match.groups()
            value = self.evaluate_expression(expression, line_num)
            self.variables[name] = value
        else:
            self.errors.append(f"Строка {line_num}: некорректный синтаксис выражения.")

    def evaluate_expression(self, expression, line_num):
        def replace_max(match):
            args = match.group(1).split(',')
            try:
                values = [self.variables[arg.strip()] for arg in args if arg.strip() in self.variables]
                if values:
                    return str(max(values))
                else:
                    self.errors.append(f"Строка {line_num}: аргументы max() не найдены: {args}.")
                    return "0"
            except Exception as e:
                self.errors.append(f"Строка {line_num}: ошибка вычисления max: {e}")
                return "0"

        expression = re.sub(r'max\((.*?)\)', replace_max, expression)

        for var in self.variables:
            expression = re.sub(rf'\b{var}\b', str(self.variables[var]), expression)
        try:
            return eval(expression)
        except Exception as e:
            self.errors.append(f"Строка {line_num}: ошибка вычисления выражения '{expression}': {e}")
            return None

    def save_output(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as file:
            for idx, dictionary in enumerate(self.dictionaries, 1):
                file.write(f"Словарь {idx}: {{" + ", ".join(f"{k}={v}" for k, v in dictionary.items()) + "}\n")
            for name, value in self.variables.items():
                file.write(f"{name} = {value}\n")
            if self.errors:
                file.write("\nОшибки:\n")
                for error in self.errors:
                    file.write(f"{error}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python main.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    output_file = "output.txt"

    parser = ConfigParser()
    parser.parse_file(config_file)
    parser.save_output(output_file)

    print(f"Результаты сохранены в файл: {output_file}")
