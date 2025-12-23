import requests

class Pokemon:
    """Класс покемона для хранения информации и проведения боев"""

    def __init__(self, pokemon_name: str):
        """
        Инициализация класса покемона.
        Загружает данные из PokeAPI при создании экземпляра.

        Args:
            pokemon_name (str): Имя покемона (в нижнем регистре)
        """

        self.name = pokemon_name.lower()
        try:
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{self.name}")
            response.raise_for_status()  # Проверка на ошибку HTTP
            self.pokeresponse = response.json()

            # Извлекаем основные характеристики
            self.hp = self.pokeresponse["stats"][0]["base_stat"]
            self.attack = self.pokeresponse["stats"][1]["base_stat"]
            self.types = [type_info["type"]["name"] for type_info in self.pokeresponse["types"]]
            self.abilities = [ability_info["ability"]["name"] for ability_info in self.pokeresponse["abilities"]]
            self.height = self.pokeresponse["height"]
            self.weight = self.pokeresponse["weight"]

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Не удалось загрузить данные для покемона '{pokemon_name}': {e}")

    def info(self):
        """Возвращает подробную информацию о покемоне в виде строки"""

        return f"""
Покемон: {self.name.capitalize()}
Типы: {', '.join(self.types)}
Способности: {', '.join(self.abilities)}
Рост: {self.height} (единицы: 0.1 м)
Вес: {self.weight} (единицы: 0.1 кг)
Текущее здоровье: {round(self.hp, 1)}
Сила атаки: {self.attack}"""

    def fight(self, other):
        """
        Устраивает битву между двумя покемонами.
        Покемоны сражаются в цикле, нанося урон друг другу.
        Побеждает тот, кто раньше снесёт противника.

        Args:
            other (Pokemon): Покемон-противник
        """

        print(f"\n--- НАЧИНАЕТСЯ БОЙ: {self.name.capitalize()} VS {other.name.capitalize()} ---")

        # Сбрасываем HP перед боем, чтобы можно было проводить несколько боев
        current_hp_self = self.hp
        current_hp_other = other.hp

        current_turn = self.name
        while current_hp_self > 0 and current_hp_other > 0:
            if current_turn == self.name:
                damage = round(self.attack * 0.2, 1)
                current_hp_other -= damage
                print(f"{current_turn.capitalize()} нанёс {other.name.capitalize()} {damage} урона. "
                      f"У того осталось: {round(current_hp_other, 1)} хп.")
            else:
                damage = round(other.attack * 0.2, 1)
                current_hp_self -= damage
                print(f"{current_turn.capitalize()} нанёс {self.name.capitalize()} {damage} урона. "
                      f"У того осталось: {round(current_hp_self, 1)} хп.")

            # Передача хода
            current_turn = self.name if current_turn == other.name else other.name

        # Определение победителя
        if current_hp_self > 0:
            winner = self.name
        else:
            winner = other.name

        print(f'\n--- В поединке победил {winner.capitalize()}! ---')

    def __str__(self):
        """Превращает класс в человекочитаемый вид (вызывает info)"""

        return self.info()


class TeamManager:
    """Менеджер команды покемонов"""

    def __init__(self):
        """Инициализация менеджера команды"""

        self.team = []

    def add_pokemon(self, pokemon_name: str):
        """
        Добавляет покемона в команду, если его там еще нет.

        Args:
            pokemon_name (str): Имя покемона для добавления
        """

        # Проверяем, есть ли уже такой покемон в команде
        for pokemon in self.team:
            if pokemon.name == pokemon_name.lower():
                print(f"Покемон '{pokemon_name.capitalize()}' уже есть в вашей команде!")
                return

        try:
            # Создаем нового покемона
            new_pokemon = Pokemon(pokemon_name)
            self.team.append(new_pokemon)
            print(f"Покемон '{new_pokemon.name.capitalize()}' успешно добавлен в команду!")
        except ValueError as e:
            print(e)

    def remove_pokemon(self, pokemon_name: str):
        """
        Удаляет покемона из команды по имени.

        Args:
            pokemon_name (str): Имя покемонa для удаления
        """

        for i, pokemon in enumerate(self.team):
            if pokemon.name == pokemon_name.lower():
                removed_pokemon = self.team.pop(i)
                print(f"Покемон '{removed_pokemon.name.capitalize()}' удалён из команды.")
                return

        print(f"Покемон '{pokemon_name.capitalize()}' не найден в вашей команде.")

    def view_team(self):
        """Просматривает подробную информацию обо всех покемонах в команде"""

        if not self.team:
            print("Ваша команда пуста.")
            return

        print("\n--- Ваша команда Pokémon ---")
        for i, pokemon in enumerate(self.team, 1):
            print(f"\n{i}. {pokemon.name.capitalize()}")
            print(pokemon.info())
        print("-----------------------------")

    def find_pokemon(self, pokemon_name: str):
        """
        Находит покемона в команде по имени и возвращает его.

        Args:
            pokemon_name (str): Имя покемона для поиска

        Returns:
            Pokemon or None: Экземпляр покемона или None, если не найден
        """

        for pokemon in self.team:
            if pokemon.name == pokemon_name.lower():
                return pokemon

        print(f"Покемон '{pokemon_name.capitalize()}' не найден в вашей команде.")
        return None

    def start_training_battle(self, pokemon1_name: str, pokemon2_name: str):
        """
        Устраивает тренировочный бой между двумя покемонами из команды.

        Args:
            pokemon1_name (str): Имя первого покемона
            pokemon2_name (str): Имя второго покемона
        """

        pokemon1 = self.find_pokemon(pokemon1_name)
        pokemon2 = self.find_pokemon(pokemon2_name)

        if pokemon1 and pokemon2:
            pokemon1.fight(pokemon2)
        else:
            print("Бой не может быть начат, так как один или оба покемона не найдены в команде.")


# =================== ОСНОВНАЯ ПРОГРАММА ===================
def main():
    """Основная функция для взаимодействия с пользователем"""

    manager = TeamManager()
    print("Добро пожаловать в Менеджер Команды Pokémon!")

    while True:
        print("\n=== МЕНЮ ===")
        print("1. Добавить покемона в команду")
        print("2. Удалить покемона из команды")
        print("3. Просмотреть всю команду")
        print("4. Найти покемона по имени")
        print("5. Устроить тренировочный бой")
        print("6. Выход")

        choice = input("Выберите действие (1-6): ").strip()

        if choice == '1':
            name = input("Введите имя покемона для добавления: ").strip()
            manager.add_pokemon(name)

        elif choice == '2':
            name = input("Введите имя покемона для удаления: ").strip()
            manager.remove_pokemon(name)

        elif choice == '3':
            manager.view_team()

        elif choice == '4':
            name = input("Введите имя покемона для поиска: ").strip()
            found = manager.find_pokemon(name)
            if found:
                print("\nНайденный покемон:")
                print(found)

        elif choice == '5':
            name1 = input("Введите имя первого покемона: ").strip()
            name2 = input("Введите имя второго покемона: ").strip()
            manager.start_training_battle(name1, name2)

        elif choice == '6':
            print("Спасибо за использование Менеджера Команды Pokémon! До свидания!")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите число от 1 до 6.")


if __name__ == "__main__":
    main()