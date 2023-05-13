import pytz
import multiprocessing
import uuid
import os
from datetime import datetime
from difflib import SequenceMatcher


FIELDS = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature class',
          'feature code', 'country code', 'cc2', 'admin1 code', 'admin2 code', 'admin3 code',
          'admin4 code', 'population', 'elevation', 'dem', 'timezone', 'modification date']

alphabet = {'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о',
            'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'}

translit_table = {'а': ('a',), 'б': ('b',), 'в': ('v', 'u'), 'г': ('g',), 'д': ('d',),
                  'е': ('e', 'ye'), 'ё': ('yo', 'ë'), 'ж': ('zh',), 'з': ('z',), 'и': ('i',),
                  'й': ('y', 'i'), 'к': ('k',), 'л': ('l',), 'м': ('m',), 'н': ('n',), 'о': ('o',),
                  'п': ('p',), 'р': ('r',), 'с': ('s',), 'т': ('t',), 'у': ('u', 'ou'), 'ф': ('f', 'ph'),
                  'х': ('kh',), 'ц': ('ts',), 'ч': ('ch',), 'ш': ('sh',), 'щ': ('sch', 'shch'),
                  'ъ': ('"', '”'), 'ы': ('y',), 'ь': ('\'', '’', ''), 'э': ('e',), 'ю': ('yu', 'ju'), 'я': ('ya', 'ja'),
                  '-': ('-', ''), '«': ('«', ''), '»': ('»', ''), '№': ('№',), '#': ('#',), ',': (',',), '"': ('"',),
                  '\'': ('\'',), '(': ('(',), ')': (')',),
                  'a': ('a',), 'b': ('b',), 'c': ('c',), 'd': ('d',), 'e': ('e',), 'f': ('f',), 'g': ('g',),
                  'h': ('h',), 'i': ('i',), 'j': ('j',), 'k': ('k',), 'l': ('l',), 'm': ('m',), 'n': ('n',),
                  'o': ('o',), 'p': ('p',), 'q': ('q',), 'r': ('r',), 's': ('s',), 't': ('t',), 'u': ('u',),
                  'v': ('v',), 'w': ('w',), 'x': ('x',), 'y': ('y',), 'z': ('z',), '—': ('—', '')}


def _translit(word_ru: str) -> list: 
    """
    Транслитерация, возвращает список возможных вариантов транслитерации.

    :param word_ru: слово на русском
    :return: набор комбинаций возможных транслитераций
    """
    list_symbols = []
    for symbol in word_ru:
        if symbol not in translit_table:
            symbol_ = (symbol.lower(),)
            list_symbols.append(symbol_)
        else:
            if len(word_ru) < 30:
                list_symbols.append(translit_table[symbol.lower()])
            else:
                symbol_ = (translit_table[symbol.lower()][0],)
                list_symbols.append(symbol_)
    set_words = find_all_combinations(list_symbols)
    return set_words


def find_by_geonameid(geonameid: str) -> dict:
    """
    Поиск по geonameid.

    :param geonameid: идентификатор города
    :return: словарь с данными
    """
    with open('RU.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if geonameid in line:
                split_line = line.split('\t')
                if split_line[0] == geonameid:
                    result = dict()
                    for number, field in enumerate(split_line):
                        result[FIELDS[number]] = field.replace('\n', '')
                    return result


def find_by_page(page: int, count: int) -> dict:
    """
    Поиск по заданному количеству городов на странице и номеру страницы.

    :param page: номер страницы
    :param count: количество городов на странице
    :return: словарь с городами
    """
    cities = []
    with open('RU.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()

        start = (page - 1) * count
        finish = start + count

        if finish > len(lines):
            return {'error': 'list of pages out of range', 'pages_amount': len(lines) // count}

        for line in lines[start:start + count]:
            split_line = line.split('\t')
            city = dict()
            for number, field in enumerate(split_line):
                city[FIELDS[number]] = field.replace('\n', '')
            cities.append(city)
    return {'cities': cities}


def multiprocess_init(length_cities: int, city_ru: str) -> list:
    """
    Мультипроцессный поиск совпадений слов (вызывается,
    если не найдена транслитерация и альтернативные русские имена).
    uid используется для идентификации и названия файла, который будет после завершения поиска удалён.

    :param length_cities: сколько всего записей о городах
    :param city_ru: входное название города на русском
    :return: список найденных городов по процентному соответствию
    """
    uid = uuid.uuid4()

    cpu_count = multiprocessing.cpu_count()
    processes = []
    portion_size = length_cities // cpu_count

    for process in range(cpu_count):
        if process == cpu_count:
            processes.append((process * portion_size, length_cities, uid, city_ru))
            break
        processes.append((process * portion_size, (process + 1) * portion_size, uid, city_ru))

    p = multiprocessing.Pool(processes=cpu_count)
    p.map(multiprocess_finding, processes)

    cities = []

    if os.path.exists(f'temp_files/{uid}.txt'):
        with open(f'temp_files/{uid}.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                split_line = line.split('\t')
                city = dict()
                for number, field in enumerate(split_line):
                    city[FIELDS[number]] = field.replace('\n', '')
                cities.append(city)
        os.remove(f'temp_files/{uid}.txt')
    return cities


def multiprocess_finding(data: tuple):
    """
    Реализация многопроцессности,
    данные сохраняются в txt файле, как общее место для всех процессовю.

    :param data: входные данные: промежуток поиска, uid, входное русское название города
    """
    start = data[0]
    finish = data[1]
    uid = data[2]
    city_ru = data[3]

    with open('RU.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines[start: finish]:
            split_line = line.split('\t')
            city_set_words = _translit(city_ru)
            for word in city_set_words:
                if check_coincidence(word, split_line[1].lower()):
                    result = ''
                    for number, field in enumerate(split_line):
                        if number == len(FIELDS) - 1:
                            result += field
                            break
                        result += field + '\t'
                    with open(f'temp_files/{uid}.txt', 'a', encoding='utf-8') as f:
                        f.write(result)


def find_by_cities(city1: str, city2: str) -> dict:
    """
    Поиск двух городов и обработка остальной информации(timezone).

    :param city1: первый город на кириллице
    :param city2: второй город на кириллице
    :return: словарь с информацией по городам
    """
    city_set_words_1 = _translit(city1.lower())
    city_set_words_2 = _translit(city2.lower())
    with open('RU.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        cities1 = []
        cities2 = []
        for line in lines:
            check_city1 = check_city(city1, city_set_words_1, line)
            check_city2 = check_city(city2, city_set_words_2, line)
            if check_city1 is not None:
                cities1.append(check_city1)
            if check_city2 is not None:
                cities2.append(check_city2)

    if not cities1:
        cities1 = multiprocess_init(len(lines), city1.lower())
    if not cities2:
        cities2 = multiprocess_init(len(lines), city2.lower())

    result_city_1 = {'error': f'City \'{city1}\' not found'} if not cities1 else compare_population(cities1, city1)
    result_city_2 = {'error': f'City \'{city2}\' not found'} if not cities2 else compare_population(cities2, city2)

    if not result_city_1.get('error') and not result_city_2.get('error'):
        north_city = result_city_1 if result_city_1['latitude'] > result_city_2['latitude'] else result_city_2
        timezone = (result_city_1['timezone'], True) if result_city_1['timezone'] == result_city_2['timezone'] else ('different', False)
        timezone_diff = tz_diff(result_city_1['timezone'], result_city_2['timezone'])
    else:
        north_city = 'missing'
        timezone = ('missing', 'missing')
        timezone_diff = 'missing'

    time_zone_data = {
        'timezone': timezone[0],
        'same_timezone_flag': timezone[1],
        'timezone_diff_hours': timezone_diff
    }

    details = {'north_city': north_city, 'timezone_info': time_zone_data}
    return {'city_1': result_city_1, 'city_2': result_city_2, 'details': details}


def find_by_part_name(part_name_ru: str) -> list:
    """
    Поиск по части слова.

    :param part_name_ru: часть слова на кириллице
    :return: список возможных вариантов
    """
    with open('RU.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        result = []
        part_name_translit = _translit(part_name_ru)
        for line in lines:

            for part_word in part_name_translit:
                if part_word in line.lower():
                    split_line = line.split('\t')
                    if part_word in split_line[1].lower():
                        result.append(split_line[1])
                elif part_name_ru.lower() in line.lower():
                    split_line = line.split('\t')
                    if part_name_ru.lower() in split_line[3].lower():
                        result.append(split_line[1])
    return result


def check_city(city_ru, city_set_words, line) -> [dict, None]:
    """
    Двухэтапный поиск
    1. Транслитерация
    2. Альтернативные русские имена

    :param city_ru: входное слово на кириллице
    :param city_set_words: набор возможных транслитераций
    :param line: строка с информацией о городе
    :return: словарь с данными, если город найден, иначе None
    """

    line_lower = line.lower()

    # Первая проверка по транслитерации
    for word in city_set_words:
        if word in line_lower:
            split_line = line.split('\t')
            if split_line[1].lower() in city_set_words:
                result = {}
                for number, field in enumerate(split_line):
                    result[FIELDS[number]] = field.replace('\n', '')
                return result

    # Вторая проверка по альтернативным русским именам
    if city_ru.lower() in line_lower:
        split_line = line.split('\t')
        for altername in split_line[3].lower().split(','):
            if is_russian_name(altername) and altername.lower() == city_ru.lower():
                result = {}
                for number, field in enumerate(split_line):
                    result[FIELDS[number]] = field.replace('\n', '')
                return result

    return None


def is_russian_name(name: str) -> bool:
    """
    Проверка на русское слово.

    :param name: слово с кириллицей
    :return: true, если русское, иначе false
    """
    return bool(alphabet.intersection(set(name.lower())))


def compare_population(cities: list, city_ru: str) -> dict:
    """
    Приоритетный поиск по словам, имеющим транслитерацию, второй приоритет у слов, не имеющих транслитерации
    Происходит поиск города с наибольшей популяцией, по умолчанию первое попавшееся

    :param cities: список найденных городов
    :param city_ru: входное значение города на кириллице
    :return: информацию о городе с наибольшей популяцией или первым попавшимся
    """
    list_for_find_firstly = []
    for city in cities:
        translit_words = _translit(city_ru)

        if city['name'].lower() in translit_words:
            list_for_find_firstly.append(city)

    if list_for_find_firstly:
        sorted_population = sorted(list_for_find_firstly, key=lambda c: c['population'])
        if sorted_population[-1] == '0':
            return list_for_find_firstly[0]
        return sorted_population[-1]

    if not list_for_find_firstly:
        sorted_population = sorted(cities, key=lambda c: c['population'])
        if sorted_population[-1] == '0':
            return cities[0]
        return sorted_population[-1]


def tz_diff(city_tz1: str, city_tz2: str) -> int:
    """
    Определение разницы временных зон в часах.

    :param city_tz1: временная зона 1 города
    :param city_tz2: временная зона 2 города
    :return: время в часах для первого города, относительно второго
    """
    tz1 = pytz.timezone(city_tz1)
    tz2 = pytz.timezone(city_tz2)
    date = datetime.now()
    diff = (tz1.localize(date) - tz2.localize(date).astimezone(tz1)).seconds / 3600
    diff = diff - 24 if diff > 12 else diff
    return diff


def find_all_combinations(data: list):
    """
    Алгоритм поиска всех вариантов транслитерации
    :param data: список с кортежем, в котором находятся символы
    :return:
    """
    unique_set = []
    len_variants = 1
    for i in [len(i) for i in data]:
        len_variants *= i

    for number, symbols in enumerate(data):
        if number == 0:
            same_symbols = int(len_variants / len(symbols))
            previous = same_symbols
        else:
            same_symbols = int(previous / len(symbols))
            previous = same_symbols

        unique = []
        for symbol in symbols:
            for j in range(same_symbols):
                unique.append(symbol)
        unique_set.append(unique)
    full_set = []
    for symbols in unique_set:
        full_set.append(symbols * int(len_variants / len(symbols)))

    result = []
    for i in range(len(full_set[0])):
        word = ''
        for j in range(len(full_set)):
            word += full_set[j][i]
        result.append(word)

    return result


def check_coincidence(to_check: str, correct: str) -> bool:
    """
    Проверка на процентное совпадение слов.

    :param to_check: слово, которое надо сравнить
    :param correct: слово, с которым сравнивают
    :return: если процентное совпадание >85%, возвращается true
    """
    similarity = SequenceMatcher(None, to_check, correct).ratio()
    if similarity > 0.85:
        return True
    return False
