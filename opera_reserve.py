from opera_verify import *


# Функция проверки брони и бронирования зала
def verify_reserve(message: types.Message, place: str) -> None:

    """
    Проверяет наличие бронировния у пользователя и, в случае отсутствия такового, бронирует зал

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    place : str
        Номер зала, который нужно забронировать

    Returns
    -------
    None
    """

    user_id = message.chat.id

    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users WHERE user_id = ?", [user_id])
    result_phone = cursor.fetchone()
    cursor.close()

    if int(place) in place_go:

        place_reserve = place_go[int(place)]

    else:

        place_reserve = ""

    if result_phone:

        cursor = conn.cursor()
        cursor.execute("SELECT date FROM users WHERE user_id = ?", [user_id])
        result = cursor.fetchone()
        cursor.close()

        date_value = result[0]

        date_list = list(new_month())

        if date_value:

            date_value_object = datetime.strptime(date_value, "%d.%m.%Y").date()

            if date_value_object >= datetime.now().date():

                bot.send_message(chat_id=message.chat.id,
                                 text=f"Извините, но Вы уже имеете бронь!\n\n"
                                      f"Своё бронирование Вы можете посмотреть по кнопке ниже!",
                                 disable_notification=True,
                                 reply_markup=inline_buttons(verify_res_menu))

            else:

                cursor = conn.cursor()
                cursor.execute("UPDATE users SET reserve = ? WHERE user_id = ?", (place_reserve, message.chat.id))
                cursor.close()

                if int(place) == 4:

                    reg = bot.send_message(chat_id=message.chat.id, text=good_message_table, disable_notification=True,
                                           reply_markup=buttons(table_res_main_list))

                    bot.register_next_step_handler(reg, reg_reserve)

                else:

                    reg = bot.send_message(chat_id=message.chat.id, text=good_message_place, disable_notification=True,
                                           reply_markup=buttons(date_list))

                    bot.register_next_step_handler(reg,
                                                   lambda message_reg_dat: reg_date(message_reg_dat, 0))

        else:

            cursor = conn.cursor()
            cursor.execute("UPDATE users SET reserve = ? WHERE user_id = ?", (place_reserve, message.chat.id))
            cursor.close()

            if int(place) == 4:

                reg = bot.send_message(chat_id=message.chat.id, text=good_message_table, disable_notification=True,
                                       reply_markup=buttons(table_res_main_list))

                bot.register_next_step_handler(reg, reg_reserve)

            else:

                reg = bot.send_message(chat_id=message.chat.id, text=good_message_place, disable_notification=True,
                                       reply_markup=buttons(date_list))

                bot.register_next_step_handler(reg, lambda message_reg_dat: reg_date(message_reg_dat, 0))


# Функция бронирования столика
def reg_reserve(message: types.Message) -> None:

    """
    Регистрирует столик, если значение зала будет "Основной зал"

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Returns
    -------
    None
    """

    user_id = message.from_user.id
    user_table_number = message.text

    try:

        table_number = int(user_table_number)

        if 1 <= table_number <= 12:

            date_list = list(new_month())

            cursor = conn.cursor()
            cursor.execute("UPDATE users SET new_table = ? WHERE user_id = ?", (table_number, user_id))
            cursor.close()

            reg = bot.send_message(
                chat_id=message.chat.id,
                text=f"Вы выбрали столик №{table_number}\n\n"
                f"Теперь введите дату, на которую хотите его забронировать\n\n"
                f"(К примеру: "
                + f"{datetime.now().date().day}".zfill(2)
                + "."
                + f"{datetime.now().date().month}".zfill(2)
                + "."
                + f"{datetime.now().date().year}"
                + ")👇", disable_notification=True,
                reply_markup=buttons(date_list))

            bot.register_next_step_handler(reg, lambda message_reg_dat: reg_date(message_reg_dat, table_number))

        else:

            reg = bot.send_message(chat_id=message.chat.id, text="Пожалуйста, выберите столик от 1 до 12:",
                                   disable_notification=True,
                                   reply_markup=buttons(table_res_main_list))

            bot.register_next_step_handler(reg, reg_reserve)

    except ValueError:

        reg = bot.send_message(chat_id=message.chat.id, text="Пожалуйста, введите номер столика цифрами от 1 до 12:",
                               disable_notification=True,
                               reply_markup=buttons(table_res_main_list))

        bot.register_next_step_handler(reg, reg_reserve)


# Функция регистрации даты бронирования
def reg_date(message: types.Message, table_number: int) -> None:

    """
    Регистрирует дату бронировния после брони столика, либо после брони зала

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    table_number : int
        Номер столика, который бронируется (Если столика нет, то значение столика == 0)

    Returns
    -------
    None
    """

    user_reg_date = message.text

    try:

        while True:

            num = verify_data(user_reg_date)

            if num in errors_date:

                desc = errors_date[num]

            elif num == 4:
                break

            else:

                desc = (
                        f"Вы ввели неверный формат даты!\n\n"
                        f"Попробуйте ввести дату как в примере\n\n"
                        f"(К примеру: "
                        + f"{datetime.now().date().day}".zfill(2)
                        + "."
                        + f"{datetime.now().date().month}".zfill(2)
                        + "."
                        + f"{datetime.now().date().year}"
                        + ")👇")

            reg = bot.send_message(chat_id=message.chat.id, text=desc, disable_notification=True)

            bot.register_next_step_handler(reg, lambda message_reg_dat: reg_date(message_reg_dat, 0))

            return

    except ValueError:

        reg = bot.send_message(chat_id=message.chat.id, text=f"Вы ввели неверный формат даты!\n\n"
                                                             f"В этом месяце нет столько дней!\n\n"
                                                             f"Введите реальную дату!",
                               disable_notification=True)

        bot.register_next_step_handler(reg, lambda message_reg_dat: reg_date(message_reg_dat, 0))

        return

    user_reg_date = user_reg_date.split(".")

    user_reg_date = (
        f"{user_reg_date[0]}".zfill(2)
        + "."
        + f"{user_reg_date[1]}".zfill(2)
        + "."
        + f"{user_reg_date[2]}")

    reg = bot.send_message(chat_id=message.chat.id, text=f"Ого! Едем дальше!\n\n"
                                                         f"Теперь введите время, к которому Вы придёте к нам\n\n"
                                                         f"(К примеру: 18:00)",
                           disable_notification=True, reply_markup=buttons(time_menu))

    bot.register_next_step_handler(reg, lambda message_reg_tim: reg_time(message_reg_tim, user_reg_date, table_number))


# Функция регистрации времени бронирования
def reg_time(message: types.Message, user_reg_date: str, table_number: int) -> None:

    """
    Регистрирует время бронирования после регистрации даты

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    user_reg_date : str
        Дата бронирования столика в зале или зала (в случае его наличия или отсутствия соответственно)

    table_number : int
        Номер столика, который бронируется (Если столика нет, то значение столика == 0)

    Returns
    -------
    None
    """

    user_reg_time = message.text

    num = verify_time(user_reg_time)

    if num in errors_time:

        message = bot.send_message(chat_id=message.chat.id, text=errors_time[num], disable_notification=True)

        bot.register_next_step_handler(
            message, lambda message_reg_tim: reg_time(message_reg_tim, user_reg_date, table_number))

        return

    else:

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE date = ? AND time = ? AND new_table = ?",
                       (user_reg_date, user_reg_time, table_number))
        result = cursor.fetchall()
        cursor.close()

        for row in result:

            if row:

                message = bot.send_message(chat_id=message.chat.id,
                                           text="Извините, выбранный столик уже занят на это время.\n\n"
                                                "Пожалуйста, выберите другое время 👇", disable_notification=True)

                bot.register_next_step_handler(
                    message, lambda message_reg_tim: reg_time(message_reg_tim, user_reg_date, table_number))

                return

        cursor = conn.cursor()
        cursor.execute("SELECT phone FROM users WHERE user_id = ?", [message.chat.id])
        result = cursor.fetchone()
        cursor.close()

        if result and result[0] is not None and result[0] != "":

            key_phone = ReplyKeyboardMarkup(resize_keyboard=True)
            btn_1 = types.KeyboardButton(f"Мой номер", request_contact=True)
            key_phone.add(btn_1)

        else:

            key_phone = types.ReplyKeyboardRemove()

        reg = bot.send_message(
            chat_id=message.chat.id,
            text=f"Остался всего один шаг!\n\n"
            f"Для завершения бронирования введите СВОЙ номер телефона и ожидайте подтверждения брони\n\n"
            f"(Пример: +7-999-999-99-99)", disable_notification=True,
            reply_markup=key_phone
        )

        bot.register_next_step_handler(
            reg, lambda message_reg_ph: reg_phone(message_reg_ph, user_reg_date, user_reg_time, table_number))


# Функция регистрации телефона
def reg_phone(message: types.Message, user_reg_date: str, user_reg_time: str, table_number: int) -> None:

    """
    Регистрирует номер телефона пользователя для бронирования

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    user_reg_date : str
        Дата бронирования столика в зале или зала (в случае его наличия или отсутствия соответственно)

    user_reg_time : str
        Время бронирования столика или зала

    table_number : int
        Номер столика, который бронируется (Если столика нет, то значение столика == 0)

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

    while True:

        num = verify_phone(user_reg_phone)

        if num in errors_phone:

            desc = errors_phone[num]

        elif num == 4:
            break

        else:

            desc = errors_phone[5]

        reg = bot.send_message(chat_id=message.chat.id, text=desc, disable_notification=True)

        bot.register_next_step_handler(
            reg,
            lambda message_reg_ph: reg_phone(message_reg_ph, user_reg_date, user_reg_time, table_number))

        return

    cursor = conn.cursor()
    cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (user_reg_phone, user_id))
    conn.commit()
    cursor.close()

    congratulation = bot.send_message(chat_id=message.chat.id, text=f"Ура! Бронирование завершено!\n\n"
                                                                    f"Ожидайте подтверждение от менеджера!",
                                      disable_notification=True, reply_markup=types.ReplyKeyboardRemove())

    message_admin(message, user_reg_date, user_reg_time, table_number, congratulation.message_id)


# Функция отправки менеджеру / администратору уведомления о желании забронировать место
def message_admin(message: types.Message, user_reg_date: str, user_reg_time: str,
                  table_number: int, congratulation: int) -> None:

    """
    Отправляет менеджеру / администратору бота (или владельцу, в случае отсутствия первых) информацию о бронировании

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    user_reg_date : str
        Дата бронирования столика в зале или зала (в случае его наличия или отсутствия соответственно)

    user_reg_time : str
        Время бронирования столика или зала

    table_number : int
        Номер столика, который бронируется (Если столика нет, то значение столика == 0)

    congratulation : int
        ID Сообщения, которое будет удалено после подтвержденной или отклонённой заявки на бронь

    Returns
    -------
    None
    """

    try:

        user_id = message.from_user.id

        cursor = conn.cursor()
        cursor.execute("UPDATE users SET date = ?, time = ?, new_table = ? WHERE user_id = ?",
                       (user_reg_date, user_reg_time, table_number, user_id))
        cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
        user = cursor.fetchone()
        cursor.execute("UPDATE users SET date = NULL, time = NULL WHERE user_id = ?", (user_id,))
        cursor.execute("SELECT * FROM users WHERE adm = 'admin'")
        user_admin = cursor.fetchall()
        conn.commit()
        cursor.close()

        key_reserve = InlineKeyboardMarkup()
        btn_1 = InlineKeyboardButton(
            "Добро ✅",
            callback_data=f"res_{user_reg_date}_{user_reg_time}_{message.chat.id}_{congratulation}_"
            f"{table_number}_{user_id}")
        btn_2 = InlineKeyboardButton("Отказ ❌", callback_data=f"resNot_{user_id}_{message.chat.id}_{congratulation}")
        key_reserve.add(btn_1, btn_2)

        if user_admin:

            if user[10] > 0:

                for i in range(len(user_admin)):

                    bot.send_message(
                        user_admin[i][1],
                        f"Пользователь {user[2]} {user[3]} желает забронировать:\n\n"
                        f"1️⃣ Место: {user[6]},\n\n"
                        f"2️⃣ Столик: {user[10]},\n\n"
                        f"3️⃣ Дата: {user[7]},\n\n"
                        f"4️⃣ Время: {user[8]},\n\n"
                        f"📱: {user[9]}\n\n"
                        f"И ждёт подтверждения брони:",
                        reply_markup=key_reserve)

            else:

                for i in range(len(user_admin)):

                    bot.send_message(
                        user_admin[i][1],
                        f"Пользователь {user[2]} {user[3]} желает забронировать:\n\n"
                        f"1️⃣ Место: {user[6]},\n\n"
                        f"2️⃣ Дата: {user[7]},\n\n"
                        f"3️⃣ Время: {user[8]},\n\n"
                        f"📱: {user[9]}\n\n"
                        f"И ждёт подтверждения брони:",
                        reply_markup=key_reserve)

        else:

            if user[10] > 0:

                bot.send_message(
                    owner,
                    f"У вас отсутствуют администраторы, поэтому Вам придётся подтверждать бронирование!\n\n\n"
                    f"Пользователь {user[2]} {user[3]} желает забронировать:\n\n"
                    f"1️⃣ Место: {user[6]},\n\n"
                    f"2️⃣ Столик: {user[10]},\n\n"
                    f"3️⃣ Дата: {user[7]},\n\n"
                    f"3️⃣ Время: {user[8]},\n\n"
                    f"📱: {user[9]}\n\n"
                    f"И ждёт подтверждения брони:",
                    reply_markup=key_reserve)

            else:

                bot.send_message(
                    owner,
                    f"У вас отсутствуют администраторы, поэтому Вам придётся подтверждать бронирование!\n\n\n"
                    f"Пользователь {user[2]} {user[3]} желает забронировать:\n\n"
                    f"1️⃣ Место: {user[6]},\n\n"
                    f"2️⃣ Дата: {user[7]},\n\n"
                    f"3️⃣ Время: {user[8]},\n\n"
                    f"📱: {user[9]}\n\n"
                    f"И ждёт подтверждения брони:",
                    reply_markup=key_reserve)

    except BaseException:

        bot.delete_message(chat_id=message.from_user.id, message_id=congratulation)

        bot.send_message(chat_id=message.from_user.id, text=sorry_res_know,
                         reply_markup=inline_buttons(main_menu_button))


# Функция подтверждения бронирования
@throttle(6)
def yes_reserve(call, user_reg_date: str, user_reg_time: str, table_number: str, userId: str) -> str:

    """
    Подтверждает бронирование пользователя администратором / менеджером или владельцем

    Parameters
    ----------
    call
        Кэлбэк-запрос при нажатии пользователем кнопки

    user_reg_date : str
        Дата бронирования столика в зале или зала (в случае его наличия или отсутствия соответственно)

    user_reg_time : str
        Время бронирования столика или зала

    table_number : str
        Номер столика, который бронируется (Если столика нет, то значение столика == 0)

    userId
        Строковое значение ID пользователя для преобразования в число

    Returns
    -------
    str
        Строковое значение (Ответ для администратора / владельца) с данными пользователя
    """

    cursor = conn.cursor()
    cursor.execute("UPDATE users SET date = ?, time = ?, new_table = ? WHERE user_id = ?",
                   (user_reg_date, user_reg_time, table_number, int(userId)))
    cursor.execute("SELECT * FROM users WHERE user_id = ?", [int(userId)])
    user = cursor.fetchone()
    cursor.close()
    conn.commit()

    bot.delete_message(call.message.chat.id, call.message.message_id)

    if int(user[10]) > 0:
        return (f"Вы успешно подтвердили бронь:\n\n"
                f"Заказчик: {user[2]} {user[3]},\n\n"
                f"Место: {user[6]},\n\n"
                f"Столик: {user[10]},\n\n"
                f"Число: {user[7]},\n\n"
                f"Время: {user[8]},\n\n"
                f"📱: {user[9]}\n\n")

    else:
        return (f"Вы успешно подтвердили бронь:\n\n"
                f"Заказчик: {user[2]} {user[3]},\n\n"
                f"Место: {user[6]},\n\n"
                f"Число: {user[7]},\n\n"
                f"Время: {user[8]},\n\n"
                f"📱: {user[9]}\n\n")


# Функция отказа в бронировании
@throttle(6)
def not_reserve(users: str) -> str:

    """
    Принимает ID пользователя и обновляет поля бронирования в БД при отказе в бронировании

    Parameters
    ----------
    users : str
        Строковое значение ID пользователя для преобразования в число

    Returns
    -------
    str
        Строковое значение (Ответ для администратора / владельца) с данными пользователя
    """

    users_id = int(users)

    cursor = conn.cursor()
    cursor.execute("UPDATE users SET reserve = NULL, date = NULL, time = NULL, new_table = NULL WHERE user_id = ?",
                   (users_id,))
    cursor.execute("SELECT * FROM users WHERE user_id = ?", [users_id])
    user = cursor.fetchone()
    conn.commit()
    cursor.close()

    return f"Вы успешно отклонили бронь пользователя {user[2]} {user[3]} с номером {user[9]}"
