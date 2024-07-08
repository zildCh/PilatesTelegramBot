import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters , ConversationHandler
import requests
from admin_commands import admin_send_photo, admin_send_message, handle_confirmation, send_regular_posts, admin_send_regular, admin_get_regular, admin_delete_post
from user_repository import UserRepository
from user import User
from PIL import Image

# # Замените на ваш токен
# TOKEN = '7475676929:AAENOqRV9rdtnL-WoEb3WHTNi-oIkuq1zA4'
# CHANNEL_ID = '@pilates_123_test'  # Замените на ваш канал
# #ADMIN_ID = '493470036'  # Замените на ваш ID админа
# ADMIN_ID = '1393684504'
# USERS_FILE = 'users.json'

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

config = load_config('config.json')

TOKEN = config['TOKEN']
CHANNEL_ID = config['CHANNEL_ID']
ADMIN_ID = config['ADMIN_ID']
USERS_FILE = config['USERS_FILE']

repo = UserRepository()

WORKOUT_VIDEOS = {
    'button_workout_1': 'https://www.youtube.com/watch?v=PbWnEIp5TME',
    'button_workout_2': 'https://www.youtube.com/watch?v=qiS3PIPsRhs',
}
WORKOUT_NAMES = {
    'button_workout_1': '🧘‍♀️ Осанка',
    'button_workout_2': '🤸‍♀️ Тренировка от целлюлита',
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    user = User(user_id, username)
    repo.add_user(user)
    #repo.delete_user(493470036)
    keyboard = [[InlineKeyboardButton("Получить бесплатную тренировку", callback_data='button_get_training')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Привет! Нажмите на кнопку ниже, чтобы получить бесплатную тренировку.',
                                    reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'button_get_training':
        keyboard = [[InlineKeyboardButton("Я подписался ✅", callback_data='button_check_subscription')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=query.message.chat_id,
                                       text=f"Пожалуйста, подпишитесь на наш канал {CHANNEL_ID}, затем нажмите на кнопку ниже:",
                                       reply_markup=reply_markup)
    elif query.data == 'button_check_subscription':
        await check_subscription(update, context)
    elif query.data.startswith('button_workout_'):
        await send_workout_link(update, context, query.data)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = CHANNEL_ID
    url = f'https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat_id}&user_id={user_id}'

    response = requests.get(url)
    data = response.json()

    if data['ok']:
        status = data['result']['status']
        if status in ['member', 'administrator', 'creator']:
            # Пользователь подписан
            await query.message.reply_text("Спасибо за подписку! Выберите тренировку:")
            # Отправка кнопок с тренировками
            keyboard = [
                [InlineKeyboardButton(f"{WORKOUT_NAMES['button_workout_1']}", callback_data='button_workout_1')],
                [InlineKeyboardButton(f"{WORKOUT_NAMES['button_workout_2']}", callback_data='button_workout_2')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await context.bot.send_message(chat_id=query.message.chat_id, text="Выберите одну из тренировок:", reply_markup=reply_markup)
            # Сохраняем информацию о том, что сообщение было отправлено
            context.user_data[user_id] = {
                'message_id': message.message_id,
                'edited': False  # Флаг для отслеживания того, было ли сообщение отредактировано
            }
        else:
            await query.message.reply_text("Вы еще не подписались на канал. Пожалуйста, подпишитесь и попробуйте снова.")
    else:
        await query.message.reply_text("Произошла ошибка при проверке подписки. Пожалуйста, попробуйте позже.")

async def send_workout_link(update: Update, context: ContextTypes.DEFAULT_TYPE, workout_key):
    query = update.callback_query
    workout_link = WORKOUT_VIDEOS.get(workout_key)
    if workout_link:
        workout_name = WORKOUT_NAMES.get(workout_key, "Неизвестная тренировка")  # Получаем название тренировки из словаря
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"Вот ссылка на выбранную тренировку: {workout_link}")

        # Редактируем сообщение, заменяя клавиатуру с одной кнопкой выбранной тренировки
        if query.message.chat_id in context.user_data and context.user_data[query.message.chat_id]['edited'] is False:
            try:
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(workout_name, callback_data=f'button_workout_{workout_key.split("_")[1]}')]])
                await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                                            message_id=context.user_data[query.message.chat_id][
                                                                'message_id'],
                                                            reply_markup=keyboard)

                # Помечаем сообщение как отредактированное
                context.user_data[query.message.chat_id]['edited'] = True
            except Exception as e:
                print(f"Error editing message: {e}")
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Ссылка на тренировку уже получена")

async def periodic_task(context: ContextTypes.DEFAULT_TYPE):
    await send_regular_posts(context)

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern='^button_'))

    application.add_handler(CommandHandler("admin_send", admin_send_message))
    application.add_handler(MessageHandler(filters.PHOTO & filters.User(int(ADMIN_ID)), admin_send_photo))

    application.add_handler(CommandHandler("admin_send_regular", admin_send_regular))
    application.add_handler(CommandHandler("admin_delete_post", admin_delete_post))
    application.add_handler(CommandHandler("admin_get_regular", admin_get_regular))  # Добавляем обработчик команды
    application.add_handler(CallbackQueryHandler(handle_confirmation))

    application.job_queue.run_repeating(periodic_task, interval=3600, first=0)

    application.run_polling()


if __name__ == '__main__':
    main()