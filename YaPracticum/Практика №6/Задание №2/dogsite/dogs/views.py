import requests
from django.shortcuts import render

def get_all_breeds():
    """Функция, которая использует метод GET и возвращает список всех пород собак в формате нумерованного списка"""
    try:
        response = requests.get("https://dog.ceo/api/breeds/list/all")
        response.raise_for_status()
        data = response.json()

        # Извлекаем список всех пород
        all_breeds = []
        for breed, subbreeds in data['message'].items():
            if len(subbreeds) == 0:
                all_breeds.append(breed)
            else:
                for subbreed in subbreeds:
                    all_breeds.append(f"{breed}/{subbreed}")
        return all_breeds
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении списка пород: {e}")
        return []

def dogs_list_view(request):
    """Представление для отображения списка всех пород"""
    breeds = get_all_breeds()
    context = {
        'breeds': breeds,
    }
    return render(request, 'dogs/dogs_viewer.html', context)

def dogs_images_view(request):
    """Представление для отображения изображений выбранных пород"""
    if request.method == 'POST':
        # Получаем введенные породы из POST-запроса
        breeds_input = request.POST.get('breeds', '').strip()
        if breeds_input:
            # Разделяем введенные породы по запятой и убираем лишние пробелы
            selected_breeds = [breed.strip() for breed in breeds_input.split(',') if breed.strip()]
        else:
            selected_breeds = []
    else:
        # Если это GET-запрос, просто отображаем форму
        selected_breeds = []

    images_data = []
    for breed in selected_breeds:
        try:
            # Запрос к API для получения изображения породы
            image_response = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random")
            image_response.raise_for_status()
            image_data = image_response.json()
            images_data.append({
                'breed': breed,
                'image_url': image_data['message']
            })
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении изображения для породы {breed}: {e}")
            images_data.append({
                'breed': breed,
                'image_url': None,
                'error': f"Не удалось загрузить изображение для {breed}"
            })

    context = {
        'selected_breeds': selected_breeds,
        'images_data': images_data,
    }
    return render(request, 'dogs/dogs_viewer.html', context)