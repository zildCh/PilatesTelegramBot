import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters , ConversationHandler
import requests
from admin_commands import admin_send_photo,admin_send_video, admin_send_message, handle_confirmation, send_regular_posts, admin_send_regular, admin_get_regular, admin_delete_post, admin_delete_all_posts
from user_repository import UserRepository
from user import User
from PIL import Image
from google_sheets import GoogleSheets
def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

config = load_config('config.json')

TOKEN = config['TOKEN']
CHANNEL_ID = config['CHANNEL_ID']
INVITE_LINK = config['INVITE_LINK']
ADMIN_ID = config['ADMIN_ID']
USERS_FILE = config['USERS_FILE']
google_sheets = GoogleSheets('credentials.json', 'AleksandraPilatesBotData')
repo = UserRepository(google_sheets)




# WORKOUT_VIDEOS = {
#     'button_workout_1': 'https://www.youtube.com/watchv?v=PbWnEIp5TME',
#     'button_workout_2': 'https://www.youtube.com/watch?v=qiS3PIPsRhs',
# }
# WORKOUT_NAMES = {
#     'button_workout_1': '🧘‍♀️ Осанка',
#     'button_workout_2': '🤸‍♀️ Тренировка от целлюлита',
# }
WORKOUT_NAMES = {
    'button_workout_1': '🧘‍♀️ Осанка',
    'button_workout_2': '🤸‍♀️ Тренировка от целлюлита',
}

WORKOUT_VIDEOS = {
    'button_workout_1': {
        'telegram': 'BAACAgIAAxkBAANuZvF-GFq8iq-DWsOm4cf1zseJZ4AAAhNcAAL19ZBLZtDGuSFuXBw2BA',  # Путь к видео на Telegram (файл на сервере или ID файла)
        'youtube': 'https://www.youtube.com/watch?v=PbWnEIp5TME',
        'vk': 'https://vk.com/video-127960182_456239022'
    },
    'button_workout_2': {
        'telegram': 'BAACAgIAAxkBAAN5ZvGJvR0iq2XH4uCdrIex3GrhdU0AAjNdAAL19ZBL27_7QL6GIHk2BA',  # Путь к видео на Telegram
        'youtube': 'https://www.youtube.com/watch?v=qiS3PIPsRhs',
        'vk': 'https://vk.com/video-127960182_456239022'
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user_id = update.message.from_user.id
    # username = update.message.from_user.username
    # user = User(user_id, username)
    # repo.add_user(user)
    #repo.save_all_users_to_google_sheets()
    #repo.delete_user(493470036)
    keyboard = [[InlineKeyboardButton("Получить бесплатную тренировку", callback_data='button_get_training')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Привет! Нажмите на кнопку ниже, чтобы получить бесплатную тренировку.',
                                    reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'button_get_training':
        keyboard = [[InlineKeyboardButton("Готово ✅", callback_data='button_check_subscription')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=query.message.chat_id,
                               text=f"Пожалуйста, подпишитесь на канал: \n[Александра Чупракова | осанка | пилатес]({INVITE_LINK}) \n\nЗатем нажмите на кнопку под этим сообщением",
                               reply_markup=reply_markup, parse_mode= "Markdown")
    elif query.data == 'button_check_subscription':
        await check_subscription(update, context)
    elif query.data.startswith('button_workout_'):
        await update_workout_selection(update, context, query.data)

async def check_subscription_status(user_id):
    """Функция для проверки статуса подписки пользователя"""
    url = f'https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={CHANNEL_ID}&user_id={user_id}'
    response = requests.get(url)
    data = response.json()

    if data['ok']:
        status = data['result']['status']
        if status in ['member', 'administrator', 'creator']:
            return True
    return False

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    is_subscribed = await check_subscription_status(user_id)

    if is_subscribed:
        await query.message.reply_text("Спасибо за подписку! Теперь выберите тренировку:")
        # Отправка кнопок с выбором тренировки
        keyboard = [
            [InlineKeyboardButton(f"{WORKOUT_NAMES['button_workout_1']}", callback_data='button_workout_1')],
            [InlineKeyboardButton(f"{WORKOUT_NAMES['button_workout_2']}", callback_data='button_workout_2')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=query.message.chat_id, text="Выберите тренировку:", reply_markup=reply_markup)
    else:
        await query.message.reply_text("Вы еще не подписались на канал. Пожалуйста, подпишитесь и попробуйте снова.")


async def send_workout_options(update: Update, context: ContextTypes.DEFAULT_TYPE, workout_key):
    query = update.callback_query
    workout_name = WORKOUT_NAMES.get(workout_key, "Неизвестная тренировка")

    # Клавиатура для выбора сервиса
    keyboard = [
        [InlineKeyboardButton("Получить видео в Telegram", callback_data=f'telegram_{workout_key}')],
        [InlineKeyboardButton("Получить ссылку на YouTube", callback_data=f'youtube_{workout_key}')],
        [InlineKeyboardButton("Получить ссылку на ВК", callback_data=f'vk_{workout_key}')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправка сообщения с клавиатурой выбора сервиса
    await context.bot.send_message(chat_id=query.message.chat_id,
                                   text=f"Выберите сервис для тренировки: {workout_name}", reply_markup=reply_markup)

async def update_workout_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, workout_key):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    remaining_workout = WORKOUT_NAMES[workout_key]

    user = User(user_id=user_id, username=username, workout_choice=remaining_workout)
    repo.add_user(user)  # Добавляем пользователя после выбора тренировки

    # Удаляем невыбранную тренировку из клавиатуры

    new_keyboard = [[InlineKeyboardButton(f"{remaining_workout}", callback_data=workout_key)]]
    reply_markup = InlineKeyboardMarkup(new_keyboard)

    # Редактируем сообщение с выбором тренировок, оставляя только выбранную тренировку
    await context.bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    # После выбора тренировки отправляем сообщение с предложением выбора платформы
    await send_workout_options(update, context, workout_key)


async def handle_service_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    service = data[0]
    workout_key = '_'.join(data[1:])

    workout_data = WORKOUT_VIDEOS.get(workout_key)

    if workout_data:
        if service == 'telegram':
            telegram_video = workout_data.get('telegram')
            if telegram_video:
                await context.bot.send_video(chat_id=query.message.chat_id, video=telegram_video, caption="Вот ваша тренировка!")
        elif service == 'youtube':
            youtube_link = workout_data.get('youtube')
            if youtube_link:
                await context.bot.send_message(chat_id=query.message.chat_id, text=f"Ссылка на YouTube: {youtube_link}")
        elif service == 'vk':
            vk_link = workout_data.get('vk')
            if vk_link:
                await context.bot.send_message(chat_id=query.message.chat_id, text=f"Ссылка на ВК: {vk_link}")
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="Произошла ошибка при выборе тренировки.")


# async def send_workout_link(update: Update, context: ContextTypes.DEFAULT_TYPE, workout_key):
#     query = update.callback_query
#     user_id = query.from_user.id
#     workout_link = WORKOUT_VIDEOS.get(workout_key)
#     if workout_link:
#         workout_name = WORKOUT_NAMES.get(workout_key, "Неизвестная тренировка")  # Получаем название тренировки из словаря
#
#
#         await context.bot.send_message(chat_id=query.message.chat_id, text=f"Вот ссылка на выбранную тренировку: {workout_link}")
#
#         # Редактируем сообщение, заменяя клавиатуру с одной кнопкой выбранной тренировки
#         if query.message.chat_id in context.user_data and context.user_data[query.message.chat_id]['edited'] is False:
#             try:
#                 keyboard = InlineKeyboardMarkup(
#                     [[InlineKeyboardButton(workout_name, callback_data=f'button_workout_{workout_key.split("_")[1]}')]])
#                 await context.bot.edit_message_reply_markup(chat_id=query.message.chat_id,
#                                                             message_id=context.user_data[query.message.chat_id][
#                                                                 'message_id'],
#                                                             reply_markup=keyboard)
#
#                 # Помечаем сообщение как отредактированное
#                 context.user_data[query.message.chat_id]['edited'] = True
#             except Exception as e:
#                 print(f"Error editing message: {e}")
#     else:
#         await context.bot.send_message(chat_id=query.message.chat_id, text="Ссылка на тренировку уже получена")

async def periodic_task(context: ContextTypes.DEFAULT_TYPE):
    await send_regular_posts(context)

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern='^button_'))

    application.add_handler(CommandHandler("admin_send", admin_send_message))
    application.add_handler(MessageHandler(filters.PHOTO & filters.User(int(ADMIN_ID)), admin_send_photo))
    application.add_handler(MessageHandler(filters.VIDEO & filters.User(int(ADMIN_ID)), admin_send_video))
    application.add_handler(CallbackQueryHandler(handle_service_selection, pattern='^(telegram|youtube|vk)_'))

    application.add_handler(CommandHandler("admin_send_regular", admin_send_regular))
    application.add_handler(CommandHandler("admin_delete_post", admin_delete_post))
    application.add_handler(CommandHandler("admin_delete_all_posts", admin_delete_all_posts))
    application.add_handler(CommandHandler("admin_get_regular", admin_get_regular))  # Добавляем обработчик команды
    application.add_handler(CallbackQueryHandler(handle_confirmation))

    application.job_queue.run_repeating(periodic_task, interval=3600, first=0)

    application.run_polling()


if __name__ == '__main__':
    main()