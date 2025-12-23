import requests

# Шаг 1: Отправить GET-запрос на endpoint /pokemon, чтобы получить список первых 20 покемонов
response = requests.get("https://pokeapi.co/api/v2/pokemon/?limit=20")
data = response.json()

# Шаг 2: Извлечь имена покемонов из ответа и вывести их список
pokemon_names = [pokemon["name"] for pokemon in data["results"]]
print("Список первых 20 покемонов:")
for name in pokemon_names:
    print(f"- {name}")

# Шаг 3: Ввести с помощью input() название одного из покемонов
chosen_pokemon_name = input("\nВведите название одного из покемонов (например, clefairy): ").strip().lower()

# Шаг 4: Отправить GET-запрос, чтобы получить полную информацию о выбранном покемоне
pokemon_response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{chosen_pokemon_name}")
if pokemon_response.status_code != 200:
    print(f"Покемон '{chosen_pokemon_name}' не найден.")
else:
    pokemon_data = pokemon_response.json()

    # Шаг 5: Извлечь и вывести следующие данные о введенном покемоне:
    name = pokemon_data["name"].capitalize()
    types = [type_info["type"]["name"] for type_info in pokemon_data["types"]]
    weight = pokemon_data["weight"]
    height = pokemon_data["height"]
    abilities = [ability_info["ability"]["name"] for ability_info in pokemon_data["abilities"]]

    print(f"\nИнформация о покемоне {name}:")
    print(f"  Имя: {name}")
    print(f"  Тип: {', '.join(types)}")
    print(f"  Вес: {weight} (единицы: 0.1 кг)")
    print(f"  Рост: {height} (единицы: 0.1 м)")
    print(f"  Способности: {', '.join(abilities)}")