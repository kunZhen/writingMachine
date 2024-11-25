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

        # Encontrar el mapeo más reciente antes de la línea actual
        mappings = self.current_register_map[register]
        current_mapping = None
        min_distance = float('inf')

        for mapping in mappings:
            distance = line_num - mapping['position']
            if 0 <= distance < min_distance:
                min_distance = distance
                current_mapping = mapping

        return current_mapping['symbol'] if current_mapping else None

    def execute(self):
        print("\nIniciando simulación del lápiz...\n")

        for i, line in enumerate(self.instructions):
            if not line.strip() or "file format" in line or "Disassembly" in line:
                continue

            print(f"[DEBUG] Procesando línea {i}: {line}")

            if "movabsq" in line:
                register = line.split(',')[-1].strip()
                var_type = self.get_current_register_type(register, i)
                if var_type:
                    print(f"[DEBUG] Usando registro {register} para {var_type}")

            elif "movl" in line:
                # Extraer el valor y el registro
                value = int(line.split('$')[1].split(',')[0].strip(), 16)
                register = line.split(',')[1].strip().strip('()')
                var_type = self.get_current_register_type(register, i)

                if var_type == "x_position":
                    old_x = self.x_position
                    self.x_position = value
                    print(f"[DEBUG] Inicializando x de {old_x} a {self.x_position}")

                elif var_type == "y_position":
                    old_y = self.y_position
                    self.y_position = value
                    print(f"[DEBUG] Inicializando y de {old_y} a {self.y_position}")

                self.render_canvas()

            elif "movb" in line:
                value = line.split('$')[1].split(',')[0].strip()
                register = line.split(',')[1].strip().strip('()')
                var_type = self.get_current_register_type(register, i)

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
                    var_type = self.get_current_register_type(register, i)

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