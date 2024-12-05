import random
import pandas as pd
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Список пользователей, которые участвуют в розыгрыше
users = []

# Словарь для хранения пар (например, кто с кем)
pairs = {}

# Команда /start для начала работы с ботом
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот для выбора случайных пар. Чтобы загрузить пользователей, отправьте /upload.")

# Команда /upload для загрузки таблицы с пользователями
def upload(update: Update, context: CallbackContext):
    if update.message.document:
        file = update.message.document.get_file()
        file.download('users.csv')
        update.message.reply_text("Файл успешно загружен!")
        process_csv()  # Обработка CSV после загрузки
    else:
        update.message.reply_text("Пожалуйста, отправьте файл с пользователями.")

# Функция для обработки CSV файла
def process_csv():
    global users
    users = []
    try:
        df = pd.read_csv('users.csv')
        if "Username" not in df.columns:
            print("Столбец 'Username' отсутствует в файле.")
            return
        users = df['Username'].dropna().tolist()
        print(f"Загружены пользователи: {users}")
    except Exception as e:
        print(f"Ошибка при обработке CSV: {e}")

# Команда /generate_pairs для создания случайных пар
def generate_pairs(update: Update, context: CallbackContext):
    global pairs
    if len(users) < 2:
        update.message.reply_text("Для генерации пар необходимо минимум 2 пользователя.")
        return
    shuffled_users = users.copy()
    random.shuffle(shuffled_users)
    pairs.clear()
    for i in range(0, len(shuffled_users), 2):
        if i + 1 < len(shuffled_users):
            pairs[shuffled_users[i]] = shuffled_users[i + 1]
    if len(shuffled_users) % 2 != 0:
        last_user = shuffled_users[-1]
        pairs[last_user] = None
    update.message.reply_text("Пары успешно сгенерированы! Для получения списка пар используйте команду /pairs.")

# Команда /pairs для вывода списка пар
def pairs_list(update: Update, context: CallbackContext):
    if not pairs:
        update.message.reply_text("Сначала нужно сгенерировать пары с помощью команды /generate_pairs.")
        return
    response = "Сгенерированные пары:\n"
    for user, partner in pairs.items():
        if partner:
            response += f"{user} - {partner}\n"
        else:
            response += f"{user} остался без пары.\n"
    update.message.reply_text(response)

# Основная функция для запуска бота
def main():
    TOKEN = '7308807733:AAF94d0IlHAuJI9PN9HJWjMBcTtRMD333FQ'
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("upload", upload))
    dp.add_handler(CommandHandler("generate_pairs", generate_pairs))
    dp.add_handler(CommandHandler("pairs", pairs_list))
    dp.add_handler(MessageHandler(Filters.document.mime_type("text/csv"), upload))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()