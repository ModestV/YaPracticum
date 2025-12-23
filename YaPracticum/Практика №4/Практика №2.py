class Vehicle:
    """
    Так называемое транспортное средство, но это класс
    """
    def __init__(self, infa):
        """
        Идёт инициализация информации
        :param infa: описание транспорта
        """
        self.infa = infa


class Car(Vehicle):
    """
    Так называемое транспортное средство, но это машина
    """

    def info(self):
        return f'Что я могу сказат о машине: {self.infa}'


class Airplane(Vehicle):
    """
    Так называемое транспортное средство, но это самолёт
    """

    def info(self):
        return f'Что я могу сказат о самолёте: {self.infa}'


class Ship(Vehicle):
    """
    Так называемое транспортное средство, но это корабль
    """

    def info(self):
        return f'Что я могу сказат о корабле: {self.infa}'


def vehicle_discription(vehicle):
    """
    выдаёт информацию, если хорошо попросить.
    :param vehicle: транспортное средство
    """
    return vehicle.info()


lamborgamar = Car("Это штука имеет четыре колеса и ездит по дорогам.")
print(vehicle_discription(lamborgamar))
Boing747 = Airplane("Здесь быстро но дорого преодалевает расстояние.")
print(vehicle_discription(Boing747))
Titanik = Ship("На таком месте меня вырвет 213801 раз.")
print(vehicle_discription(Titanik))


