from opera_admin import *


# Функция выбора номера телефона для назначения администратора
@throttle(2)
def adm_add(message: types.Message) -> None:

    """
    Позволяет владельцу выбрать номер телефона пользователя из БД для добавления в ряды администраторов

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Returns
    -------
    None
    """

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users WHERE adm != 'admin'")
    result = cursor.fetchall()
    cursor.close()

    if result:

        adm = bot.send_message(chat_id=message.chat.id,
                               text="Выберите номер телефона пользователя, которого хотите назначить Администратором:",
                               disable_notification=True,
                               reply_markup=buttons([i[0] for i in result], width=1))

        bot.register_next_step_handler(adm, add_admin)

    else:

        own = bot.send_message(chat_id=message.chat.id,
                               text='У Вас нет ни одного пользователя без статуса "Администратор"!',
                               disable_notification=True,
                               reply_markup=types.ReplyKeyboardRemove())

        sleep(5)

        bot.delete_message(chat_id=message.chat.id, message_id=own.message_id)

        bot.send_message(chat_id=message.chat.id,
                         text=owner_menu_desc, disable_notification=True,
                         reply_markup=inline_buttons(owner_menu))


# Функция добавления администратора
def add_admin(message: types.Message) -> None:

    """
    Позволяет владельцу добавить выбранный номер телефона пользователя в ряды Администраторов

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Raises
    ------
    TypeError
        Ловит исключение, если пользователя, с указанным номером телефона, нет в БД

    ValueError
        Ловит исключение, если номер телефона пользователя состоит не только из цифр

    Returns
    -------
    None
    """

    try:

        phones = message.text

        cursor = conn.cursor()
        cursor.execute("UPDATE users SET adm = 'admin' WHERE phone = ?", [phones])
        cursor.execute("SELECT * FROM users WHERE phone = ?", [phones])
        result = cursor.fetchone()
        cursor.execute("SELECT user_id FROM users WHERE phone = ?", [phones])
        user = cursor.fetchone()
        conn.commit()
        cursor.close()

        mess = bot.send_message(
            message.chat.id,
            f"Вы успешно добавили пользователя {result[2]} {result[3]} с номером {phones} в Администраторы!",
            disable_notification=True, reply_markup=types.ReplyKeyboardRemove())

        bot.send_message(chat_id=user[0], text="Вас добавили в Администраторы!\n\n"
                                               "Теперь Вы можете перейти в меню админа👇",
                         reply_markup=inline_buttons(main_menu_button))

        sleep(5)

        bot.delete_message(chat_id=message.chat.id, message_id=mess.message_id)

        bot.send_message(chat_id=message.chat.id, text=owner_go_desc,
                         disable_notification=True, reply_markup=inline_buttons(main_menu_button))

    except TypeError:

        adm = bot.send_message(chat_id=message.chat.id, text="Пользователя с таким номером телефона не существует!"
                                                             "Попробуйте ещё раз 👇", disable_notification=True)

        bot.register_next_step_handler(adm, del_admin)

    except ValueError:

        adm = bot.send_message(chat_id=message.chat.id, text=repeat_desc_phone, disable_notification=True)

        bot.register_next_step_handler(adm, del_admin)


# Функция выбора номера телефона для удаления администратора
@throttle(2)
def adm_del(message: types.Message) -> None:

    """
    Позволяет владельцу выбрать номер телефона пользователя для его удаления из Администраторов

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Returns
    -------
    None
    """

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users WHERE adm == 'admin'")
    result = cursor.fetchall()
    cursor.close()

    if result:

        adm = bot.send_message(chat_id=message.chat.id,
                               text="Выберите номер телефона пользователя, которого хотите убрать из Администраторов:",
                               disable_notification=True,
                               reply_markup=buttons([i[0] for i in result], width=1))

        bot.register_next_step_handler(adm, del_admin)

    else:

        own = bot.send_message(chat_id=message.chat.id, text='У вас нет ни одного Администратора!',
                               disable_notification=True,
                               reply_markup=types.ReplyKeyboardRemove())

        sleep(5)

        bot.delete_message(chat_id=message.chat.id, message_id=own.message_id)

        bot.send_message(chat_id=message.chat.id, text=owner_menu_desc, disable_notification=True,
                         reply_markup=inline_buttons(owner_menu))


# Функция удаления администратора
def del_admin(message: types.Message) -> None:

    """
    Позволяет владельцу удалить выбранный номер телефона пользователя из Администраторов

    Parameters
    ----------
    message : types.Message
        Значение сообщения из кэлбэк-запроса для дальнейшей работы

    Raises
    ------
    TypeError
        Ловит исключение, если Администратора, с указанным номером телефона, нет в БД

    ValueError
        Ловит исключение, если номер телефона Администратора состоит не только из цифр

    Returns
    -------
    None
    """

    try:

        phones = message.text

        cursor = conn.cursor()
        cursor.execute("UPDATE users SET adm = '' WHERE phone = ?", [phones])
        cursor.execute("SELECT * FROM users WHERE phone = ?", [phones])
        result = cursor.fetchone()
        conn.commit()
        cursor.close()

        mess = bot.send_message(
            message.chat.id,
            f"Вы успешно удалили пользователя {result[2]} {result[3]} с номером {phones} из Администраторов!",
            disable_notification=True, reply_markup=types.ReplyKeyboardRemove())

        sleep(5)

        bot.delete_message(chat_id=message.chat.id, message_id=mess.message_id)

        bot.send_message(chat_id=message.chat.id, text=owner_go_desc,
                         disable_notification=True, reply_markup=inline_buttons(main_menu_button))

    except TypeError:

        adm = bot.send_message(chat_id=message.chat.id, text="Администратора с таким номером телефона "
                                                             "не существует!\n\nПопробуйте ещё раз 👇",
                               disable_notification=True)

        bot.register_next_step_handler(adm, del_admin)

    except ValueError:

        adm = bot.send_message(chat_id=message.chat.id, text=repeat_desc_phone, disable_notification=True)

        bot.register_next_step_handler(adm, del_admin)
