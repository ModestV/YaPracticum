class Book:
    def __init__(self, title, author, year):
        """
        Так называемый класс для книг, да.
        :param title: тут названьице книженции.
        :param author: тут автор сего произведения.
        :param year: год выпуска этого творения.
        """
        self.title = title
        self.author = author
        self.year = year

    def info(self) -> str:
        """
        Так называемый метод для возвращаения сведений о книженции.
        """
        return f'Книжка {self.title} под авторством {self.author} {self.year} года выпуска.'

    def __str__(self):
        """
        Магический метод, который вызывается при выводе объекта через print().
        """
        return f'{self.title} — {self.author} ({self.year})'

    def __eq__(self, other):
        """
        Магический метод для сравнения двух книг.
        """
        if not isinstance(other, Book):
            return False
        return (
            self.title == other.title and
            self.author == other.author and
            self.year == other.year
        )

    @property
    def age(self):
        """
        Свойство, возвращающее возраст книги.
        """
        from datetime import datetime
        current_year = datetime.now().year
        return current_year - self.year

    @age.setter
    def age(self, value):
        """
        Сеттер для свойства age.
        Меняет год выпуска книги.
        """
        from datetime import datetime
        current_year = datetime.now().year
        self.year = current_year - value

    @classmethod
    def from_string(cls, data_string):
        """
        Классовый метод для создания книги из строки.
        Ожидаемый формат: 'Название;Автор;Год'
        """
        title, author, year = data_string.split(';')
        return cls(title, author, int(year))


class Ebook(Book):
    def __init__(self, title, author, year, format):
        """
        Так называемый наследственный класс книженции, было бы смешнее
        если бы задание было про электронные баллы, который получит каждый.
        """
        super().__init__(title, author, year)
        self.format = format

    def info(self) -> str:
        """
        Переделанынй, переосмысленный метод, который всё также возвращает инфу.
        """
        return f'Книжка {self.title} под авторством {self.author} {self.year} года выпуска, а ещё она {self.format}'
