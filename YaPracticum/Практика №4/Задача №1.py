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
        :return: возвращается красивую строчку.
        """

        return f'Книжка {self.title} под авторством {self.author} {self.year} года выпуска.'