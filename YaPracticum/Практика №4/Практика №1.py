class Employee:
    """
    Так называемый работник так называемой компании.
    """

    def __init__(self,money,percent):
        """
        Инициализируем деньгу и процент с зп
        :param money:
        :param percent:
        """
        self.money = money
        self.percent = percent

    def money_get(self):
        """
        Считаем оклад работяги с завода.
        :return: возвращает деньгу умноженную на процент
        """
        return self.money * (self.percent / 100)


class Manager(Employee):

    def __init__(self):
        super().__init__(100,99)


class Developer(Employee):
    """
    Так называемый разраб-работяга.
    """
    def __init__(self):
        super().__init__(100,1)

Artem = Manager()
Nikita = Developer()
print(Nikita.money_get())
print(Artem.money_get())