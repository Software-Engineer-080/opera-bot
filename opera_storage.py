import sqlite3
# from telebot import TeleBot
from telebot.async_telebot import AsyncTeleBot
from datetime import datetime
from calendar import monthrange


# Конкретные значения ------------------------------------------------------------------------------

bot = AsyncTeleBot("YOUR_TOKEN")

conn = sqlite3.connect("opera.sqlite", check_same_thread=False)

owner = 0000  # Здесь написать ID владельца компании

m_day = monthrange(int(datetime.now().date().year), int(datetime.now().date().month))[-1]

opera_link_yandex = "[Яндекс карты](https://yandex.ru/maps/org/52896029199)"

opera_link_gis = "[2 Gis](https://2gis.ru/kemerovo/firm/70000001057524200)"

# Списки ------------------------------------------------------------------------------

owner_menu = ["+ админ", "- админ", "🔁 Меню️", "🔁 Новинки", "🔁 Акции", "🔁 Эвент", "Регистрация", "Бронь 🆑",
              "⚠️Рассылка ⚠️"]

user_menu = ["👤Профиль", "Резерв 🔏", "🍽 Меню️", "Новинки 🔥", "🎁 Акции", "Отзыв 💬", "⚡️ Эвент", "Песни 🎤"]

admin_menu = ["🔁 Меню️", "🔁 Новинки", "🔁 Акции", "🔁 Эвент", "Регистрация", "Бронь 🆑", "⚠️Рассылка ⚠️"]

table_menu = ['1🪑', '2🪑', '3🪑', '4🪑', '5🪑', '6🪑', '7🪑', '8🪑', '9🪑', '10🪑', '11🪑', '12🪑', 'Барная стойка',
              'Главное меню']

food_menu = ["🍻 Бар", "Коктейли 🍹", "🍝 Кухня", "Десерты 🍰", "🍱 Роллы", "Главное меню"]

time_menu = ["18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "00:00", "01:00"]

res_menu = ["Апартаменты", "Кабинет 🏢", "🏕️ Холл", "Основной 🏠", "Главное меню"]

admin_res_menu = ["Конкретная бронь", "Всё бронировние", "Главное меню"]

rate_menu = ["1⭐️", "4⭐️", "2⭐️", "5⭐️", "3⭐️", "Главное меню"]

news_menu = ["Мужчинам", "Женщинам", "Всем", "Главное меню"]

cancel_button_menu = ["Отменить бронь", "Главное меню"]

music_menu = ["Буду 🤩", "Главное меню"]

table_res_main_list = [str(i) for i in range(1, 13)]

sale_menu = ["15 %", "Подарок 🎉", "Вернуться ⤴️"]

verify_res_menu = ["🔖 Моя бронь", "К залам ⏏️"]

menu_user_res = ["🔖 Моя бронь", "Главное меню"]

res_button_menu = ["Резерв 🔏", "Главное меню"]

sex_list = ["🙋‍♂️ Мужской", "Женский 🙋‍♀️"]

main_menu_button = ["Главное меню"]

alphabet = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с",
            "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]

# Словари ------------------------------------------------------------------------------

menu_category = {
    "🍻 Бар": "base_bar",
    "Коктейли 🍹": "base_cocktails",
    "🍝 Кухня": "base_kitchen",
    "Десерты 🍰": "base_desert",
    '🍱 Роллы': 'base_roll',
}

place_category = {
    "Апартаменты": "base_apart",
    "Кабинет 🏢": "base_cab",
    "🏕️ Холл": "base_holl",
    "Основной 🏠": "base_main"
}

menu_go = {
    "apart": 1,
    "cab": 2,
    "holl": 3,
    "main": 4
}

place_go = {
    1: "Апартаменты",
    2: "Кабинет",
    3: "Холл",
    4: "Основной зал"
}

error_name = {
    0: "Имя слишком короткое!",
    1: "Имя не может содержать цифры!",
    2: "Имя слишком длинное!",
    4: "Имя должно содержать буквы русского алфавита!"
}

error_surname = {
    0: "Фамилия слишком короткая!",
    1: "Фамилия не может содержать цифры!",
    2: "Фамилия слишком длинная!",
    4: "Фамилия должна содержать буквы русского алфавита!"
}

errors_birthday = {
    1: "Вы ввели неверный формат даты!",
    2: "Дата должна содержать только цифры!",
    3: "Такой даты не существует!",
    5: "Вам нет 18 лет! Получите разрешение родителей!"
}

errors_date = {
    1: (
            "Вы ввели неверный формат даты!\n\n"
            "Вводите день, месяц и год разделенные точкой\n\n"
            "(К примеру: "
            + f"{datetime.now().date().day}".zfill(2)
            + "."
            + f"{datetime.now().date().month}".zfill(2)
            + "."
            + f"{datetime.now().date().year}"
            + ")👇"
    ),
    2: (
            "Вы ввели неверный формат даты!\n\n"
            "Дата должна содержать только цифры\n\n"
            "(К примеру: "
            + f"{datetime.now().date().day}".zfill(2)
            + "."
            + f"{datetime.now().date().month}".zfill(2)
            + "."
            + f"{datetime.now().date().year}"
            + ")👇"
    ),
    3: (
            "Такой даты не существует!\n\n"
            "Введите существующую дату\n\n"
            "(К примеру: "
            + f"{datetime.now().date().day}".zfill(2)
            + "."
            + f"{datetime.now().date().month}".zfill(2)
            + "."
            + f"{datetime.now().date().year}"
            + ")👇"
    ),
    5: (
            "Дата уже прошла!\n\n"
            "Введите дату, больше сегодняшней\n\n"
            "(В формате: "
            + f"{datetime.now().date().day}".zfill(2)
            + "."
            + f"{datetime.now().date().month}".zfill(2)
            + "."
            + f"{datetime.now().date().year}"
            + ")👇"
    ),
    6: (
            "Дата слишком далеко!\n\n"
            "Бронировать можно только на месяц вперёд!\n\n"
            "(До: "
            + f"{datetime.now().date().day}".zfill(2)
            + "."
            + f"{datetime.now().date().month + 1}".zfill(2)
            + "."
            + f"{datetime.now().date().year}"
            + ")👇"
    )
}

errors_time = {
    1: (
        "Вы ввели неверный формат времени!\n\n"
        "Введите часы и минуты через двоеточие!\n\n"
        "(К примеру: 18:00)👇"
    ),
    2: (
        "Вы ввели неверный формат времени!\n\n"
        "Часы и минуты должны быть цифрами!\n\n"
        "(К примеру: 18:00)👇"
    ),
    3: (
        "Такого времени не существует!\n\n"
        "Введите существующее время\n\n"
        "(К примеру: 18:00)👇"
    ),
    4: (
        "Мы в это время не работаем!\n\n"
        "Мы работаем с 18:00 до 03:00. Введите время в данном диапазоне\n\n"
        "(К примеру: 18:00)👇"
    )
}

errors_phone = {
    1: "Вы ввели неверный формат номера телефона!\n\n"
       "Введите номер, части которого разделены дефисом\n\n"
       "(Пример: +7-999-999-99-99)👇",
    2: "Вы ввели неверный формат номера телефона!\n\n"
       'Номер должен начинаться с "+7"\n\n'
       "(Пример: +7-999-999-99-99)👇",
    3: "Вы ввели неверный формат номера телефона!\n\n"
       "Номер должен состоять из цифр\n\n"
       "(Пример: +7-999-999-99-99)👇",
    5: "Вы ввели неверный формат номера телефона!\n\n"
       "Попробуйте ввести номер как в примере\n\n"
       "(Пример: +7-999-999-99-99)👇"
}

month_dict = {
    1: 'ЯНВАРЯ',
    2: 'ФЕВРАЛЯ',
    3: 'МАРТА',
    4: 'АПРЕЛЯ',
    5: 'МАЯ',
    6: 'ИЮНЯ',
    7: 'ИЮЛЯ',
    8: 'АВГУСТА',
    9: 'СЕНТЯБРЯ',
    10: 'ОКТЯБРЯ',
    11: 'НОЯБРЯ',
    12: 'ДЕКАБРЯ'
}

# Строки ------------------------------------------------------------------------------

# -------------------- Владелец --------------------

repeat_desc_phone = (
    "Номер телефона должен состоять из цифр!\n\n"
    "Попробуйте ещё раз 👇"
)

owner_go_desc = "Теперь Вы можете перейти в главное меню!"

# -------------------- Общее --------------------

thank_reg_desc = (
    '✅ Регистрация успешно завершена.\n\n'
    'Покажите официанту это сообщение и забирайте подарок 🎁\n\n'
    'Добро пожаловать в диско караоке бар «OPERA»!\n\n'
    'Приятного отдыха!'
)

owner_menu_desc = "Вы в меню владельца!"

admin_menu_desc = "Вы в меню админа!"

user_menu_desc = "Вы в главном меню!"

menu_news_desc = "Вы в меню рассылки!\n\nВыберите кому отправить сообщение:"

# -------------------- Профиль --------------------

absence_res_desc = (
    "🙌 Ваша бронь 🙌\n\n"
    "У Вас отсутствует бронирование!\n\n"
    "Хотите зарезервировать столик?"
)

cancel_res_desc = (
    "Для отмены бронирования Вам необходимо позвонить по телефону:\n\n"
    "+7-(900)-100-72-04\n\n"
    f"И сообщить менеджеру о Своём желании отменить бронировние!"
)

# -------------------- Бронирование --------------------

good_message_table = (
    "Отлично! Зал выбран!\n\n"
    "Теперь выберите столик, который хотите забронировать!👇\n\n"
)

good_message_place = (
        f"Отлично! Зал выбран!\n\n"
        f"Теперь введите дату, на которую хотите его забронировать\n\n"
        f"(К примеру: "
        + f"{datetime.now().date().day}".zfill(2)
        + "."
        + f"{datetime.now().date().month}".zfill(2)
        + "."
        + f"{datetime.now().date().year}"
        + ")👇"
)

sorry_res_know = (
    'Извините, но в данный момент Мы не можем подтвердить ваше бронирование!\n\n'
    'Свяжитесь для бронирования по телефону:\n\n'
    '+7-(900)-100-72-04\n\n'
    'Ещё раз извиняемся за доставленные неудобства! Хорошего дня!'
)

sorry_res_not = (
    "Администратор отклонил Ваше бронирование!\n\n"
    f"Попробуйте забронировать снова или свяжитесь для бронирования по телефону:\n\n"
    f"+7-(900)-100-72-04\n\n"
    f"❗️При бронировании через менеджера, оно НЕ БУДЕТ отбражаться в вашем профиле❗️\n\n"
    "Приятного отдыха!"
)

admin_desc_know = "Решение по бронированию принято другим администратором!"

# -------------------- Меню --------------------

menu_desc = "Здесь Вы можете найти различное меню!"

# -------------------- Акции --------------------

sale_desc = (
    "🔥Каждому имениннику дарим 15% скидку!\n\n"
    "✨Всем, кто зарегистрировался в боте, дарим подарок!"
)

percent_desc = "Для получения скидки\nобратитесь к официанту\nс паспартом!"

desc_present = (
    "Для получения подарка покажите официанту сообщение, отправленное вам после регистрации в боте!"
)

# -------------------- Отзывы --------------------

review_desc = "Вам понравилось у нас?\n\nПоставьте оценку:"

max_rate_desc = (
    "Спасибо за высокую оценку!\n\nПожалуйста, оставьте отзыв о вашем опыте, "
    f"это поможет нам быть еще лучше!\n\n{opera_link_yandex}      {opera_link_gis}"
)

min_rate_desc = (
    "Жаль, что у Вас сложился такой опыт. Мы хотим всё исправить!\n\n"
    "Пожалуйста, поделитесь, почему Вы поставили такую оценку?\n\n"
    "Ответы читает собственник заведения!"
)

thank_desc_rate = (
    "Спасибо за Ваш отзыв, мы обязательно его передадим собственнику.\n\n"
    "Хорошего дня!"
)

# -------------------- Музыка --------------------

music_menu_desc = 'Будете отжигать?'

music_table_desc = 'За каким столиком сидите?'

# -------------------- Другое --------------------

sorry_desc_base = "Извините, но данный раздел пока не доступен для просмотра!"
