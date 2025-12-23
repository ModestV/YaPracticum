def check_winners(scores_of_members, score_of_student):
    sorted_scores = sorted(scores_of_members, reverse=True)  # Создаём отсортированный по убыванию список баллов.
    if score_of_student in sorted_scores[0:3]:  # Если балл целевого студента есть в первых трёх местах, то он выиграл.
        print('Вы в тройке победителей!')
    else:
        print('Вы не прошли в тройку победителей.')


count_of_members = int(input('Сколько участников? '))
scores = []  # Объявляется пустой список, куда будут записываться баллы участников.

for i in range(count_of_members):
    scores.append(int(input('Введите балл участника: ')))  # Вводится кол-во баллов, равное кол-ву участников.

student_score = int(input('Введите ваш бал: '))  # Вводится балл, на который ориентируется программа.
print(check_winners(scores, student_score))