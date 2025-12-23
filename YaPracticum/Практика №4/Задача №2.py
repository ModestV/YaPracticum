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

class Ebook(Book):
    def __init__(self, title, author, year, format):
        """
        Так называемый наследственный класс книженции, было бы смешнее
        если бы задание было про электронные баллы, который получит каждый.

        :param title: тут названьице книженции.
        :param author: тут автор сего произведения.
        :param year: год выпуска этого творения.
        :param format: формат книжки!
        """
        super().__init__(title, author, year)
        self.format = format


    def info(self) -> str:
        """
        Переделанынй, переосмысленный метод, который всё также возвращает инфу.
        """
        return f'Книжка {self.title} под авторством {self.author} {self.year} года выпуска, а ещё она {self.format}'
