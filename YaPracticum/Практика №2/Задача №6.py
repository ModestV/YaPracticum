"""
Функция которая склеивает поле field в единую картинку, к сожалению фантазии хватило только на принты.
Принимает в себя errors, они же количество ошибок (максимум 11), чтобы потом передать это количество
функции mistakes, которая в свою очередь видоизменяет поле по количеству ошибок, здесь же её и использование.
"""


def the_hanged_display(errors):
    mistakes(errors)
    print(''.join(field[0]))
    print(''.join(field[1]))
    print(''.join(field[2]))
    print(''.join(field[3]))
    print(''.join(field[4]))
    print(''.join(field[5]))
    print(''.join(field[6]))
    print(''.join(field[7]))
    print(''.join(field[8]))
    print(''.join(field[9]))

    """
    Фукнция о функционале которой было оговорено ранее, меняет поле по ошибкам.
    """


def mistakes(counts_mistakes):
    if counts_mistakes >= 1:
        field[3][4] = field[4][4] = field[5][4] = field[6][4] = field[7][4] = '|'
    if counts_mistakes >= 2:
        field[8][3] = field[8][4] = field[8][5] = field[8][6] = field[8][7] = '_'
    if counts_mistakes >= 3:
        field[2][3] = field[2][4] = field[2][5] = field[2][6] = field[2][7] = field[2][8] = field[2][9] = '-'
    if counts_mistakes >= 4:
        field[3][5] = '/'
    if counts_mistakes >= 5:
        field[3][9] = '|'
    if counts_mistakes >= 6:
        field[4][9] = 'o'
    if counts_mistakes >= 7:
        field[5][9] = '0'
    if counts_mistakes >= 8:
        field[5][8] = '/'
    if counts_mistakes >= 9:
        field[5][10] = '|'
    if counts_mistakes >= 10:
        field[6][8] = '/'
    if counts_mistakes >= 11:
        field[6][9] = '|'


""" Визуальное отображение завершённого висельника, как он должен быть.
______________ 0
|            | 1  
|  _______   | 2
|   |/   |   | 3
|   |    o   | 4
|   |   /0|  | 5
|   |   /|   | 6
|   |        | 7
|  ‾‾‾‾‾     | 8 
|____________| 9
01234567891234
"""

# Само поле, на котором происходят визуальные изменения с висельником.
field = [
    ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|'],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|'],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|'],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|'],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|'],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|'],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|'],
    ['|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|'],
    ['|', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '|'],
]

err = 0  # Счётчик ошибок, изначально ошибок нет.
guessing_word = input('Загадайте слово: ').lower()  # Получаем загаданное слово и переводим его в нижний регистр.
original_guess = guessing_word  # Сохраняем изначальное слово для дальнейшего сравнения
new_string = '_' * len(guessing_word)  # Создаём слово, состоящее ищ "_" для визуального представления в угадывании.
using_letters = []  # Пустой список для использованных букв, помогает в игре.
percent = (err * 100 // 11)  # Процент висельник, только в конце игры выводится. Только для красоты и статистики.

while err < 11:  # Игра идёт до тех пор, пока ошибок меньше 11, после получения 11-ой ошибка игрок проигрывает.

    if err >= 11:  # Исход, если игрок проиграл.
        print('\n\nК сожалению, вы проиграли!')
        print('Вы использовали буквы:', using_letters)
        print('Текущий прогресс:', percent, '%')
        the_hanged_display(err)
        break

    if new_string == original_guess:  # Исход, если игрок выиграл.
        print('\n\nПоздравляем, вы выиграли!')
        print('Вы использовали буквы:', using_letters)
        print('Текущий прогресс:', percent, '%')
        the_hanged_display(err)
        break

    # Каждую итерацию в цикле вводится букву, показываются использованные и строка, происходят промежуточные вычисления.
    print('\nУгадайте букву!\n')
    print('Текущая строка: ', new_string)
    print('Вы использовали буквы:', using_letters)
    guessing_letter = input('Напишите букву: ').lower()
    using_letters.append(guessing_letter)
    percent = (err * 100 // 11)

    # Если угаданная буква была в загаданном слове, то в угадываемом слове появляются эта(и) буква(ы) на соответствующих
    # местах, а в изначальном слове угаданные буквы заменяются на "_"
    if guessing_letter in guessing_word:
        while guessing_letter in guessing_word:
            letter_index = guessing_word.index(guessing_letter)
            new_string = new_string[:letter_index] + guessing_letter + new_string[letter_index + 1:]
            guessing_word = guessing_word.replace(guessing_letter, '_', 1)
    else:
        err += 1
    the_hanged_display(err)  # В конце каждой итерации показывается текущий прогресс в Висельнике визуально.