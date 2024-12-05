import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Список пользователей, которые участвуют в розыгрыше
users = []

# Словарь для хранения пар (например, кто с кем)
pairs = {}

# Создание клавиатуры с кнопками
def create_keyboard():
    keyboard = [
        [InlineKeyboardButton("Добавить пользователей", callback_data='add_users')],
        [InlineKeyboardButton("Сгенерировать пары", callback_data='generate_pairs')],
        [InlineKeyboardButton("Показать пары", callback_data='show_pairs')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Команда /start для начала работы с ботом
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = create_keyboard()
    await update.message.reply_text("Привет! Я бот для выбора случайных пар.", reply_markup=reply_markup)

# Обработка нажатий на инлайн-кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'add_users':
        await query.message.reply_text("Введите имена пользователей через пробел:")
        context.user_data['state'] = 'add_users'
    elif query.data == 'generate_pairs':
        await generate_pairs(query.message, context)
    elif query.data == 'show_pairs':
        await pairs_list(query.message, context)

# Добавление пользователей
async def add_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    new_users = update.message.text.split()
    users.extend(new_users)
    reply_markup = create_keyboard()
    await update.message.reply_text(f"Добавлены пользователи: {', '.join(new_users)}", reply_markup=reply_markup)
    context.user_data['state'] = None

# Генерация пар
async def generate_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pairs
    if len(users) < 2:
        reply_markup = create_keyboard()
        await update.reply_text("Для генерации пар необходимо минимум 2 пользователя.", reply_markup=reply_markup)
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
    reply_markup = create_keyboard()
    await update.reply_text("Пары успешно сгенерированы! Для получения списка пар используйте кнопку 'Показать пары'.", reply_markup=reply_markup)

# Вывод списка пар
async def pairs_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not pairs:
        reply_markup = create_keyboard()
        await update.reply_text("Сначала нужно сгенерировать пары с помощью кнопки 'Сгенерировать пары'.", reply_markup=reply_markup)
        return
    response = "Сгенерированные пары:\n"
    for user, partner in pairs.items():
        if partner:
            response += f"{user} - {partner}\n"
        else:
            response += f"{user} остался без пары.\n"
    reply_markup = create_keyboard()
    await update.reply_text(response, reply_markup=reply_markup)

# Основная функция для запуска бота
def main():
    TOKEN = '7308807733:AAF94d0IlHAuJI9PN9HJWjMBcTtRMD333FQ'
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_users))

    application.run_polling()

if __name__ == '__main__':
    main()