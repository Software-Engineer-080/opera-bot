from time import time
from telebot import types
from typing import Callable
from functools import wraps
from opera_storage import *
from aiogram.enums import ChatAction
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


# Функция создания инлайн клавиатуры
def inline_buttons(buttons_lst: list, buttons_per_row: int = 2) -> InlineKeyboardMarkup:

    """
    Создаёт инлайн клавиатуру кнопок под текстом

    Parameters
    ----------
    buttons_lst : list
        Список строковых значений под кнопки

    buttons_per_row : int
        Количество кнопок в строке

    Returns
    -------
    markup : InlineKeyboardMarkup
        Инлайновая клавиатура кнопок
    """

    markup = InlineKeyboardMarkup()

    for i in range(0, len(buttons_lst), buttons_per_row):

        button_row = []

        for j in range(buttons_per_row):

            if i + j < len(buttons_lst):

                button_row.append(InlineKeyboardButton(text=buttons_lst[i + j], callback_data=buttons_lst[i + j]))

        markup.row(*button_row)

    return markup


# Функция создания реплай клавиатуры
def buttons(buttons_lst: list, width: int = 3) -> ReplyKeyboardMarkup:

    """
    Создаёт текстовую клавиатуру кнопок

    Parameters
    ----------
    buttons_lst : list
        Список строковых значений под кнопки

    width : int
        Количество кнопок в строке

    Returns
    -------
    keyboard : ReplyKeyboardMarkup
        Текстовая клавиатура кнопок
    """

    lst = []

    for button in buttons_lst:

        lst.append(types.KeyboardButton(text=button))

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=width)
    keyboard.add(*lst)

    return keyboard


# Декоратор ограничения времени вызова функции
def throttle(seconds: int) -> Callable:

    def decorator(func):

        last_call = 0

        @wraps(func)
        def wrapper(*args, **kwargs):

            nonlocal last_call

            now = time()

            if now - last_call < seconds:

                return

            last_call = now

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Функция создания пагинации для всех фотографий
@throttle(2)
def sending_photo(call, num_menu: str, page: int = 1, previous_message: int = None) -> None:

    """
    Создает пагинацию и кнопки для всех видов меню

    Parameters
    ----------
    call
        Кэлбэк-запрос при нажатии пользователем кнопки

    num_menu : str
        Имя Базы Данных из кэлбэк-запроса

    page : int
        Страница, которую нужно показать пользователю

    previous_message : int | None
        ID сообщения, которое нужно будет удалить

    Raises
    ------
    BaseException
        Ловит исключение, если невозможно удалить сообщение

    Returns
    -------
    None
    """

    try:

        bot.send_chat_action(chat_id=call.chat.id, action=ChatAction.UPLOAD_PHOTO)

        num_menu = num_menu.split("_")[-1]

        buttons_photo = InlineKeyboardMarkup()

        if num_menu in menu_go:

            res_num = menu_go[num_menu]

        else:

            res_num = 0

        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM base_{num_menu}")
        record_count = cursor.fetchone()[0]
        cursor.close()

        if record_count > 1:

            btn_1 = InlineKeyboardButton("⬅️ Prev", callback_data=f"prev_{num_menu}_{page}")
            btn_2 = InlineKeyboardButton(f"{page}/{record_count}", callback_data=" ")
            btn_3 = InlineKeyboardButton("Next ➡️", callback_data=f"next_{num_menu}_{page}")
            buttons_photo.row(btn_1, btn_2, btn_3)

            if (num_menu == "new") or (num_menu == "event"):

                btn_4 = InlineKeyboardButton("Вернуться ⤴️", callback_data="Вернуться ⤴️")
                buttons_photo.row(btn_4)

            elif num_menu in menu_go:

                btn_4 = InlineKeyboardButton("✅ Бронь", callback_data=f"reserve_{res_num}")
                btn_5 = InlineKeyboardButton("К залам ⏏️", callback_data="К залам ⏏️")
                buttons_photo.row(btn_4, btn_5)

            else:

                btn_4 = InlineKeyboardButton("Ко всем меню ↘️", callback_data="Ко всем меню ↘️")
                buttons_photo.row(btn_4)

        else:

            if (num_menu == "new") or (num_menu == "event"):

                btn_1 = InlineKeyboardButton("Вернуться ⤴️", callback_data=f"Вернуться ⤴️")
                buttons_photo.row(btn_1)

            elif num_menu in menu_go:

                btn_1 = InlineKeyboardButton("✅ Бронь", callback_data=f"reserve_{res_num}")
                btn_2 = InlineKeyboardButton("К залам ⏏️", callback_data="К залам ⏏️")
                buttons_photo.row(btn_1, btn_2)

            elif num_menu == "reg":

                buttons_photo = types.ReplyKeyboardRemove()

            else:

                btn_1 = InlineKeyboardButton("Ко всем меню ↘️", callback_data="Ко всем меню ↘️")
                buttons_photo.row(btn_1)

        desc = ""
        new_photo = ""

        cursor = conn.cursor()
        cursor.execute(f"SELECT url, desc FROM base_{num_menu} WHERE id = ?", (page,))
        result = cursor.fetchone()
        cursor.close()

        if result:

            new_photo = result[0]
            desc = result[1]

            if num_menu == "event":

                myMonth = datetime.today().month

                desc = f"МЕРОПРИЯТИЯ {month_dict[myMonth]} 🌿"

        if new_photo:

            if num_menu == 'reg':

                bot.send_photo(call.chat.id, photo=new_photo, caption=desc, protect_content=True,
                               reply_markup=buttons_photo)

            else:

                bot.send_photo(call.chat.id, photo=new_photo, caption=desc, disable_notification=True,
                               protect_content=True, reply_markup=buttons_photo)

            if previous_message:

                bot.delete_message(call.chat.id, previous_message)

        else:

            if num_menu == 'reg':

                bot.send_message(chat_id=call.chat.id, text=thank_reg_desc, reply_markup=types.ReplyKeyboardRemove())

            else:

                bot.send_message(chat_id=call.chat.id, text=sorry_desc_base, disable_notification=True,
                                 reply_markup=inline_buttons(main_menu_button))

    except BaseException:

        pass


# Функция выставления минимальной оценки пользователем
@throttle(2)
def min_star(call, star: int) -> None:

    """
    Принимает, поставленную пользователем, низкую оценку

    Parameters
    ----------
    call
        Кэлбэк-запрос при нажатии пользователем кнопки

    star : int
        Оценка пользователя для загрузки в Базу Данных

    Returns
    -------
    None
    """

    update_user_star(call.chat.id, star)

    mess = bot.edit_message_text(chat_id=call.chat.id, message_id=call.message_id, text=min_rate_desc)

    bot.register_next_step_handler(mess, next_mess, star)


# Функция написания отзыва при негативной оценке
@throttle(2)
def next_mess(call, star: int) -> None:

    """
    Отправляет отзыв пользователя с низкой оценкой напрямую владельцу

    Parameters
    ----------
    call
        Кэлбэк-запрос при нажатии пользователем кнопки

    star : int
        Оценка пользователя для загрузки в Базу Данных

    Returns
    -------
    None
    """

    text = call.text

    bot.send_message(chat_id=owner,
                     text=f"Пользователь {call.from_user.first_name} с ID {call.chat.id} поставил "
                          f"оценку {star} по причине:\n\n{text}")

    bot.send_message(call.chat.id, thank_desc_rate, reply_markup=inline_buttons(main_menu_button))


# Функция выставления максимальной оценки пользователем
@throttle(2)
def max_star(call, star: int) -> None:

    """
    Принимает, поставленную пользователем, высокую оценку

    Parameters
    ----------
    call
        Кэлбэк-запрос при нажатии пользователем кнопки

    star : int
        Оценка пользователя для загрузки в Базу Данных

    Returns
    -------
    None
    """

    update_user_star(call.chat.id, star)

    star_reply = InlineKeyboardMarkup()
    btn_1 = InlineKeyboardButton(text='🌟Оставить отзыв🌟', url="https://yandex.ru/maps/org/52896029199")
    btn_2 = InlineKeyboardButton(text='Главное меню', callback_data='Главное меню')
    star_reply.row(btn_1)
    star_reply.row(btn_2)

    bot.edit_message_text(chat_id=call.chat.id, message_id=call.message_id, text=max_rate_desc, parse_mode="Markdown",
                          disable_web_page_preview=True, reply_markup=star_reply)


# Функция обновления оценки пользователя в Базе Данных
def update_user_star(user_id: int, new_star: int) -> bool:

    """
    Обновляет оценку пользователя в Базе Данных

    Parameters
    ----------
    user_id : int
        ID чата (может быть ID пользователя)

    new_star : int
        Оценка пользователя для загрузки в Базу Данных

    Returns
    -------
    bool
        Возвращает True, в любом случае
    """

    cursors = conn.cursor()
    cursors.execute("UPDATE users SET star = ? WHERE user_id = ?", (new_star, user_id))
    conn.commit()
    cursors.close()

    return True


# Функция получения информации о пользователе
@throttle(2)
def get_user_data(message: types.Message) -> None:

    """
    Получает информацию о пользователе по его ID

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Raises
    ------
    BaseException
        Ловит исключение, если невозможно изменить сообщение

    Returns
    -------
    None
    """

    try:

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", [message.chat.id])
        user = cursor.fetchone()
        cursor.close()

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f"💁Ваш профиль:\n\n"
                 f"Имя: {user[2]}\n\n"
                 f"Фамилия: {user[3]}\n\n"
                 f"Пол: {user[12]}\n\n"
                 f"📅: {user[4]}\n\n"
                 f"☎️: {user[9]}",
            reply_markup=inline_buttons(menu_user_res))

    except BaseException:

        pass


# Функция получения количества записей в БД
def get_total_pages(table_name: str) -> int:

    """
    Получает количество записей в Базе Данных, для указанной таблицы

    Parameters
    ----------
    table_name : str
        Имя таблицы, в которой нужно посчитать количество записей

    Returns
    -------
    total_records : int
        Количество записей в БД, для указанной таблицы
    """

    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    total_records = cursor.fetchone()[0]
    cursor.close()

    return total_records


# Функция показа пользователю действующих акций
@throttle(2)
def sale_photo(message: types.Message) -> None:

    """
    Отправляет пользователю действующие акции с фотографией

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Returns
    -------
    None
    """

    cursor = conn.cursor()
    cursor.execute(f"SELECT url FROM base_sale WHERE id = ?", (1,))
    result = cursor.fetchone()
    cursor.close()

    if result:

        bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)

        photo_url = result[0]

        bot.send_photo(message.chat.id, photo_url, disable_notification=True, caption=sale_desc, protect_content=True,
                       reply_markup=inline_buttons(sale_menu))

    else:

        bot.send_message(message.chat.id, "Ошибка при получении данных об акции!",
                         reply_markup=inline_buttons(main_menu_button))


# Функция выведения пользователю информации о резервировании
@throttle(2)
def info_reserve(message: types.Message, edit: types.Message) -> None:

    """
    Выводит информацию о бронировании пользователя

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    edit : types.Message
        Предыдущее сообщение бота, которое нужно будет заменить на новое

    Returns
    -------
    None
    """

    user_id = message.chat.id

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
    user = cursor.fetchone()
    cursor.close()

    my_date = user[7]

    if my_date:

        date_value_object = datetime.strptime(my_date, "%d.%m.%Y")

        if user[6] == "Основной зал":

            if date_value_object.date() >= datetime.now().date():

                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=edit.message_id,
                    text=f"🙌 Ваша бронь 🙌\n\n"
                         f"Зал: {user[6]}\n\n"
                         f"Столик: {user[10]}\n\n"
                         f"Дата: {user[7]}\n\n"
                         f"Время: {user[8]}\n\n",
                    reply_markup=inline_buttons(cancel_button_menu, buttons_per_row=1))

            else:

                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET reserve = NULL, date = NULL, time = NULL, new_table = NULL WHERE user_id = ?",
                    [user_id])
                conn.commit()
                cursor.close()

                bot.edit_message_text(chat_id=message.chat.id, message_id=edit.message_id, text=absence_res_desc,
                                      reply_markup=inline_buttons(res_button_menu))

        elif user[6] is None:

            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET reserve = NULL, date = NULL, time = NULL, new_table = NULL WHERE user_id = ?",
                [user_id])
            conn.commit()
            cursor.close()

            bot.edit_message_text(chat_id=message.chat.id, message_id=edit.message_id, text=absence_res_desc,
                                  reply_markup=inline_buttons(res_button_menu))

        else:

            if date_value_object.date() >= datetime.now().date():

                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=edit.message_id,
                    text=f"🙌 Ваша бронь 🙌\n\n"
                         f"Зал: {user[6]}\n\n"
                         f"Дата: {user[7]}\n\n"
                         f"Время: {user[8]}\n\n",
                    reply_markup=inline_buttons(cancel_button_menu, buttons_per_row=1))

            else:

                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET reserve = NULL, date = NULL, time = NULL, new_table = NULL WHERE user_id = ?",
                    [user_id])
                conn.commit()
                cursor.close()

                bot.edit_message_text(chat_id=message.chat.id, message_id=edit.message_id, text=absence_res_desc,
                                      reply_markup=inline_buttons(res_button_menu))

    else:

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET reserve = NULL, date = NULL, time = NULL, new_table = NULL WHERE user_id = ?", [user_id])
        conn.commit()
        cursor.close()

        bot.edit_message_text(chat_id=message.chat.id, message_id=edit.message_id, text=absence_res_desc,
                              reply_markup=inline_buttons(res_button_menu))


# Функция создания списка дат, в зависимости от последнего дня месяца
def new_month() -> list:

    """
    Создает список дат для бронирования с учетом последнего дня каждого месяца

    Returns
    -------
    date_list : list
        Список дат, доступных для бронирования
    """

    date_list = []

    for i in range(1, 10):

        if (datetime.now().date().day + i) <= m_day:

            day = datetime.now().date().day + i
            month = datetime.now().date().month

        else:

            day = (datetime.now().date().day + i) % m_day
            month = datetime.now().date().month + 1

        date_list.append(f"{day}" + "." + f"{month}".zfill(2) + "." + f"{datetime.now().date().year}")

    return list(date_list)
