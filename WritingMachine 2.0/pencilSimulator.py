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
        last_register = None

        for i, line in enumerate(self.instructions):
            if "movabsq" in line:
                last_register = line.split(',')[-1].strip()
                print(f"[DEBUG] Encontrado registro: {last_register}")

            elif "IMAGE_REL_AMD64_ADDR64" in line and last_register:
                symbol = line.strip().split()[-1]
                self.current_register_map[last_register] = symbol
                print(f"[DEBUG] Mapeando registro {last_register} a {symbol}")
                last_register = None

        print(f"[DEBUG] Mapa de registros final: {self.current_register_map}")

    def execute(self):
        print("\nIniciando simulación del lápiz...\n")

        for line in self.instructions:
            if not line.strip() or "file format" in line or "Disassembly" in line:
                continue

            print(f"[DEBUG] Procesando línea: {line}")

            if "movabsq" in line:
                register = line.split(',')[-1].strip()
                var_type = self.current_register_map.get(register)
                if var_type:
                    print(f"[DEBUG] Usando registro {register} para {var_type}")

            elif "movb" in line:
                # Extraer el valor y el registro
                value = line.split('$')[1].split(',')[0].strip()
                register = line.split(',')[1].strip().strip('()')
                var_type = self.current_register_map.get(register)

                if var_type == "pen_down":
                    old_pen_state = self.pen_down
                    self.pen_down = value == "0x1"
                    state_change = "activando" if self.pen_down else "desactivando"
                    print(f"[DEBUG] {state_change} pen_down={self.pen_down} en posición x={self.x_position}")

                    if self.pen_down and not old_pen_state:
                        self.handle_pen_down()

                    self.render_canvas()

            elif "addl" in line:
                try:
                    value = int(line.split("$")[1].split(",")[0].strip(), 16)
                    register = line.split(',')[1].strip().strip('()')
                    var_type = self.current_register_map.get(register)

                    if var_type == "x_position":
                        old_x = self.x_position
                        self.x_position += value
                        print(f"[DEBUG] Moviendo x de {old_x} a {self.x_position}")

                        if self.pen_down:
                            print(f"[DEBUG] Dibujando línea de {old_x} a {self.x_position}")
                            self.draw_line(old_x, self.x_position)
                        else:
                            print(f"[DEBUG] Movimiento sin dibujo: pen_down={self.pen_down}")

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

    def draw_line(self, x1, x2):
        """Dibuja una línea horizontal desde x1 hasta x2 en la posición y actual"""
        if self.pen_down:
            start = min(x1, x2)
            end = max(x1, x2)
            for x in range(start, end + 1):
                if 0 <= x < len(self.canvas[0]) and 0 <= self.y_position < len(self.canvas):
                    self.canvas[self.y_position][x] = "*"
            print(f"[DEBUG] Línea dibujada de x={start} a x={end}, y={self.y_position}")
        else:
            print(f"[DEBUG] No se dibuja línea porque pen_down está en {self.pen_down}")

    def render_canvas(self):
        print("\nEstado actual del canvas:")
        for row in self.canvas:
            print("".join(row))
        print(f"[DEBUG] Estado actual: pen_down={self.pen_down}, x_position={self.x_position}")


# Ejemplo de uso
if __name__ == "__main__":
    simulator = PencilSimulator("output.o")
    simulator.load_object()
    simulator.execute()