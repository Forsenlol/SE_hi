import matplotlib.pyplot as plt
import matplotlib as mp
import numpy as np

def graphs(name, user_answers = [2,3,4,5,1,3,4],
            subjects = ['Матанализ', 'Линейка', 'Комбинаторика', 'Теорвер', 'Python', 'C++', 'Алгоритмы']):

    """В функцию передавать количество правильных ответов и названия предметов сответственно"""

    number_of_questions = 5

    fig, ax = plt.subplots(figsize=(15,15))

    # set width of bar
    barWidth = 0.8

    data_normalizer = mp.colors.Normalize()
    color_map = mp.colors.LinearSegmentedColormap(
        "my_map",
        {
            "red": [(0, 1.0, 1.0),
                    (1.0, .5, .5)],
            "green": [(0, 0.5, 0.5),
                      (1.0, 0, 0)],
            "blue": [(0, 0.50, 0.5),
                     (1.0, 0.5, 0)]
        }
    )

    # Plot a bar graph:
    ax.bar(
        subjects,
        user_answers,
        width = barWidth,
        align="center",
        color=color_map(data_normalizer(user_answers))
    )

    ax.set_xticklabels(subjects, fontsize = 30)
    ax.set_ylim([0, 5])
    ax.set_yticklabels(list(range(number_of_questions + 1)), fontsize = 30)

    ax.set_title("ВАШИ РЕЗУЛЬТАТЫ", fontsize = 50)
    ax.yaxis.grid(True)
    
    # СОХРАНЕНИЕ КАРТИНКИ
    plt.savefig(name, dpi = 300)