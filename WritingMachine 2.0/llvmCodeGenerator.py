from llvmlite import ir, binding
import ctypes
import llvmlite.binding as llvm

class LLVMCodeGenerator:
    def __init__(self):
        # Inicializar LLVM
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # Crear módulo y tipos
        self.module = ir.Module(name="writing_machine_module")
        self.int_type = ir.IntType(32)
        self.void_type = ir.VoidType()
        self.bool_type = ir.IntType(1)
        
        # Crear builder
        self.builder = None
        
        # Tabla de símbolos para variables
        self.variables = {}
        
        # Declarar funciones de la máquina virtual
        self._declare_runtime_functions()

    def _declare_runtime_functions(self):
        """Declara las funciones base que necesitará nuestro lenguaje"""
        
        # Función para mover el lápiz
        move_type = ir.FunctionType(self.void_type, [self.int_type, self.int_type])
        self.move_func = ir.Function(self.module, move_type, name="move_to")
        
        # Función para subir/bajar el lápiz
        pen_type = ir.FunctionType(self.void_type, [self.bool_type])
        self.pen_up = ir.Function(self.module, pen_type, name="pen_up")
        self.pen_down = ir.Function(self.module, pen_type, name="pen_down")
        
        # Función para cambiar color
        color_type = ir.FunctionType(self.void_type, [self.int_type])
        self.change_color = ir.Function(self.module, color_type, name="change_color")

    def generate_procedure(self, name, params, body):
        """Genera código LLVM para un procedimiento"""
        # Crear tipos de parámetros
        param_types = [self.int_type for _ in params]
        
        # Crear tipo de función
        func_type = ir.FunctionType(self.void_type, param_types)
        
        # Crear función
        func = ir.Function(self.module, func_type, name=name)
        
        # Crear bloque de entrada
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        
        # Agregar parámetros a la tabla de símbolos
        self.variables.clear()
        for i, param in enumerate(params):
            alloca = self.builder.alloca(self.int_type, name=param)
            self.builder.store(func.args[i], alloca)
            self.variables[param] = alloca
            
        # Generar código para el cuerpo
        self.generate_body(body)
        
        # Agregar retorno
        self.builder.ret_void()

    def generate_body(self, body):
        """Genera código LLVM para el cuerpo de un procedimiento"""
        for statement in body:
            self.generate_statement(statement)

    def generate_statement(self, statement):
        """Genera código LLVM para una instrucción"""
        if isinstance(statement, dict):  # Asumiendo que el AST usa diccionarios
            if statement['type'] == 'move':
                x = self.generate_expression(statement['x'])
                y = self.generate_expression(statement['y'])
                self.builder.call(self.move_func, [x, y])
                
            elif statement['type'] == 'pen_down':
                self.builder.call(self.pen_down, [ir.Constant(self.bool_type, 1)])
                
            elif statement['type'] == 'pen_up':
                self.builder.call(self.pen_up, [ir.Constant(self.bool_type, 0)])
                
            elif statement['type'] == 'color':
                color = self.generate_expression(statement['value'])
                self.builder.call(self.change_color, [color])
                
            elif statement['type'] == 'assignment':
                value = self.generate_expression(statement['value'])
                var = self.variables[statement['variable']]
                self.builder.store(value, var)

    def generate_expression(self, expr):
        """Genera código LLVM para una expresión"""
        if isinstance(expr, (int, float)):
            return ir.Constant(self.int_type, int(expr))
            
        elif isinstance(expr, str):  # Variable
            ptr = self.variables[expr]
            return self.builder.load(ptr)
            
        elif isinstance(expr, dict):  # Operación
            left = self.generate_expression(expr['left'])
            right = self.generate_expression(expr['right'])
            
            if expr['op'] == '+':
                return self.builder.add(left, right)
            elif expr['op'] == '-':
                return self.builder.sub(left, right)
            elif expr['op'] == '*':
                return self.builder.mul(left, right)
            elif expr['op'] == '/':
                return self.builder.sdiv(left, right)

    def optimize_module(self):
        """Aplica optimizaciones al módulo"""
        pass_manager = binding.create_module_pass_manager()
        pass_manager.add_instruction_combining_pass()
        pass_manager.add_reassociate_pass()
        pass_manager.add_gvn_pass()
        pass_manager.add_cfg_simplification_pass()
        pass_manager.run(self.module)

    def generate_machine_code(self):
        """Genera el código de máquina final"""
        # Inicializar el motor de ejecución
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        
        # Optimizar el módulo
        self.optimize_module()
        
        # Generar código objeto
        obj = target_machine.emit_object(self.module)
        return obj