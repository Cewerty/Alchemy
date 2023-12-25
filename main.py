import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

import typer
from typing_extensions import Annotated, Optional
from chempy import Substance
from chempy.chemistry import Reaction, Species, balance_stoichiometry
from chemlib import Compound
from mendeleev import element
from translate import Translator
from random import choice

from colorama import init


translator = Translator(to_lang='ru')
init()
app = typer.Typer()


def is_keys(keys: list):
    for i in range(len(keys)):
        if keys[i].istitle() or keys[i].isnumeric():
            return True
        else:
            return False


def is_element(subs: str):
    for i in range(len(subs)):
        if subs[i].isalpha():
            return True
        else:
            return False


@app.command()
def about_element(user_element: Annotated[str, typer.Argument()] = None):
    """
    Команда, выводящяя всю основную информацию про химический элемент.
    """
    if user_element is None:
        std_elements = choice(['F', 'Na', 'Ag', 'Cl'])
        user_element = element(str(std_elements))
    else:
        user_element = element(user_element)
    main_element = [('Основные параметры', 'Параметр'),
                    ('Символ', user_element.symbol),
                    ('Название', translator.translate(user_element.name)),
                    ('Радиус', str(user_element.atomic_radius) + " pm"),
                    ('Электронные уровни', user_element.econf),
                    ('Массовое число', user_element.mass_number),
                    ("Атомный объём",
                     str(user_element.atomic_volume) + ' см^2/моль'),
                    ('Атомное число', user_element.atomic_number),
                    ('Радиактивность', user_element.is_radioactive),
                    ('Менделеево число', user_element.mendeleev_number),]
    place_element = [('Местоположение элемента', 'Параметр'),
                     ("Номер", user_element.atomic_number),
                     ("Группа", user_element.group.symbol),
                     ("Период", user_element.period),
                     ("Ряд", translator.translate(user_element.series)),
                     ("Блок элемента", user_element.block),]
    about_element = [('Об этом элементе', 'Параметр'),
                     ('Описание',
                      translator.translate(user_element.description)),
                     ('Применение', translator.translate(user_element.uses)),
                     ('Источники', translator.translate(user_element.sources)),
                     ('Место открытия',
                      translator.translate(user_element.discovery_location)),
                     ('Первооткрыватели', user_element.discoverers),
                     ('Год открытия', user_element.discovery_year),]
    adudance_element = [('Содержание элемента в природе', 'Параметры'),
                        ('Содержание предмета в земле',
                         str(user_element.abundance_crust) + ' мг/кг'),
                        ('Содержание предмета в воде',
                         str(user_element.abundance_sea) + ' мг/л'),
                        ('Геохимический класс',
                         translator.translate(user_element.geochemical_class)),
                        ]
    main_df = pd.DataFrame(main_element)
    place_df = pd.DataFrame(place_element)
    about_df = pd.DataFrame(about_element)
    adudance_element = pd.DataFrame(adudance_element)
    print(tabulate(main_df,
                   stralign='center',
                   showindex=False,
                   tablefmt='rounded_grid'))
    print('\n')
    print(tabulate(place_df,
                   stralign='center',
                   showindex=False,
                   tablefmt='rounded_grid'))
    print('\n')
    print(tabulate(about_df,
                   stralign='center',
                   showindex=False,
                   tablefmt='rounded_grid',
                   maxcolwidths=[None, 30]))
    print('\n')
    print(tabulate(adudance_element,
                   stralign='center',
                   showindex=False,
                   tablefmt='rounded_grid'))


@app.command()
def translation(user_formula: str,
                latex: bool = False,
                html: bool = False):
    """
    Выражает вещество или реакцию в latex/html/Unicode
    """
    Keys = user_formula.split()
    translated_dict = [('Кодировка', 'Формула'),]
    if len(Keys) == 1:
        user_substance = Substance.from_formula(user_formula)
        if latex:
            translated_dict.append(("Latex", user_substance.latex_name))
        if html:
            translated_dict.append(("HTML", user_substance.latex_name))
        translated_dict.append(("Unicode", user_substance.latex_name))
    else:
        Keys = list(filter(is_keys, Keys))
        subst = {k: Substance.from_formula(k) for k in Keys}
        user_substance = Reaction.from_string(user_formula, subst)
        if latex:
            translated_dict.append(("Latex", user_substance.latex(subst)))
        if html:
            translated_dict.append(("HTML", user_substance.html(subst)))
        translated_dict.append(("Unicode", user_substance.unicode(subst)))
    translated_df = pd.DataFrame(translated_dict)
    print(tabulate(translated_df,
                   stralign='center',
                   showindex=False,
                   tablefmt='rounded_grid'),)


@app.command()
def percent_mass(user_substance: Annotated[Optional[str],
                                           typer.Argument()] = None,
                 graf: bool = False):
    """
    Определяет процентное соотношение масс элементов в сложном веществе
    """
    if user_substance is None:
        user_substance = 'H2SO4'
    formula = Compound(user_substance)
    elm = list(filter(is_element, user_substance))
    elm_mass_percent = []
    for i in range(len(elm)):
        Mass_percent = formula.percentage_by_mass(elm[i])
        elm_mass_percent.append(Mass_percent)
    Mass_percent_dict = {'Элемент в сложном веществе':
                         'Процентное соотношение массы'}
    Mass_percent_dict.update({elm[x]: elm_mass_percent[x]
                              for (x) in range(len(elm))})
    if graf:
        Y = list(Mass_percent_dict.keys())
        X = list(Mass_percent_dict.values())
        Y.remove('Элемент в сложном веществе')
        X.remove('Процентное соотношение массы')
        plt.style.use('seaborn-v0_8-dark')
        plt.bar(Y, X, label='Процентное соотношение элементов')
        plt.xlabel('Элементы')
        plt.ylabel('Процент содержания')
        plt.title('Процентное содержание элементов в сложном веществе')
        plt.legend()
        plt.show()
    Mass_percent_df = pd.DataFrame(Mass_percent_dict, index=[0])
    print(tabulate(Mass_percent_df,
                   stralign='center',
                   showindex=False,
                   tablefmt='rounded_grid',
                   headers='keys'))


@app.command()
def phase(user_substance: str):
    """
    Определяет количество фаз в веществе
    """
    user_substance = Species.from_formula(user_substance)
    print(user_substance.phase_idx)


@app.command()
def balance():
    """
    Команда, которая балансирует реакцию
    """
    reac = typer.prompt('Реакция')
    prod = typer.prompt('Продукты реакции')
    unbalanced_reaction = reac + ' -> ' + prod
    reac = reac.split()
    reac = list(filter(is_element, reac))
    prod = prod.split()
    prod = list(filter(is_element, prod))
    balanced_reaction, balanced_production = balance_stoichiometry(reactants=reac,
                                                                   products=prod)
    reaction_list = [str(y) + x for (x, y) in balanced_reaction.items()]
    balanced_reaction = ' + '.join(reaction_list)
    production_list = [str(y) + x for (x, y) in balanced_production.items()]
    balanced_production = ' + '.join(production_list)
    balanced_reaction = balanced_reaction + ' -> ' + balanced_production
    output_dict = {'Несбаланисированная реакция':
                   'Сбалансированная реакция', }
    output_dict.update({unbalanced_reaction: balanced_reaction, })
    output_df = pd.DataFrame(output_dict, index=[0])
    print(tabulate(output_df,
                   stralign='center',
                   showindex=False,
                   tablefmt='rounded_grid',
                   headers='keys'))


if __name__ == '__main__':
    app()
