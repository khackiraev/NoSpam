 "admin_panel": "Ба панели мудири хуш омадед. Шумо метавонед аз ин ҷо ба ҳама чатҳо пайғом фиристоед. Барои дидани омор, /stats нависед."
    }
}

# Создаем функцию для получения языка пользователя
def get_language(user_id):
    # Открываем подключение к базе данных
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    # Ищем пользователя в таблице users
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    # Закрываем подключение к базе данных
    conn.close()
    # Если пользователь найден, возвращаем его язык
    if result:
        return result[0]
    # Иначе возвращаем None
    else:
        return None

# Создаем функцию для установки языка пользователя
def set_language(user_id, language):
    # Открываем подключение к базе данных
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    # Обновляем или добавляем пользователя в таблицу users с указанным языком
    cursor.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)", (user_id, language))
    # Сохраняем изменения в базе данных
    conn.commit()
    # Закрываем подключение к базе данных
    conn.close()

# Создаем функцию для получения предупреждающего сообщения пользователя
def get_warning(user_id):
    # Открываем подключение к базе данных
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    # Ищем пользователя в таблице users
    cursor.execute("SELECT warning FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    # Закрываем подключение к базе данных
    conn.close()
    # Если пользователь найден и у него есть предупреждающее сообщение, возвращаем его
    if result and result[0]:
        return result[0]
    # Иначе возвращаем None
    else:
        return None

# Создаем функцию для добавления чата в базу данных
def add_chat(chat_id, chat_title, chat_type):
    # Открываем подключение к базе данных
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    # Добавляем чат в таблицу chats с указанными параметрами
    cursor.execute("INSERT OR IGNORE INTO chats (chat_id, chat_title, chat_type) VALUES (?, ?, ?)", (chat_id, chat_title, chat_type))
    # Сохраняем изменения в базе данных
    conn.commit()
    # Закрываем подключение к базе данных
    conn.close()

# Создаем функцию для добавления ссылки в базу данных
def add_link(user_id, chat_id, message_id, link, timestamp):
    # Открываем подключение к базе данных
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    # Добавляем ссылку в таблицу links с указанными параметрами
    cursor.execute("INSERT INTO links (user_id, chat_id, message_id, link, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, chat_id, message_id, link, timestamp))
    # Сохраняем изменения в базе данных
    conn.commit()
    # Закрываем подключение к базе данных
    conn.close()

# Создаем функцию для удаления ссылки из базы данных
def delete_link(link_id):
    # Открываем подключение к базе данных
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    # Удаляем ссылку из таблицы links по указанному идентификатору
    cursor.execute("DELETE FROM links WHERE link_id = ?", (link_id,))
    # Сохраняем изменения в базе данных
    conn.commit()
    # Закрываем подключение к базе данных
    conn.close()

# Создаем функцию для получения статистики из базы данных
def get_stats():
    # Открываем подключение к базе данных
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    # Получаем количество пользователей, активных пользователей, добавленных чатов и удаленных ссылок из таблиц users, chats и links
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM links")
    active_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT chat_id) FROM chats")
    total_chats = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM links")
    total_links = cursor.fetchone()[0]
    # Закрываем подключение к базе данных
    conn.close()
    # Возвращаем статистику в виде строки
    return f"Total users: {total_users}\nActive users: {active_users}\nTotal chats: {total_chats}\nTotal links deleted: {total_links}"

# Создаем функцию для проверки наличия ссылок в сообщении
def has_link(message):
    # Используем регулярное выражение для поиска ссылок в тексте сообщения
    pattern = r"(?:https?://|www\.)\S+"
    match = re.search(pattern, message)
    # Если найдено совпадение, возвращаем True и текст ссылки
    if match:
        return True, match.group()
    # Иначе возвращаем False и None
    else:
        return False, None

# Создаем функцию для отправки предупреждающего сообщения пользователю и удаления его сообщения со ссылкой через 30 секунд
def delete_link_and_warn(message):
    # Получаем идентификаторы пользователя, чата и сообщения из объекта message
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id
    # Получаем язык пользователя из базы данных или устанавливаем его по умолчанию на английский
    language = get_language(user_id) or "en"
    # Получаем предупреждающее сообщение пользователя из базы данных или используем его по умолчанию
    warning = get_warning(user_id) or languages[language]["default_warning"]
    # Получаем текст ссылки из сообщения пользователя
    _, link = has_link(message.text)
    # Добавляем ссылку в базу данных с текущим временем
    timestamp = time.time()
    add_link(user_id, chat_id, message_id, link, timestamp)
    # Отправляем предупреждающее сообщение пользователю в чат
    bot.send_message(chat_id, warning.format(link), reply_to_message_id=message_id)
    # Ждем 30 секунд
    time.sleep(30)
    # Удаляем сообщение пользователя со ссылкой из чата
    bot.delete_message(chat_id, message_id)
    # Удаляем ссылку из базы данных
    delete_link(message_id)

# Создаем обработчик команды /start
@bot.message_handler(commands=["start"])
def start(message):
    # Получаем идентификатор пользователя из объекта message
    user_id = message.from_user.id
    # Получаем язык пользователя из базы данных или устанавливаем его по умолчанию на английский
    language = get_language(user_id) or "en"
    # Отправляем приветственное сообщение пользователю с предложением выбрать язык
    bot.send_message(user_id, languages[language]["welcome"])

# Создаем обработчик команды /language
@bot.message_handler(commands=["language"])
def language(message):
    # Получаем идентификатор пользователя из объекта message
    user_id = message.from_user.id
    # Получаем язык пользователя из базы данных или устанавливаем его по умолчанию на английский
    language = get_language(user_id) or "en"
    # Отправляем сообщение пользователю с предложением выбрать язык
    bot.send_message(user_id, languages[language]["welcome"])

# Создаем обработчик команды /warning
@bot.message_handler(commands=["warning"])
def warning(message):
    # Получаем идентификатор пользователя из объекта message
    user_id = message.from_user.id
    # Получаем язык пользователя из базы данных или устанавливаем его по умолчанию на английский
    language = get_language(user_id) or "en"
    # Проверяем, есть ли аргумент после команды /warning
    if len(message.text.split()) > 1:
        # Если есть, то берем его как предупреждающее сообщение пользователя и устанавливаем его в базе данных
        warning = message.text.split(maxsplit=1)[1]
        set_warning(user_id, warning)
        # Отправляем сообщение пользователю с подтверждением установки предупреждающего сообщения
        bot.send_message(user_id, languages[language]["warning_set"].format(warning))
    else:
        # Если нет, то отправляем сообщение пользователю с просьбой ввести предупреждающее сообщение после команды /warning
        bot.send_message(user_id, "Please enter your warning message after the command /warning.")

# Создаем обработчик команды /stats для администратора бота (ваш идентификатор пользователя)
@bot.message_handler(commands=["stats"], func=lambda message: message.from_user.id == 5485398974)
def stats(message):
    # Получаем статистику из базы данных
    stats = get_stats()
    # Отправляем статистику пользователю в виде сообщения
    bot.send_message(message.chat.id, stats)

# Создаем обработчик текстовых сообщений для администратора бота (ваш идентификатор пользователя)
@bot.message_handler(content_types=["text"], func=lambda message: message.from_user.id == 5485398974)
def admin_panel(message):
    # Проверяем, является ли чат приватным (личным)
    if message.chat.type == "private":
        # Если да, то отправляем приветственное сообщение в панель администратора
        bot.send_message(message.chat.id, languages["en"]["admin_panel"])
    else:
                # Если нет, то отправляем текст сообщения во все чаты, в которых бот является администратором или участником
            # Открываем подключение к базе данных
            conn = sqlite3.connect("bot.db")
            cursor = conn.cursor()
            # Получаем список всех чатов из таблицы chats
            cursor.execute("SELECT chat_id FROM chats")
            chats = cursor.fetchall()
            # Закрываем подключение к базе данных
            conn.close()
            # Для каждого чата в списке
            for chat in chats:
                # Получаем идентификатор чата
                chat_id = chat[0]
                # Пытаемся отправить текст сообщения в чат
                try:
                    bot.send_message(chat_id, message.text)
                # Если возникает ошибка, то игнорируем ее
                except:
                    pass

# Создаем обработчик текстовых сообщений для обычных пользователей
@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Получаем идентификаторы пользователя и чата из объекта message
    user_id = message.from_user.id
    chat_id = message.chat.id
    # Получаем язык пользователя из базы данных или устанавливаем его по умолчанию на английский
    language = get_language(user_id) or "en"
    # Проверяем, является ли чат приватным (личным)
    if message.chat.type == "private":
        # Если да, то проверяем, является ли сообщение выбором языка из предложенных вариантов
        if message.text in ["English", "Русский", "O'zbek", "Тоҷикӣ"]:
            # Если да, то устанавливаем язык пользователя в соответствии с его выбором и сохраняем его в базе данных
            language = message.text[:2].lower()
            set_language(user_id, language)
            # Отправляем сообщение пользователю с подтверждением установки языка
            bot.send_message(user_id, languages[language]["language_set"])
        else:
            # Если нет, то отправляем сообщение пользователю с предложением выбрать язык
            bot.send_message(user_id, languages[language]["welcome"])
    else:
        # Если нет, то проверяем, есть ли ссылка в сообщении пользователя
        link, _ = has_link(message.text)
        if link:
            # Если да, то вызываем функцию для удаления ссылки и отправки предупреждающего сообщения
            delete_link_and_warn(message)
        else:
            # Если нет, то игнорируем сообщение пользователя
            pass

# Запускаем бота в бесконечном цикле
bot.polling(none_stop=True)

