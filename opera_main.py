from opera_owner import *


@bot.message_handler(commands=["start"])
@throttle(5)
def send_welcome(message: types.Message) -> None:

    """
    Обрабатывает команду '/start' и выводит приветственное сообщение

    Parameters
    ----------
    message : types.Message
        Значение сообщения для дальнейшей работы

    Returns
    -------
    None
    """

    cursor = conn.cursor()
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT,
                surname TEXT,
                birthday INTEGER,
                star INTEGER,
                reserve TEXT,
                date INTEGER,
                time INTEGER,
                phone INTEGER,
                new_table INTEGER,
                adm TEXT DEFAULT '',
                sex TEXT
            )
        """
    )
    conn.commit()

    user_id = message.chat.id

    if user_id == owner:

        bot.send_message(message.chat.id, owner_menu_desc, reply_markup=inline_buttons(owner_menu, buttons_per_row=2))

    else:

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
        user = cursor.fetchone()
        cursor.close()

        if user:

            if user[11] == "admin":

                bot.send_message(message.chat.id, admin_menu_desc, reply_markup=inline_buttons(admin_menu))

            else:

                user_name = user[2]

                bot.send_message(message.chat.id, f"Рады снова Вас видеть, {user_name}!",
                                 reply_markup=inline_buttons(user_menu))

        else:

            welcome = bot.send_message(message.chat.id, f"Здравствуйте 👋\n\nВы раньше у нас не были 🤔\n\n"
                                                        f"Давайте познакомимся!")

            sleep(4)

            send_name = bot.edit_message_text(chat_id=message.chat.id, message_id=welcome.message_id,
                                              text="Введите Своё имя 👇")

            bot.register_next_step_handler(send_name, reg_name)

        cursor.close()


@bot.message_handler(commands=["star"])
@throttle(5)
def send_star(message: types.Message) -> None:

    """
    Позволяет пользователю выбрать оценку для дальнейшего написания отзыва о компании

    Parameters
    ----------
    message : types.Message
        Значение сообщения для дальнейшей работы

    Returns
    -------
    None
    """

    user_id = message.chat.id

    if user_id == owner:

        pass

    else:

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
        user = cursor.fetchone()
        cursor.close()

        if user[11] == "admin":

            pass

        else:

            bot.send_message(chat_id=message.chat.id, text=review_desc, reply_markup=inline_buttons(rate_menu))


@bot.message_handler(commands=["my_res"])
@throttle(5)
def mess_info(message: types.Message) -> None:

    """
    Позволяет пользователю посмотреть его текущее бронирование

    Parameters
    ----------
    message : types.Message
        Значение сообщения для дальнейшей работы

    Returns
    -------
    None
    """

    user_id = message.chat.id

    if user_id == owner:

        pass

    else:

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
        user = cursor.fetchone()
        cursor.close()

        if user[11] == "admin":

            pass

        else:

            edit = bot.send_message(chat_id=message.chat.id, text="Сверяем информацию!")

            bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

            sleep(4)

            info_reserve(message, edit)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: types.CallbackQuery) -> None:

    """
    Позволяет обрабатывать все указанные кэлбэк-запросы

    Parameters
    ----------
    call
        Кэлбэк-запрос при нажатии пользователем кнопки

    Raises
    ------
    BaseException
        Ловит исключение невозможности редактирования сообщения

    Returns
    -------
    None
    """

    # Владелец ---------------------------------------

    if call.data == "+ админ":

        adm_add(call.message)

    elif call.data == "- админ":

        adm_del(call.message)

    # Администратор ---------------------------------------

    elif call.data == "Бронь 🆑":

        try:

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите, что из бронирования Вы хотите удалить:",
                                  reply_markup=inline_buttons(admin_res_menu, buttons_per_row=1))

        except BaseException:

            pass

    elif call.data == "Конкретная бронь":

        delete_res(call.message)

    elif call.data == "Всё бронировние":

        try:

            cursor = conn.cursor()
            cursor.execute("UPDATE users SET reserve = NULL, date = NULL, time = NULL, new_table = NULL")
            cursor.close()
            conn.commit()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы успешно сбросили все бронирования!",
                                  reply_markup=inline_buttons(main_menu_button))

        except BaseException:

            pass

    elif call.data == 'Регистрация':

        opera_administrator(call, 'reg')

    elif call.data.startswith("admDel_"):

        adm_menu = call.data.split("_")[-1]

        all_photo(call.message, adm_menu)

    elif call.data.startswith("admAdd_"):

        adm_menu = call.data.split("_")[-1]

        new_photo(call.message, adm_menu)

    elif call.data == '⚠️Рассылка ⚠️':

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=menu_news_desc, reply_markup=inline_buttons(news_menu))

    elif call.data == 'Мужчинам':

        sex = 'Мужской'

        new_sex_func(call.message, sex)

    elif call.data == 'Женщинам':

        sex = 'Женский'

        new_sex_func(call.message, sex)

    elif call.data == 'Всем':

        sex = None

        new_sex_func(call.message, sex)

    # Профиль ---------------------------------------

    elif call.data == "👤Профиль":

        get_user_data(call.message)

    elif call.data == "🔖 Моя бронь":

        try:

            info_reserve(call.message, call.message)

        except BaseException:

            pass

    elif call.data == "Отменить бронь":

        try:

            bot.send_chat_action(chat_id=call.message.chat.id, action=ChatAction.TYPING)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=cancel_res_desc, reply_markup=inline_buttons(main_menu_button))

        except BaseException:

            pass

    # Резервирование ---------------------------------------

    elif (call.data == "Резерв 🔏") or (call.data == "Назад ▶️"):

        try:

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите зал к просмотру!",
                                  reply_markup=inline_buttons(res_menu, buttons_per_row=2))

        except BaseException:

            pass

    elif call.data in place_category:

        try:

            bot.delete_message(call.message.chat.id, call.message.message_id)

            category_value = place_category[call.data]

            sending_photo(call.message, category_value)

        except BaseException:

            pass

    elif call.data.startswith("reserve_"):

        try:

            bot.delete_message(call.message.chat.id, call.message.message_id)

            place = call.data.split("_")[-1]

            verify_reserve(call.message, place)

        except BaseException:

            pass

    elif call.data == "К залам ⏏️":

        try:

            bot.delete_message(call.message.chat.id, call.message.message_id)

            bot.send_message(chat_id=call.message.chat.id, text="Выберите зал к просмотру!", disable_notification=True,
                             reply_markup=inline_buttons(res_menu, buttons_per_row=2))

        except BaseException:

            pass

    elif call.data.startswith("res_"):

        try:

            date, times, cht_id, mes_id, table, userId = (call.data.split("_")[1], call.data.split("_")[2],
                                                          call.data.split("_")[3], call.data.split("_")[4],
                                                          call.data.split("_")[-2], call.data.split("_")[-1])

            bot.delete_message(cht_id, mes_id)

            bot.send_message(call.message.chat.id, text=yes_reserve(call, date, times, table, userId),
                             disable_notification=True)

            if int(table) != 0:

                bot.send_message(
                    int(userId),
                    text="Администратор подтвердил Ваше бронирование!\n\n"
                         f"Ожидаем Вас {date} в {times} на {table} столик!\n\n"
                         f"❗️Своё бронирование Вы можете посмотреть по кнопке ниже или же в профиле❗️\n\n"
                         "Приятного отдыха!", reply_markup=inline_buttons(menu_user_res)
                )

            else:

                bot.send_message(
                    int(userId),
                    text="Администратор подтвердил Ваше бронирование!\n\n"
                         f"Ожидаем Вас {date} в {times}!\n\n"
                         f"❗️Своё бронирование Вы можете посмотреть по кнопке ниже или же в профиле❗️\n\n"
                         "Приятного отдыха!", reply_markup=inline_buttons(menu_user_res)
                )

        except:

            try:

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=admin_desc_know)

                sleep(5)

                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            except:

                pass

    elif call.data.startswith("resNot_"):

        try:

            userId, chatId, messId = call.data.split("_")[1], call.data.split("_")[-2], call.data.split("_")[-1]

            bot.send_chat_action(chat_id=call.message.chat.id, action=ChatAction.TYPING)

            bot.delete_message(chatId, messId)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=not_reserve(userId))

            bot.send_chat_action(chat_id=chatId, action=ChatAction.TYPING)

            bot.send_message(chat_id=chatId, text=sorry_res_not, reply_markup=inline_buttons(main_menu_button))

        except:

            try:

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=admin_desc_know)

                sleep(5)

                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            except:

                pass

    # Меню ---------------------------------------

    elif (call.data == "🍽 Меню️") or (call.data == "🔁 Меню️"):

        try:

            user_id = call.message.chat.id

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
            user = cursor.fetchone()
            cursor.close()

            if (user[11] == "admin") or (user[1] == owner):

                desc = "Выберите меню, которое хотите поменять!"

            else:

                desc = "Здесь Вы можете найти различное меню!"

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=desc,
                                  reply_markup=inline_buttons(food_menu, buttons_per_row=2))

        except BaseException:

            pass

    elif call.data in menu_category:

        try:

            user_id = call.message.chat.id

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
            user = cursor.fetchone()
            cursor.close()

            if (user[11] == "admin") or (user[1] == owner):

                category_value = menu_category[call.data]

                opera_administrator(call, category_value)

            else:

                bot.delete_message(call.message.chat.id, call.message.message_id)

                category_value = menu_category[call.data]

                sending_photo(call.message, category_value)

        except BaseException:

            pass

    elif call.data == "Ко всем меню ↘️":

        try:

            bot.delete_message(call.message.chat.id, call.message.message_id)

            bot.send_message(chat_id=call.message.chat.id, text=menu_desc,
                             disable_notification=True, reply_markup=inline_buttons(food_menu, buttons_per_row=2))

        except BaseException:

            pass

    # Новинки ---------------------------------------

    elif (call.data == "Новинки 🔥") or (call.data == "🔁 Новинки"):

        try:

            user_id = call.message.chat.id

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
            user = cursor.fetchone()
            cursor.close()

            if (user[11] == "admin") or (user[1] == owner):

                category_value = "new"

                opera_administrator(call, category_value)

            else:

                bot.delete_message(call.message.chat.id, call.message.message_id)

                sending_photo(call.message, "base_new")

        except BaseException:

            pass

    # Акции ---------------------------------------

    elif (call.data == "🎁 Акции") or (call.data == "🔁 Акции"):

        try:

            user_id = call.message.chat.id

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
            user = cursor.fetchone()
            cursor.close()

            if (user[11] == "admin") or (user[1] == owner):

                category_value = "sale"

                opera_administrator(call, category_value)

            else:

                bot.delete_message(call.message.chat.id, call.message.message_id)

                sale_photo(call.message)

        except BaseException:

            pass

    elif call.data == "15 %":

        bot.answer_callback_query(call.id, text=percent_desc, show_alert=True)

    elif call.data == "Подарок 🎉":

        bot.answer_callback_query(call.id, text=desc_present, show_alert=True)

    # Отзыв ---------------------------------------

    elif call.data == "Отзыв 💬":

        try:

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=review_desc,
                                  reply_markup=inline_buttons(rate_menu))

        except BaseException:

            pass

    elif call.data in ["1⭐️", "2⭐️", "3⭐️", "4⭐️", "5⭐️"]:

        stars = int(call.data.replace("⭐️", ""))

        if stars <= 3:

            min_star(call.message, stars)

        else:

            max_star(call.message, stars)

    # Мероприятия ---------------------------------------

    elif (call.data == "⚡️Мероприятия⚡️") or (call.data == "🔁 Эвент"):

        try:

            user_id = call.message.chat.id

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
            user = cursor.fetchone()
            cursor.close()

            if (user[11] == "admin") or (user[1] == owner):

                category_value = "event"

                opera_administrator(call, category_value)

            else:

                bot.delete_message(call.message.chat.id, call.message.message_id)

                sending_photo(call.message, "base_event")

        except BaseException:

            pass

    # Другое ---------------------------------------

    elif call.data == "Главное меню":

        try:

            user_id = call.message.chat.id

            if user_id == owner:

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=owner_menu_desc, reply_markup=inline_buttons(owner_menu, buttons_per_row=2))

            else:

                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", [user_id])
                user = cursor.fetchone()
                cursor.close()

                if user:

                    if user[11] == "admin":

                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=admin_menu_desc, reply_markup=inline_buttons(admin_menu))

                    else:

                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=user_menu_desc, reply_markup=inline_buttons(user_menu))

        except BaseException:

            pass

    elif call.data.startswith("prev_"):

        page = int(call.data.split("_")[-1]) - 1

        menu = call.data.split("_")[-2]

        if page < 1:
            total_pages = get_total_pages(f"base_{menu}")

            page = total_pages

        sending_photo(call.message, f"base_{menu}", page=page, previous_message=call.message.id)

    elif call.data.startswith("next_"):

        page = int(call.data.split("_")[-1]) + 1

        menu = call.data.split("_")[-2]

        total_pages = get_total_pages(f"base_{menu}")

        if page > total_pages:

            page = 1

        sending_photo(call.message, f"base_{menu}", page=page, previous_message=call.message.message_id)

    elif call.data == "Вернуться ⤴️":

        try:

            bot.delete_message(call.message.chat.id, call.message.message_id)

            bot.send_message(chat_id=call.message.chat.id, text=user_menu_desc, disable_notification=True,
                             reply_markup=inline_buttons(user_menu))

        except BaseException:

            pass

    elif call.data == " ":

        pass

    else:

        bot.answer_callback_query(call.id, text="Команда в разработке!")


while True:
    try:
        print('Бот запущен!')
        bot.polling(none_stop=True, interval=1)
    except:
        continue
