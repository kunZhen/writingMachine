import os
import subprocess


class PencilSimulator:
    def __init__(self, object_file):
        self.object_file = object_file
        self.x_position = 0
        self.y_position = 0
        self.pen_down = False
        self.canvas = [[" " for _ in range(50)] for _ in range(20)]
        self.instructions = []
        self.current_register_map = {}
        self.last_movabs_line = None
        self.last_movabs_register = None
        self.stack = []
        self.current_line = 0
        self.stack_vars = {}  # Para mantener las variables del stack

    def load_object(self, objdump_path=None):
        if objdump_path is None:
            objdump_path = r"C:\Program Files\LLVM\bin\llvm-objdump.exe"

        if not os.path.exists(objdump_path):
            raise FileNotFoundError(f"No se encontró llvm-objdump en: {objdump_path}")

        llvm_dir = os.path.dirname(objdump_path)
        os.environ["PATH"] = llvm_dir + os.pathsep + os.environ["PATH"]

        try:
            cmd = [objdump_path, "-d", "-r", self.object_file]
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            self.instructions = [line for line in result.stdout.splitlines() if line.strip()]
            print("Archivo desensamblado y cargado con éxito.")
            self.process_relocations()
        except subprocess.CalledProcessError as e:
            print(f"Error al desensamblar el archivo objeto: {e}")
            raise

    def process_relocations(self):
        for i, line in enumerate(self.instructions):
            if "movabsq" in line:
                self.last_movabs_line = line
                self.last_movabs_register = line.split(',')[-1].strip()
                print(f"[DEBUG] Encontrado registro: {self.last_movabs_register}")

            elif "IMAGE_REL_AMD64_ADDR64" in line and self.last_movabs_register:
                symbol = line.strip().split()[-1]
                if self.last_movabs_register not in self.current_register_map:
                    self.current_register_map[self.last_movabs_register] = []
                self.current_register_map[self.last_movabs_register].append({
                    'symbol': symbol,
                    'line': self.last_movabs_line,
                    'position': i
                })
                print(f"[DEBUG] Mapeando registro {self.last_movabs_register} a {symbol} en posición {i}")
                self.last_movabs_register = None

        print(f"[DEBUG] Mapa de registros completo: {self.current_register_map}")

    def get_current_register_type(self, register, line_num):
        if register not in self.current_register_map:
            return None

        mappings = self.current_register_map[register]
        current_mapping = None
        min_distance = float('inf')

        # Buscamos el mapeo más cercano pero anterior a la línea actual
        for mapping in mappings:
            distance = line_num - mapping['position']
            if 0 <= distance < min_distance:
                min_distance = distance
                current_mapping = mapping

        # Si estamos procesando una instrucción addl o incl con %rax,
        # siempre asumimos que es x_position
        if current_mapping and register == '%rax' and \
                ('addl' in self.instructions[line_num] or 'incl' in self.instructions[line_num]):
            return 'x_position'

        return current_mapping['symbol'] if current_mapping else None
    def get_line_address(self, line):
        # Extrae la dirección de una línea de instrucción
        if ':' in line:
            addr_str = line.split(':')[0].strip()
            try:
                return int(addr_str, 16)
            except ValueError:
                return None
        return None

    def find_line_by_address(self, target_addr):
        # Encuentra el índice de la línea que corresponde a una dirección
        for i, line in enumerate(self.instructions):
            addr = self.get_line_address(line)
            if addr == target_addr:
                return i
        return None

    def get_jump_target_address(self, jump_target):
        """Convierte una referencia de salto en una dirección hexadecimal."""
        # Si el salto es una dirección directa (0xb2)
        if jump_target.startswith('0x'):
            return int(jump_target, 16)

        # Si el salto es relativo a una función (<Main+0x92>)
        if '+0x' in jump_target:
            offset = int(jump_target.split('+0x')[1].rstrip('>'), 16)
            # Encontrar la dirección base de Main
            for line in self.instructions:
                if '<Main>:' in line:
                    base_addr = int(line.split('<')[0].strip(), 16)
                    return base_addr + offset
        return None

    def execute(self):
        print("\nIniciando simulación del lápiz...\n")
        self.stack = []
        self.current_line = 0
        self.stack_vars = {}  # Para mantener las variables del stack

        while self.current_line < len(self.instructions):
            line = self.instructions[self.current_line]
            if not line.strip() or "file format" in line or "Disassembly" in line:
                self.current_line += 1
                continue

            print(f"[DEBUG] Procesando línea {self.current_line}: {line}")

            # Push y Pop para el manejo de la pila
            if "pushq" in line:
                register = line.split()[-1].strip()
                self.stack.append(register)
                self.current_line += 1
                continue

            if "popq" in line:
                if self.stack:
                    self.stack.pop()
                self.current_line += 1
                continue

            # Instrucciones de control de flujo
            if "cmpl" in line:
                parts = line.split(',')
                compare_value = int(parts[0].split('$')[1].strip(), 16)
                offset = parts[1].strip().split('(')[0].strip()
                stack_value = self.stack_vars.get(offset, 0)
                self.compare_result = compare_value
                self.last_compare = stack_value  # Guardar el valor para comparaciones
                print(f"[DEBUG] Comparando {compare_value} con variable en stack ({stack_value})")
                self.current_line += 1
                continue

            if "jg" in line:
                target = line.split()[-1].strip()
                target_addr = self.get_jump_target_address(target)
                if target_addr is not None:
                    if self.compare_result < self.last_compare:
                        new_line = self.find_line_by_address(target_addr)
                        if new_line is not None:
                            print(f"[DEBUG] Salto a línea {new_line} (dirección {hex(target_addr)})")
                            self.current_line = new_line
                            continue
                self.current_line += 1
                continue

            if "jle" in line:
                target = line.split()[-1].strip()
                target_addr = self.get_jump_target_address(target)
                if target_addr is not None:
                    if self.last_compare <= self.compare_result:
                        new_line = self.find_line_by_address(target_addr)
                        if new_line is not None:
                            print(f"[DEBUG] Salto a línea {new_line} (dirección {hex(target_addr)})")
                            self.current_line = new_line
                            continue
                self.current_line += 1
                continue

            if "jmp" in line:
                target = line.split()[-1].strip()
                target_addr = self.get_jump_target_address(target)
                if target_addr is not None:
                    new_line = self.find_line_by_address(target_addr)
                    if new_line is not None:
                        print(f"[DEBUG] Salto incondicional a línea {new_line} (dirección {hex(target_addr)})")
                        self.current_line = new_line
                        continue
                self.current_line += 1
                continue

            if "incl" in line:
                if "(%rax)" in line:
                    self.x_position += 1
                    if self.pen_down:
                        self.handle_pen_down()
                    print(f"[DEBUG] Incrementando x a {self.x_position}")
                elif "(%rcx)" in line:
                    self.y_position += 1
                    if self.pen_down:
                        self.handle_pen_down()
                    print(f"[DEBUG] Incrementando y a {self.y_position}")
                elif "(%rsp)" in line:
                    offset = line.split('(')[0].strip().split()[-1]
                    if offset in self.stack_vars:
                        self.stack_vars[offset] += 1
                        print(f"[DEBUG] Incrementando variable en stack offset {offset} a {self.stack_vars[offset]}")
                self.current_line += 1
                self.render_canvas()
                continue

            # Procesamiento de movl para variables del stack
            if "movl" in line:
                if "rsp" in line or "esp" in line:
                    parts = line.split(',')
                    value = int(parts[0].split('$')[1].strip(), 16)
                    offset = parts[1].strip().split('(')[0].strip()
                    self.stack_vars[offset] = value
                    print(f"[DEBUG] Inicializando variable en stack offset {offset} = {value}")
                elif "esp" not in line:
                    value = int(line.split('$')[1].split(',')[0].strip(), 16)
                    register = line.split(',')[1].strip().strip('()')
                    var_type = self.get_current_register_type(register, self.current_line)

                    if var_type == "x_position":
                        old_x = self.x_position
                        self.x_position = value
                        print(f"[DEBUG] Inicializando x de {old_x} a {self.x_position}")

                    elif var_type == "y_position":
                        old_y = self.y_position
                        self.y_position = value
                        print(f"[DEBUG] Inicializando y de {old_y} a {self.y_position}")

                    self.render_canvas()

            elif "movabsq" in line:
                register = line.split(',')[-1].strip()
                var_type = self.get_current_register_type(register, self.current_line)
                if var_type:
                    print(f"[DEBUG] Usando registro {register} para {var_type}")

            elif "movb" in line:
                value = line.split('$')[1].split(',')[0].strip()
                register = line.split(',')[1].strip().strip('()')
                var_type = self.get_current_register_type(register, self.current_line)

                if var_type == "pen_down":
                    old_pen_state = self.pen_down
                    self.pen_down = value == "0x1"
                    state_change = "activando" if self.pen_down else "desactivando"
                    print(
                        f"[DEBUG] {state_change} pen_down={self.pen_down} en posición x={self.x_position}, y={self.y_position}"
                    )

                    if self.pen_down and not old_pen_state:
                        self.handle_pen_down()

                    self.render_canvas()

            elif "addl" in line:
                try:
                    value = int(line.split("$")[1].split(",")[0].strip(), 16)
                    register = line.split(',')[1].strip().strip('()')
                    var_type = self.get_current_register_type(register, self.current_line)

                    if var_type == "x_position":
                        old_x = self.x_position
                        self.x_position += value
                        print(f"[DEBUG] Moviendo x de {old_x} a {self.x_position}")

                        if self.pen_down:
                            print(f"[DEBUG] Dibujando línea horizontal de {old_x} a {self.x_position}")
                            self.draw_line_horizontal(old_x, self.x_position)
                        else:
                            print(f"[DEBUG] Movimiento en x sin dibujo: pen_down={self.pen_down}")

                    elif var_type == "y_position":
                        old_y = self.y_position
                        self.y_position += value
                        print(f"[DEBUG] Moviendo y de {old_y} a {self.y_position}")

                        if self.pen_down:
                            print(f"[DEBUG] Dibujando línea vertical de {old_y} a {self.y_position}")
                            self.draw_line_vertical(old_y, self.y_position)
                        else:
                            print(f"[DEBUG] Movimiento en y sin dibujo: pen_down={self.pen_down}")

                    self.render_canvas()
                except Exception as e:
                    print(f"[ERROR] Error procesando addl: {e} en línea: {line}")

            elif "mfence" in line:
                print("[DEBUG] Barrera de memoria - asegurando orden de operaciones")

            self.current_line += 1
    def get_stack_var(self):
        """Obtiene el valor actual de la variable en el stack que se está comparando"""
        # Buscar la variable más reciente en el stack
        if '0x4' in self.stack_vars:  # Esta es la variable que se usa en el while
            return self.stack_vars['0x4']
        return 0  #
    def handle_pen_down(self):
        """Maneja el evento de bajar el lápiz, dibujando en la posición actual"""
        if 0 <= self.x_position < len(self.canvas[0]) and 0 <= self.y_position < len(self.canvas):
            self.canvas[self.y_position][self.x_position] = "*"
            print(f"[DEBUG] Dibujando punto en x={self.x_position}, y={self.y_position}")

    def draw_line_vertical(self, y1, y2):
        """Dibuja una línea vertical desde y1 hasta y2 en la posición x actual"""
        if self.pen_down:
            start = min(y1, y2)
            end = max(y1, y2)
            for y in range(start, end + 1):
                if 0 <= self.x_position < len(self.canvas[0]) and 0 <= y < len(self.canvas):
                    self.canvas[y][self.x_position] = "*"
            print(f"[DEBUG] Línea vertical dibujada de y={start} a y={end}, x={self.x_position}")
        else:
            print(f"[DEBUG] No se dibuja línea porque pen_down está en {self.pen_down}")

    def draw_line_horizontal(self, x1, x2):
        """Dibuja una línea horizontal desde x1 hasta x2 en la posición y actual"""
        if self.pen_down:
            start = min(x1, x2)
            end = max(x1, x2)
            for x in range(start, end + 1):
                if 0 <= x < len(self.canvas[0]) and 0 <= self.y_position < len(self.canvas):
                    self.canvas[self.y_position][x] = "*"
            print(f"[DEBUG] Línea horizontal dibujada de x={start} a x={end}, y={self.y_position}")
        else:
            print(f"[DEBUG] No se dibuja línea porque pen_down está en {self.pen_down}")

    def render_canvas(self):
        print("\nEstado actual del canvas:")
        for row in self.canvas:
            print("".join(row))
        print(
            f"[DEBUG] Estado actual: pen_down={self.pen_down}, x_position={self.x_position}, y_position={self.y_position}")


if __name__ == "__main__":
    simulator = PencilSimulator("output.o")
    simulator.load_object()
    simulator.execute()