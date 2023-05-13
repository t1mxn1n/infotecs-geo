## P.S. не прошёл
<hr>
<hr>
<hr>
<hr>
# Тестовое задание Infotecs для стажера на позицию "Программист на языке Python"

Реализовать HTTP-сервер для предоставления информации по географическим объектам.
Данные взять из географической базы данных GeoNames, по [ссылке](http://download.geonames.org/export/dump/RU.zip).

## Метод принимает идентификатор geonameid и возвращает информацию о городе

**Пример запроса** `http://127.0.0.1:8000/city?geonameid=7586303`

```json
{
  "geonameid": "7586303",
  "name": "Ozero Bol’shoye",
  "asciiname": "Ozero Bol'shoye",
  "alternatenames": "Ozero Bol'shoe,Ozero Bol'shoye,Ozero Bol’shoye,Озеро Большое",
  "latitude": "57.7414",
  "longitude": "37.6936",
  "feature class": "H",
  "feature code": "LK",
  "country code": "RU",
  "cc2": "",
  "admin1 code": "88",
  "admin2 code": "",
  "admin3 code": "",
  "admin4 code": "",
  "population": "0",
  "elevation": "",
  "dem": "143",
  "timezone": "Europe/Moscow",
  "modification date": "2012-01-21"
}
```

## Метод принимает страницу и количество отображаемых на странице городов и возвращает список городов с их информацией

**Пример запроса** `http://127.0.0.1:8000/cities_list?page=100&count=2`


```json
{
  "cities": [
    {
      "geonameid": "451945",
      "name": "Mishevo",
      "asciiname": "Mishevo",
      "alternatenames": "Mishevo,Мишево",
      "latitude": "56.97825",
      "longitude": "34.26705",
      "feature class": "P",
      "feature code": "PPL",
      "country code": "RU",
      "cc2": "",
      "admin1 code": "77",
      "admin2 code": "",
      "admin3 code": "",
      "admin4 code": "",
      "population": "0",
      "elevation": "",
      "dem": "231",
      "timezone": "Europe/Moscow",
      "modification date": "2012-01-16"
    },
    {
      "geonameid": "451946",
      "name": "Minino",
      "asciiname": "Minino",
      "alternatenames": "Minino,Минино",
      "latitude": "56.70315",
      "longitude": "34.48691",
      "feature class": "P",
      "feature code": "PPL",
      "country code": "RU",
      "cc2": "",
      "admin1 code": "77",
      "admin2 code": "",
      "admin3 code": "",
      "admin4 code": "",
      "population": "0",
      "elevation": "",
      "dem": "257",
      "timezone": "Europe/Moscow",
      "modification date": "2012-01-16"
    }
  ]
}
```

## Метод принимает названия двух городов (на русском языке) и получает информацию о найденных городах, а также дополнительно: какой из них расположен севернее и одинаковая ли у них временная зона (когда несколько городов имеют одно и то же название, разрешать неоднозначность выбирая город с большим населением; если население совпадает, брать первый попавшийся)
## Доп. задание: Для 3-его метода показывать пользователю не только факт различия временных зон, но и на сколько часов они различаются.
###

**Пример запроса** `http://127.0.0.1:8000/cities?city1=Чёрный&city2=Назарово`

```json
{
  "city_1": {
    "geonameid": "12505453",
    "name": "Chërnyy",
    "asciiname": "Chernyy",
    "alternatenames": "Chernyy,Chjornyj,Chërnyy,Чёрный",
    "latitude": "49.99736",
    "longitude": "137.58109",
    "feature class": "H",
    "feature code": "STM",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "30",
    "admin2 code": "",
    "admin3 code": "",
    "admin4 code": "",
    "population": "0",
    "elevation": "",
    "dem": "84",
    "timezone": "Asia/Vladivostok",
    "modification date": "2023-01-13"
  },
  "city_2": {
    "geonameid": "1497951",
    "name": "Nazarovo",
    "asciiname": "Nazarovo",
    "alternatenames": "Nasarowo,Nazarava,Nazarovo,Nazarowo,Nazàrovo,na zha luo wo,nazarwfw,nazarwfw  krasnwyarsk,Назарава,Назарово,نازاروفو,نازاروفو، کراسنویارسک,納扎羅沃",
    "latitude": "56.0104",
    "longitude": "90.4011",
    "feature class": "P",
    "feature code": "PPL",
    "country code": "RU",
    "cc2": "",
    "admin1 code": "91",
    "admin2 code": "",
    "admin3 code": "",
    "admin4 code": "",
    "population": "55252",
    "elevation": "",
    "dem": "253",
    "timezone": "Asia/Krasnoyarsk",
    "modification date": "2019-09-05"
  },
  "details": {
    "north_city": {
      "geonameid": "1497951",
      "name": "Nazarovo",
      "asciiname": "Nazarovo",
      "alternatenames": "Nasarowo,Nazarava,Nazarovo,Nazarowo,Nazàrovo,na zha luo wo,nazarwfw,nazarwfw  krasnwyarsk,Назарава,Назарово,نازاروفو,نازاروفو، کراسنویارسک,納扎羅沃",
      "latitude": "56.0104",
      "longitude": "90.4011",
      "feature class": "P",
      "feature code": "PPL",
      "country code": "RU",
      "cc2": "",
      "admin1 code": "91",
      "admin2 code": "",
      "admin3 code": "",
      "admin4 code": "",
      "population": "55252",
      "elevation": "",
      "dem": "253",
      "timezone": "Asia/Krasnoyarsk",
      "modification date": "2019-09-05"
    },
    "timezone_info": {
      "timezone": "different",
      "same_timezone_flag": false,
      "timezone_diff_hours": -3
    }
  }
}
```

#### В теле ответа в поле details возвращается:

```
1.  north_city – информация о городе, расположенном севернее 

2.  timezone_info – информация о временных зонах двух городов. timezone показывает 
    временную зону, если она у двух городов одинаковая, иначе different. same_timezone_flag 
    показывает true или false в зависимости от равенства временных зон. timezone_diff_hours 
    показывает разницу в часах для первого города, относительно второго. Т.е. как в примере 
    ответа -3 означает, что в первом городе необходимо сделать -3 часа, чтобы время совпало 
    со вторым.
```

#### Краткое описание логики поиска городов

```
Поиск слов осуществлён тремя шагами: 
1.Поиск по транслитерации слова. Если найдена транслитерация, то город добавляется в 
  список для дальнейшей сортировки 
2.Поиск по альтернативным русским именам. Если не найдена 
  транслитерация, проверяется наличие запрашиваемого города в альтернативных именах. Если 
  слово имеется, оно также добавляется в список для дальнейшей сортировки 
3.Третий шаг включается в работу только в том случае, если не найдено ни одного города 
  по первым двум шагам. Производится поиск по процентному совпадению запрашиваемого города 
  с именами городов. Если слово совпадает на более чем 85%, оно добавится в список для 
  дальнейшей сортировки. 

    Отбор необходимого города производится по приоритетам. Высший приоритет имеют города, у 
которых есть совпадающая транслитерация. По ним происходит сортировка популяции. 
Второй приоритет имеют города, у которых нет транслитерации, но которые были найдены 2-м 
или 3-м способом. Среди них тоже происходит сортировка по популяции.
```

## Дополнительное задание: Реализовать метод, в котором пользователь вводит часть названия города и возвращает ему подсказку с возможными вариантами продолжений.

**Пример запроса** `http://127.0.0.1:8000/city/names?part_of_name=тропи`

```json
[
  "Tropino",
  "Stropitsy",
  "Tropinino",
  "Tropinsk",
  "Tropino",
  "Tropino",
  "Tropino",
  "Tropinka",
  "Antropikha",
  "Tropinskoye",
  "Tropino",
  "Antropikha",
  "Antropikha",
  "Antropikha",
  "Letnik Tropinskiy",
  "Ozero Tropino",
  "Tropinskaya",
  "Tropin",
  "Antropikha",
  "Foresta Tropicana"
]
```

## Все возможные эндпоинты

`http://127.0.0.1:8000/city?geonameid=<id>`
####
`http://127.0.0.1:8000/city/names?part_of_name=<part_of_name>`
####
`http://127.0.0.1:8000/cities_list?page=<num_page>&count=<count_per_page>`
####
`http://127.0.0.1:8000/cities?city1=<city_ru_first>&city2=<city_ru_second>`


## Запуск программы

```
1. Версия Python 3.11
2. (Желательно) Настройка виртуального окружения:
   "python -m venv venv" 
   ".\venv\Scripts\activate"
3. Установка библиотек "pip install -r requirements.txt"
4. Запуск "python script.py" (windows), "python3 script.py" (linux)
```





