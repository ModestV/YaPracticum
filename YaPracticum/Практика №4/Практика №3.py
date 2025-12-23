class Product:
    """
    Класс Product описывает товар в онлайн-магазине.
    """

    def __init__(self, name, price, stock, category):
        """
        Инициализация товара.

        :param name: название товара
        :param price: цена товара
        :param stock: количество на складе
        :param category: категория товара
        """
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category

    def is_available(self, quantity):
        """
        Проверяет, есть ли нужное количество товара на складе.
        """
        return self.stock >= quantity

    def reduce_stock(self, quantity):
        """
        Уменьшает количество товара на складе.
        """
        if quantity <= self.stock:
            self.stock -= quantity


class ShoppingCart:
    """
    Класс ShoppingCart отвечает за корзину покупок.
    """

    def __init__(self):
        """
        Инициализация пустой корзины.
        """
        self.items = {}  # product -> quantity

    def add_product(self, product, quantity):
        """
        Добавляет товар в корзину.
        """
        if product.is_available(quantity):
            if product in self.items:
                self.items[product] += quantity
            else:
                self.items[product] = quantity
        else:
            print("Недостаточно товара на складе")

    def remove_product(self, product):
        """
        Удаляет товар из корзины.
        """
        if product in self.items:
            del self.items[product]

    def update_quantity(self, product, quantity):
        """
        Обновляет количество товара в корзине.
        """
        if product in self.items and product.is_available(quantity):
            self.items[product] = quantity

    def get_total_price(self):
        """
        Возвращает общую стоимость товаров в корзине.
        """
        total = 0
        for product, quantity in self.items.items():
            total += product.price * quantity
        return total


class Order:
    """
    Класс Order описывает заказ пользователя.
    """

    def __init__(self, cart, discount=0, tax=0.2):
        """
        Инициализация заказа.

        :param cart: объект корзины
        :param discount: скидка (в процентах)
        :param tax: налог
        """
        self.cart = cart
        self.discount = discount
        self.tax = tax

    def calculate_total(self):
        """
        Рассчитывает итоговую стоимость с учетом скидки и налога.
        """
        total = self.cart.get_total_price()
        total -= total * (self.discount / 100)
        total += total * self.tax
        return total

    def place_order(self):
        """
        Оформляет заказ и уменьшает количество товаров на складе.
        """
        for product, quantity in self.cart.items.items():
            product.reduce_stock(quantity)
        return self.calculate_total()


class Customer:
    """
    Класс Customer описывает покупателя.
    """

    def __init__(self, name, email):
        """
        Инициализация покупателя.
        """
        self.name = name
        self.email = email
        self.order_history = []

    def make_order(self, cart, discount=0):
        """
        Создает заказ и добавляет его в историю заказов.
        """
        order = Order(cart, discount)
        total_price = order.place_order()
        self.order_history.append(order)
        return total_price



# product1 = Product("Книга", 500, 10, "Образование")
# product2 = Product("Наушники", 3000, 5, "Электроника")
#
# cart = ShoppingCart()
# cart.add_product(product1, 2)
# cart.add_product(product2, 1)
#
# customer = Customer("Иванушка", "ivandurak@random.com")
# total = customer.make_order(cart, discount=10)
#
# print("Итоговая стоимость заказа:", total)
