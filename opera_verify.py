from time import sleep
from opera_func import *


# Функция регистрации имени пользователя
def reg_name(message: types.Message) -> None:

    """
    Регистрирует имя пользователя при первом запуске бота

    Parameters
    ----------
    message : types.Message
        Значение сообщения для дальнейшей работы

    Returns
    -------
    None
    """

    user_id = message.from_user.id
    user_name = message.text.lower()

    num = verify_name(user_name)

    if num == 3:

        cursors = conn.cursor()
        cursors.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, user_name.capitalize()))
        cursors.close()

        send_surname = bot.send_message(chat_id=message.chat.id,
                                        text=f"Приятно познакомиться, "
                                             f"{user_name.capitalize()}!\n\nВведите Свою фамилию 👇",
                                        disable_notification=True)

        bot.register_next_step_handler(send_surname, reg_surname)

    else:

        error_message = error_name.get(num, "Вы неверно ввели имя!")

        if error_message:

            reg = bot.send_message(chat_id=message.chat.id, text=f"{error_message}\n\nВведите настоящее имя 👇",
                                   disable_notification=True)

            bot.register_next_step_handler(reg, reg_name)


# Функция регистрации фамилии пользователя
def reg_surname(message: types.Message) -> None:

    """
    Регистрирует фамилию пользователя при первом запуске бота

    Parameters
    ----------
    message : types.Message
        Значение сообщения для дальнейшей работы

    Returns
    -------
    None
    """

    user_id = message.from_user.id
    user_surname = message.text.strip().lower()

    num = verify_surname(user_surname)

    if num in error_surname:

        reg = bot.send_message(chat_id=message.chat.id, text=error_surname[num] + "\n\nВведите настоящую фамилию 👇",
                               disable_notification=True)

        bot.register_next_step_handler(reg, reg_surname)

        return

    cursors = conn.cursor()
    cursors.execute("UPDATE users SET surname = ? WHERE user_id = ?", (user_surname.capitalize(), user_id))
    conn.commit()
    cursors.close()

    send_birthday = bot.send_message(chat_id=message.chat.id,
                                     text="Осталось совсем чуть-чуть!\n\nВведите дату рождения 👇",
                                     disable_notification=True)

    bot.register_next_step_handler(send_birthday, reg_birthday)


# Функция регистрации даты рождения пользователя
def reg_birthday(message: types.Message) -> None:

    """
    Регистрирует дату рождения пользователя при первом запуске бота

    Parameters
    ----------
    message : types.Message
        Значение сообщения для дальнейшей работы

    Raises
    ------
    ValueError
        Ловит исключение, если в дату рождения будут написаны недопустимые символы

    Returns
    -------
    None
    """

    user_id = message.from_user.id
    user_birthday = message.text

    try:

        num = verify_birthday(user_birthday)

        if num in errors_birthday:

            desc = errors_birthday[num]

        else:

            user_birthday = user_birthday.split(".")
            user_birthday = f"{user_birthday[0].zfill(2)}.{user_birthday[1].zfill(2)}.{user_birthday[2]}"

            cursors = conn.cursor()
            cursors.execute("UPDATE users SET birthday = ? WHERE user_id = ?", (user_birthday, user_id))
            conn.commit()
            cursors.close()

            send_sex = bot.send_message(
                chat_id=message.chat.id,
                text="Небольшая формальность 🫣\n\nУкажите свой пол 👇",
                disable_notification=True, reply_markup=buttons(sex_list)
            )

            bot.register_next_step_handler(send_sex, registration_sex)

            return

        reg = bot.send_message(
            chat_id=message.chat.id,
            text=f"{desc}\n\nВведите день, месяц и год разделенные точкой\n\n"
                 f"(К примеру: {datetime.now().date().day:02}."
                 f"{datetime.now().date().month:02}.{datetime.now().date().year})👇", disable_notification=True)

        bot.register_next_step_handler(reg, reg_birthday)

    except ValueError:

        reg_birthday(message)


# Функция регистрации гендера пользователя
def registration_sex(message: types.Message) -> None:

    """
    Регистрирует гендер пользователя при первом запуске бота

    Parameters
    ----------
    message : types.Message
        Значение сообщения для дальнейшей работы

    Raises
    ------
    BaseException
        Ловит все исключения, если будет указан гендер не из представленных

    Returns
    -------
    None
    """

    try:

        if (message.text == '🙋‍♂️ Мужской') or (message.text == 'Женский 🙋‍♀️'):

            user_id = message.from_user.id
            user_sex = message.text.split()[1] if message.text == '🙋‍♂️ Мужской' else message.text.split()[0]

            cursors = conn.cursor()
            cursors.execute("UPDATE users SET sex = ? WHERE user_id = ?", (user_sex, user_id))
            conn.commit()
            cursors.close()

            key_phone = ReplyKeyboardMarkup(resize_keyboard=True)
            btn_1 = types.KeyboardButton(f"Мой номер", request_contact=True)
            key_phone.add(btn_1)

            send_number = bot.send_message(
                chat_id=message.chat.id,
                text="Финальный аккорд! Укажите свой номер телефона\n\n(Пример: +7-999-999-99-99)👇",
                disable_notification=True, reply_markup=key_phone
            )

            bot.register_next_step_handler(send_number, registration_phone)

        else:

            send_sex = bot.send_message(
                chat_id=message.chat.id,
                text="Такого гендера не существует!\n\nУкажите свой пол 👇",
                disable_notification=True
            )

            bot.register_next_step_handler(send_sex, registration_sex)

    except BaseException:

        registration_sex(message)


# Функция регистрации номера телефона
def registration_phone(message: types.Message) -> None:

    """
    Регистрирует номер телефона пользователя при первом запуске бота

    Parameters
    ----------
    message : types.Message
        Значение сообщения для дальнейшей работы

    Returns
    -------
    None
    """

    user_id = message.from_user.id

    if message.contact:

        user_reg_phone = message.contact.phone_number

        if user_reg_phone[0] == '+':

            user_reg_phone = (user_reg_phone[:2] + '-' + user_reg_phone[2:5] + '-' + user_reg_phone[5:8] + '-' +
                              user_reg_phone[8:10] + '-' + user_reg_phone[10:])

        else:

            user_reg_phone = ('+' + user_reg_phone[:1] + '-' + user_reg_phone[1:4] + '-' + user_reg_phone[4:7] + '-' +
                              user_reg_phone[7:9] + '-' + user_reg_phone[9:])

    else:

        user_reg_phone = message.text

    num = verify_phone(user_reg_phone)

    if num == 4:

        cursor = conn.cursor()
        cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (user_reg_phone, user_id))
        conn.commit()
        cursor.close()

        # hell = bot.send_message(message.chat.id, thank_reg_desc, reply_markup=types.ReplyKeyboardRemove())

        sending_photo(message, 'base_reg')

        sleep(5)

        # bot.delete_message(chat_id=message.chat.id, message_id=hell.id)

        bot.send_message(chat_id=message.chat.id, text=user_menu_desc, disable_notification=True,
                         reply_markup=inline_buttons(user_menu))

    else:

        reg = bot.send_message(chat_id=message.chat.id, text=errors_phone[num])

        bot.register_next_step_handler(reg, registration_phone)


# Функция проверки имени пользователя на валидность
def verify_name(user_name: str) -> int:

    """
    Проверяет имя пользователя на валидность

    Parameters
    ----------
    user_name : str
            Строка, которая должна содержать имя пользователя

    Returns
    -------
    int
        Номер ошибки в словаре ошибок имени
    """

    if len(user_name) < 2:

        return 0

    elif not user_name.isalpha():

        return 1

    elif len(user_name) > 12:

        return 2

    elif not all(char in alphabet for char in user_name):

        return 4

    else:

        return 3


# Функция проверки фамилии пользователя на валидность
def verify_surname(user_surname: str) -> int:

    """
    Проверяет фамилию пользователя на валидность

    Parameters
    ----------
    user_surname : str
            Строка, которая должна содержать фамилию пользователя

    Returns
    -------
    int
        Номер ошибки в словаре ошибок фамилии
    """

    if len(user_surname) < 3:

        return 0

    elif not user_surname.isalpha():

        return 1

    elif len(user_surname) > 13:

        return 2

    elif any(char not in alphabet for char in user_surname):

        return 4

    else:

        return 3


# Функция проверки дня рождения пользователя на валидность
def verify_birthday(user_birthday: str) -> int:

    """
    Проверяет дату рождения на валидность

    Parameters
    ----------
    user_birthday : str
            Строка, которая должна содержать день рождения пользователя

    Returns
    -------
    int
        Номер ошибки в словаре ошибок даты рождения
    """

    date = user_birthday.split(".")
    now = datetime.now().date().year - 18

    if len(date) != 3 or not all(part.isdigit() for part in date):

        return 1

    day, month, year = map(int, date)

    if day > 31 or month > 12:

        return 3

    if year > now:

        return 5

    return 4


# Функция проверки даты бронирования на валидность
def verify_data(user_date: str) -> int:

    """
    Проверяет дату бронирования на валидность

    Parameters
    ----------
    user_date : str
            Строка, которая должна содержать дату бронирования

    Returns
    -------
    int
        Номер ошибки в словаре ошибок даты
    """

    date = user_date.split(".")

    if len(date) != 3:

        return 1

    else:

        if (not date[0].isdigit()) or (not date[1].isdigit()) or (not date[2].isdigit()):

            return 2

        else:

            if int(date[0]) > 31 or int(date[1]) > 12:

                return 3

            elif int(date[2]) < datetime.now().date().year:

                return 5

            elif int(date[1]) > datetime.now().date().month + 1:

                return 6

            elif int(date[2]) > datetime.now().date().year:

                return 6

            else:

                date_value_object = datetime.strptime(user_date, "%d.%m.%Y")

                if date_value_object.date() >= datetime.now().date():

                    return 4

                else:

                    return 5


# Функция проверки времени бронирования на валидность
def verify_time(user_time: str) -> int:

    """
    Проверяет время бронирования на валидность

    Parameters
    ----------
    user_time : str
            Строка, которая должна содержать время бронирования

    Returns
    -------
    int
        Номер ошибки в словаре ошибок времени
    """

    times = user_time.split(":")

    if len(times) != 2:

        return 1

    else:

        if (not times[0].isdigit()) or (not times[1].isdigit()):

            return 2

        else:

            if (int(times[0]) > 23) or (int(times[1]) > 59):

                return 3

            elif (int(times[0]) > 3) and (int(times[0]) < 18):

                return 4

            else:

                return 5


# Функция проверки номера телефона на валидность
def verify_phone(user_phone: str) -> int:

    """
    Проверяет номер телефона на валидность

    Parameters
    ----------
    user_phone : str
            Строка, которая должна содержать номер телефона

    Returns
    -------
    int
        Номер ошибки в словаре ошибок номера телефона
    """

    phone = user_phone.split("-")

    if len(phone) != 5:

        return 1

    else:
        if phone[0] != "+7":

            return 2

        elif (len(phone[1]) != 3) or (not phone[1].isdigit()):

            return 3

        elif (len(phone[2]) != 3) or (not phone[2].isdigit()):

            return 3

        elif (len(phone[3]) != 2) or (not phone[3].isdigit()):

            return 3

        elif (len(phone[4]) != 2) or (not phone[4].isdigit()):

            return 3

        else:

            return 4
