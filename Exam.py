from abc import ABC, abstractmethod


class Shape(ABC):
    """Базовый класс для примитивов"""

    def __init__(self, color: str) -> None:
        self.color = color

    @abstractmethod
    def move(self, dx: float, dy: float) -> None:
        """Перемещает фигуру на заданные значения"""
        pass

    def set_color(self, color: str) -> None:
        """Изменяет цвет фигуры."""
        self.color = color

    @abstractmethod
    def draw(self) -> None:
        """Отрисовывает фигуру"""
        pass


class Circle(Shape):
    """Класс для круга"""

    def __init__(self, x: float, y: float, radius: float, color: str) -> None:
        super().__init__(color)
        self.x = x
        self.y = y
        self.radius = radius

    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    def draw(self) -> None:
        pass


class Rectangle(Shape):
    """Класс для прямоугольника"""

    def __init__(self, x: float, y: float, width: float, height: float, color: str) -> None:
        super().__init__(color)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    def draw(self) -> None:
        pass


class Line(Shape):
    """Класс для линии"""

    def __init__(self, x1: float, y1: float, x2: float, y2: float, color: str) -> None:
        super().__init__(color)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def move(self, dx: float, dy: float) -> None:
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy

    def draw(self) -> None:
        pass


class Canvas:
    """Холст для хранения фигур"""

    def __init__(self) -> None:
        self.shapes = []

    def add_shape(self, shape: Shape) -> None:
        """Добавляет фигуру на холст"""
        self.shapes.append(shape)

    def remove_shape(self, shape: Shape) -> None:
        """Удаляет фигуру с холста"""
        if shape in self.shapes:
            self.shapes.remove(shape)


class EditorCommand(ABC):
    """Базовый класс для команд редактора"""

    def __init__(self) -> None:
        self.shape = None
        self.args = ()

    @abstractmethod
    def execute(self, canvas: Canvas, shape: Shape, *args) -> None:
        """Выполняет команду"""
        pass

    @abstractmethod
    def undo(self, canvas: Canvas) -> None:
        """Отменяет команду"""
        pass


class AddShapeCommand(EditorCommand):
    """Команда добавления фигуры"""

    def execute(self, canvas: Canvas, shape: Shape, *args) -> None:
        self.shape = shape
        canvas.add_shape(shape)

    def undo(self, canvas: Canvas) -> None:
        if self.shape:
            canvas.remove_shape(self.shape)


class RemoveShapeCommand(EditorCommand):
    """Команда удаления фигуры"""

    def execute(self, canvas: Canvas, shape: Shape, *args) -> None:
        self.shape = shape
        canvas.remove_shape(shape)

    def undo(self, canvas: Canvas) -> None:
        if self.shape:
            canvas.add_shape(self.shape)


class MoveShapeCommand(EditorCommand):
    """Команда перемещения фигуры"""

    def execute(self, canvas: Canvas, shape: Shape, *args) -> None:
        if len(args) < 2:
            print("Ошибка! Требуются dx и dy для перемещения...")
        else:
            dx, dy = args[0], args[1]
            self.shape = shape
            self.args = (dx, dy)
            shape.move(dx, dy)

    def undo(self, canvas: Canvas) -> None:
        if self.shape and len(self.args) >= 2:
            dx, dy = self.args
            self.shape.move(-dx, -dy)


class ChangeColorCommand(EditorCommand):
    """Команда изменения цвета фигуры"""

    def __init__(self) -> None:
        super().__init__()
        self.old_color = ""

    def execute(self, canvas: Canvas, shape: Shape, *args) -> None:
        if not args:
            print("Ошибка! Требуется новый цвет...")
        else:
            new_color = args[0]
            self.shape = shape
            self.old_color = shape.color
            shape.set_color(new_color)

    def undo(self, canvas: Canvas) -> None:
        if self.shape:
            self.shape.set_color(self.old_color)


class EditorHistory:
    """Менеджер истории операций"""

    def __init__(self) -> None:
        self.undo_stack = []
        self.redo_stack = []

    def execute_command(self, command: EditorCommand, canvas: Canvas, shape: Shape, *args) -> None:
        """Выполняет команду и сохраняет её в истории"""
        command.execute(canvas, shape, *args)
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo(self, canvas: Canvas) -> None:
        """Отменяет последнюю команду"""
        if not self.undo_stack:
            return
        command = self.undo_stack.pop()
        command.undo(canvas)
        self.redo_stack.append(command)

    def redo(self, canvas: Canvas) -> None:
        """Повторяет последнюю отменённую команду"""
        if not self.redo_stack:
            return
        command = self.redo_stack.pop()
        if command.shape is not None:
            command.execute(canvas, command.shape, *command.args)
        self.undo_stack.append(command)



canvas = Canvas()
history = EditorHistory()

while True:
    print("\nМеню:")
    print("1. Добавить круг")
    print("2. Добавить прямоугольник")
    print("3. Добавить линию")
    print("4. Удалить фигуру")
    print("5. Переместить фигуру")
    print("6. Изменить цвет фигуры")
    print("7. Undo")
    print("8. Redo")
    print("9. Выход")
    choice = input("Выберите действие: ").strip()

    if choice == '1':
        try:
            x = float(input("x: "))
            y = float(input("y: "))
            radius = float(input("Радиус: "))
            color = input("Цвет: ")
            shape = Circle(x, y, radius, color)
            command = AddShapeCommand()
            history.execute_command(command, canvas, shape)
            print("Круг добавлен.")
        except ValueError:
            print("Ошибка ввода данных.")

    elif choice == '2':
        try:
            x = float(input("x: "))
            y = float(input("y: "))
            width = float(input("Ширина: "))
            height = float(input("Высота: "))
            color = input("Цвет: ")
            shape = Rectangle(x, y, width, height, color)
            command = AddShapeCommand()
            history.execute_command(command, canvas, shape)
            print("Прямоугольник добавлен.")
        except ValueError:
            print("Ошибка ввода данных.")

    elif choice == '3':
        try:
            x1 = float(input("x1: "))
            y1 = float(input("y1: "))
            x2 = float(input("x2: "))
            y2 = float(input("y2: "))
            color = input("Цвет: ")
            shape = Line(x1, y1, x2, y2, color)
            command = AddShapeCommand()
            history.execute_command(command, canvas, shape)
            print("Линия добавлена.")
        except ValueError:
            print("Ошибка ввода данных.")

    elif choice == '4':
        if not canvas.shapes:
            print("Нет фигур для удаления.")
            continue
        print("Список фигур:")
        for i, shape in enumerate(canvas.shapes):
            print(f"{i}: {type(shape).__name__}")
        try:
            idx = int(input("Индекс фигуры для удаления: "))
            if 0 <= idx < len(canvas.shapes):
                shape = canvas.shapes[idx]
                command = RemoveShapeCommand()
                history.execute_command(command, canvas, shape)
                print("Фигура удалена.")
            else:
                print("Неверный индекс.")
        except ValueError:
            print("Введите число.")

    elif choice == '5':
        if not canvas.shapes:
            print("Нет фигур для перемещения.")
            continue
        print("Список фигур:")
        for i, shape in enumerate(canvas.shapes):
            print(f"{i}: {type(shape).__name__}")
        try:
            idx = int(input("Индекс фигуры: "))
            if 0 <= idx < len(canvas.shapes):
                dx = float(input("dx: "))
                dy = float(input("dy: "))
                shape = canvas.shapes[idx]
                command = MoveShapeCommand()
                history.execute_command(command, canvas, shape, dx, dy)
                print("Фигура перемещена.")
            else:
                print("Неверный индекс.")
        except ValueError:
            print("Ошибка ввода данных.")

    elif choice == '6':
        if not canvas.shapes:
            print("Нет фигур для изменения цвета.")
            continue
        print("Список фигур:")
        for i, shape in enumerate(canvas.shapes):
            print(f"{i}: {type(shape).__name__}, цвет: {shape.color}")
        try:
            idx = int(input("Индекс фигуры: "))
            if 0 <= idx < len(canvas.shapes):
                new_color = input("Новый цвет: ")
                shape = canvas.shapes[idx]
                command = ChangeColorCommand()
                history.execute_command(command, canvas, shape, new_color)
                print("Цвет изменен.")
            else:
                print("Неверный индекс.")
        except ValueError:
            print("Ошибка ввода данных.")

    elif choice == '7':
        history.undo(canvas)
        print("Undo выполнено.")

    elif choice == '8':
        history.redo(canvas)
        print("Redo выполнено.")

    elif choice == '9':
        print("Выход.")
        break

    else:
        print("Другого выбора нету...")
