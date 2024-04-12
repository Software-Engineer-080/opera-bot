from opera_reserve import *


# Функция удаления или добавления фотографий в выбранной категории
def opera_administrator(call, category_value: str) -> None:
    """
    Позволяет удалить или добавить фотографии в выбранной категории

    Parameters
    ----------
    call
        Кэлбэк-запрос при нажатии пользователем кнопки

    category_value : str
        Категория главного меню для удаления или добавления фотографий

    Returns
    -------
    None
    """

    adm_cat = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="Удалить все", callback_data=f"admDel_{category_value}")

    if (category_value == "sale") or (category_value == "reg"):

        btn2 = InlineKeyboardButton(text="Главное меню", callback_data=f"Главное меню")
        adm_cat.row(btn1, btn2)

        admin_question_desc = "УДАЛЯЕМ ВСЕ фотографии в данной категории\n\n" "или\n\n" "В главное меню?"

    else:

        btn2 = InlineKeyboardButton(text="Добавить ещё", callback_data=f"admAdd_{category_value}")
        btn3 = InlineKeyboardButton("Главное меню", callback_data=f"Главное меню")
        adm_cat.row(btn1, btn2)
        adm_cat.row(btn3)

        admin_question_desc = "УДАЛЯЕМ ВСЕ фотографии в данной категории\n\n" "или\n\n" "ДОБАВЛЯЕМ новые?"

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=admin_question_desc, reply_markup=adm_cat)


# Функция удаления всх фотографий в выбранной категории
def all_photo(message: types.Message, category: str) -> None:
    """
    Позволяет удалить все фотографии в выбранной категории

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    category : str
        Категория, в которой будут удаленый фотографии

    Returns
    -------
    None
    """

    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM base_{category}")
    conn.commit()
    cursor.close()

    if (category == "sale") or (category == 'reg'):

        bot.send_message(chat_id=message.chat.id, text=f"Отправьте 1 фото:", disable_notification=True)

        bot.register_next_step_handler(message, lambda msg: handle_photo_for(msg, category, 1))

    else:

        adm = bot.edit_message_text(message_id=message.message_id, chat_id=message.chat.id,
                                    text="Сколько фотографий вы хотите загрузить в данную категорию (Число)?")

        bot.register_next_step_handler(adm, lambda number: add_photo(number, category))


# Функция указания количества добавляемых фотографий
def new_photo(message: types.Message, category: str) -> None:
    """
    Позволяет указать количество фотографий, которое будет загружено в выбранную категорию

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    category : str
        Категория, в которую будут добавлены фотографии

    Returns
    -------
    None
    """

    adm = bot.edit_message_text(message_id=message.message_id, chat_id=message.chat.id,
                                text="Сколько фотографий вы хотите загрузить в данную категорию (Число)?")

    bot.register_next_step_handler(adm, lambda number: add_photo(number, category))


# Функция добавления одной фотографии в категорию
def add_photo(message: types.Message, category: str) -> None:
    """
    Позволяет добавить 1 фотографию в выбранную категорию

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    category : str
        Категория, в которую будут добавлены фотографии

    Raises
    ------
    ValueError
        Ловит исключение, если количество загружаемых фотографий введено не цифрами

    Returns
    -------
    None
    """

    try:

        num = int(message.text)

        if num <= 0:
            adm = bot.send_message(chat_id=message.chat.id, text="Число фотографий должно быть больше 0!",
                                   disable_notification=True)

            bot.register_next_step_handler(adm, lambda number: add_photo(number, category))

        bot.send_message(chat_id=message.chat.id, text=f"Отправьте 1 фото:", disable_notification=True)

        bot.register_next_step_handler(message, lambda msg: handle_photo_for(msg, category, 1, num))

    except ValueError:

        adm = bot.send_message(chat_id=message.chat.id, text="Введите количество загружаемых фотографий числом!",
                               disable_notification=True)

        bot.register_next_step_handler(adm, lambda number: add_photo(number, category))


# Функция добавления фотографий, если их больше одной
def handle_photo_for(message: types.Message, category: str, current_photo_num: int, total_photos: int = None) -> None:
    """
    Позволяет добавить остальные фотографии, если их больше 1

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    category : str
        Категория, в которую будут добавлены фотографии

    current_photo_num : int
        Номер текущей добавляемой фотографии

    total_photos : int, optional
        Общее количество добавляемых фотографий

    Returns
    -------
    None
    """

    if message.photo:

        photo = max(message.photo, key=lambda x: x.height)
        file_id = photo.file_id

        cursors = conn.cursor()
        cursors.execute(f"INSERT INTO base_{category} (url) VALUES (?)", (file_id,))
        conn.commit()
        cursors.close()

        if category == "sale":

            bot.send_message(chat_id=message.chat.id, text="Фотография успешно добавлена!", disable_notification=True,
                             reply_markup=inline_buttons(main_menu_button))

        elif (category == "new") or (category == 'reg'):

            message = bot.send_message(chat_id=message.chat.id,
                                       text=f"Введите описание для фотографии {current_photo_num}:",
                                       disable_notification=True)

            bot.register_next_step_handler(
                message, lambda msg: handle_photo_description(msg, category, file_id, current_photo_num, total_photos))

        else:

            current_photo_num += 1

            if current_photo_num <= total_photos:

                bot.send_message(chat_id=message.chat.id, text=f"Отправьте {current_photo_num} фото:",
                                 disable_notification=True)

                bot.register_next_step_handler(
                    message, lambda msg: handle_photo_for(msg, category, current_photo_num, total_photos))

            else:

                bot.send_message(chat_id=message.chat.id, text="Все фотографии успешно добавлены!",
                                 disable_notification=True, reply_markup=inline_buttons(main_menu_button))

    else:

        bot.send_message(chat_id=message.chat.id, text="Пожалуйста, отправьте картинку!", disable_notification=True)

        bot.register_next_step_handler(
            message, lambda msg: handle_photo_for(msg, category, current_photo_num, total_photos))


# Функция добавления описания к каждой фотографии
def handle_photo_description(message: types.Message, category: str, file_id: str, current_photo_num: int,
                             total_photos: int) -> None:
    """
    Позволяет добавить описание к фотографиям в выбранной категории

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    category : str
        Категория, в которую будут добавлены фотографии

    file_id : str
        ID фотографии, к которой будет добавлено описание

    current_photo_num : int
        Номер текущей добавляемой фотографии

    total_photos : int, optional
        Общее количество добавляемых фотографий

    Returns
    -------
    None
    """

    desc = message.text

    cursors = conn.cursor()
    cursors.execute(f"UPDATE base_{category} SET desc = ? WHERE url = ?", (desc, file_id,))
    conn.commit()
    cursors.close()

    current_photo_num += 1

    if category == 'reg':

        bot.send_message(chat_id=message.chat.id, text="Все фотографии успешно добавлены!", disable_notification=True,
                         reply_markup=inline_buttons(main_menu_button))

    elif current_photo_num <= total_photos:

        bot.send_message(chat_id=message.chat.id, text=f"Отправьте {current_photo_num} фото:",
                         disable_notification=True)

        bot.register_next_step_handler(
            message, lambda msg: handle_photo_for(msg, category, current_photo_num, total_photos))

    else:

        bot.send_message(chat_id=message.chat.id, text="Все фотографии успешно добавлены!", disable_notification=True,
                         reply_markup=inline_buttons(main_menu_button))


# Функция выбора телефона пользователя для удаления конкретной брони
def delete_res(message: types.Message) -> None:
    """
    Позволяет выбрать номер телефона пользователя, чьё бронирование нужно удалить

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Raises
    ------
    BaseException
        Ловит исключение невозможности редактирования сообщения

    Returns
    -------
    None
    """

    try:

        cursor = conn.cursor()
        cursor.execute("SELECT user_id, date, time, phone FROM users WHERE date IS NOT NULL AND time IS NOT NULL")
        user = cursor.fetchall()
        cursor.close()

        if user:

            user_list = []

            for i in range(len(user)):

                date = verify_data(user[i][1])
                times = verify_time(user[i][2])

                if (date == 4) and (times == 5):

                    user_list.append(user[i][3])

                else:

                    phones = user[i][3]
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE users SET reserve = NULL, date = NULL, time = NULL, new_table = NULL WHERE phone = ?",
                        (phones,))
                    cursor.close()
                    conn.commit()

            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            adm = bot.send_message(chat_id=message.chat.id,
                                   text="Выберите номер телефона пользователя, чьё бронирование хотите удалить:",
                                   disable_notification=True, reply_markup=buttons(user_list, width=2))

            bot.register_next_step_handler(adm, del_one_res)

        else:

            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text="Бронирования отсутствуют!", reply_markup=inline_buttons(main_menu_button))

    except BaseException:

        pass


# Функция удаления конкретного бронирования
def del_one_res(message: types.Message) -> None:
    """
    Позволяет удалить бронирование у выбранного пользователя

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Returns
    -------
    None
    """

    phones = message.text

    cursor = conn.cursor()
    cursor.execute("UPDATE users SET reserve = NULL, date = NULL, time = NULL, new_table = NULL WHERE phone = ?",
                   (phones,))
    cursor.close()
    conn.commit()

    adm = bot.send_message(chat_id=message.chat.id,
                           text=f"Вы успешно удалили бронировние у пользователя с номером {phones} !\n\n"
                                f"Можете продолжать работу!", disable_notification=True,
                           reply_markup=types.ReplyKeyboardRemove())

    sleep(5)

    bot.delete_message(chat_id=message.chat.id, message_id=adm.message_id)

    if message.chat.id == owner:

        bot.send_message(chat_id=message.chat.id, text=admin_menu_desc, disable_notification=True,
                         reply_markup=inline_buttons(owner_menu))

    else:

        bot.send_message(chat_id=message.chat.id, text=admin_menu_desc, disable_notification=True,
                         reply_markup=inline_buttons(admin_menu))


# Функция создания рассылки
def new_sex_func(message: types.Message, sex: str | None) -> None:

    """
    Функция по созданию рассылки пользователям

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    sex : str | None
        Название гендерной принадлежности для рассылки

    Raises
    ------
    BaseException
        Ловит все возможные исключения в данной функции

    Returns
    -------
    None
    """

    try:

        bot.send_message(chat_id=message.chat.id, text=f"Отправьте фото рассылки:", disable_notification=True)

        bot.register_next_step_handler(message, lambda msg: handle_photo_sex(msg, sex))

    except BaseException:

        pass


# Функция добавления фотографии рассылки
def handle_photo_sex(message: types.Message, sex: str | None):

    """
    Функция по добавлению фотографии в рассылку

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    sex : str | None
        Название гендерной принадлежности для рассылки

    Raises
    ------
    BaseException
        Ловит все возможные исключения в данной функции

    Returns
    -------
    None
    """

    try:

        if message.photo:

            photo = max(message.photo, key=lambda x: x.height)

            file_id = photo.file_id

            bot.send_message(chat_id=message.chat.id, text="Отправьте текст рассылки:", disable_notification=True)

            bot.register_next_step_handler(message, lambda msg: handle_sex_desc(msg, sex, file_id))

        else:

            bot.send_message(chat_id=message.chat.id, text="Пожалуйста, отправьте картинку!", disable_notification=True)

            bot.register_next_step_handler(message, lambda msg: handle_photo_sex(msg, sex))

    except BaseException:

        pass


# Функция добавления текста рассылки и отправки её
def handle_sex_desc(message: types.Message, sex: str | None, file_id: str) -> None:

    """
    Функция по добавлению текста к фотографии и отправке рассылки

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    sex : str | None
        Название гендерной принадлежности для рассылки

    file_id : str
        ID фотографии для её отправки в рассылке

    Returns
    -------
    None
    """

    if message.text:

        desc = message.text

        if sex is not None:

            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE sex = ?", (sex,))
            users_info = cursor.fetchall()
            cursor.close()

        else:

            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            users_info = cursor.fetchall()
            cursor.close()

        for user_info in users_info:

            info_id = user_info[0]

            bot.send_photo(chat_id=info_id, photo=file_id, caption=desc, protect_content=True)

        bot.send_message(chat_id=message.chat.id, text="Вы успешно провели рассылку!\n\n"
                                                       "Можете вернуться в главное меню!", disable_notification=True,
                         reply_markup=inline_buttons(main_menu_button))

    else:

        bot.send_message(chat_id=message.chat.id, text="Пожалуйста, отправьте текст рассылки!",
                         disable_notification=True)

        bot.register_next_step_handler(message, lambda msg: handle_sex_desc(msg, sex, file_id))
