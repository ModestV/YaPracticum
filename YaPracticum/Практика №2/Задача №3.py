def print_pack_report(number):
    while number>0:
        """
        Пока число положительное проверяем все варианты, когда оно кратно трём и/или пяти, или вовсе не кратно.
        От этого разница вывод программы. В конце каждой итерации вычитаем единицу из числа.
        """
        if number%3==0 and number%5==0:
            print(f'{number} - расфасуем по 3 или по 5')
        elif number%5==0:
            print(f'{number} - расфасуем по 5')
        elif number%3==0:
            print(f'{number} - расфасуем по 3')
        else:
            print(f'{number} - не заказываем!')
        number -= 1


print(print_pack_report(30))