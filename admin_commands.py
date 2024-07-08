import json
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from user_repository import UserRepository
with open('config.json', 'r') as file:
    config = json.load(file)
from datetime import datetime
from regular_repository import RegularPostRepository
ADMIN_ID = config['ADMIN_ID']
from telegram.constants import ParseMode
UserRepo = UserRepository()
RegularPostRepo = RegularPostRepository()

async def admin_send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    print(f"ADMIN_ID: {ADMIN_ID}, user_id: {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фотографию.")
        return

    photo_id = update.message.photo[-1].file_id
    context.user_data['photo_id'] = photo_id  # Сохраняем photo_id в user_data
    await update.message.reply_text("Теперь отправьте команду /admin_send с текстом сообщения или команду /admin_send_regular с текстом сообщения и временным интервалом")

async def send_regular_posts(context: ContextTypes.DEFAULT_TYPE):
    users = UserRepo.get_all_users()  # Предполагаем, что у вас есть функция для получения всех пользователей
    now = datetime.now()

    for user in users:
        user_id = user.user_id
        start_date = datetime.fromtimestamp(user.start_date)
        hours_since_join = round((now - start_date).total_seconds() // 3600)

        print(hours_since_join)
        series_post = RegularPostRepo.get_post_for_hours(hours_since_join)

        if series_post:
            message = series_post['message']
            photo_id = series_post['photo_id']

            try:
                if photo_id:
                    await context.bot.send_photo(chat_id=user_id, photo=photo_id, caption=message)
                else:
                    await context.bot.send_message(chat_id=user_id, text=message)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

async def admin_send_regular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    print(f"ADMIN_ID: {ADMIN_ID}, user_id: {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Пожалуйста, укажите сообщение для рассылки и через сколько часов его отправлять.")
        return

    try:
        hours = int(context.args[-1])
        message = ' '.join(context.args[:-1])
    except ValueError:
        await update.message.reply_text("Пожалуйста, укажите корректное количество часов.")
        return

    context.user_data['regular_message'] = message
    context.user_data['regular_hours'] = hours

    if 'photo_id' in context.user_data:
        photo_id = context.user_data['photo_id']
        RegularPostRepo.insert_post(hours, message, photo_id)
    else:
        RegularPostRepo.insert_post(hours, message)
    await update.message.reply_text(f"Регулярное сообщение установлено на {hours} часов:")

    if 'photo_id' in context.user_data:
        await update.message.reply_photo(photo=photo_id, caption=message)
    else:
        await context.bot.send_message(chat_id=user_id, text=message)

async def admin_delete_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    print(f"ADMIN_ID: {ADMIN_ID}, user_id: {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Пожалуйста, укажите ID поста для удаления.")
        return

    try:
        post_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Пожалуйста, укажите корректный ID сообщения.")
        return

    RegularPostRepo.delete_post(post_id)
    await update.message.reply_text(f"Сообщение с ID {post_id} успешно удалено.")

async def admin_get_regular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    print(f"ADMIN_ID: {ADMIN_ID}, user_id: {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    posts = RegularPostRepo.get_all_posts()
    if not posts:
        await update.message.reply_text("Регулярные сообщения отсутствуют.")
        return

    response = "Список регулярных постов:\n\n"
    for post in posts:
        post_id, message = post
        response += f"ID: {post_id}, Текст: {message[:50]}...\n"  # Выводим первые 50 символов сообщения

    await update.message.reply_text(response)


async def admin_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    print(f"ADMIN_ID: {ADMIN_ID}, user_id: {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Пожалуйста, укажите сообщение для рассылки.")
        return

    message = ' '.join(context.args)
    context.user_data['message'] = message
    if 'photo_id' in context.user_data:
        photo_id = context.user_data['photo_id']
    # Определение временных интервалов для выбора пользователей
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Менее 1 недели", callback_data='send_7'),
                InlineKeyboardButton("Менее 3 недель", callback_data='send_21'),
                InlineKeyboardButton("Менее 4 недель", callback_data='send_28'),
                InlineKeyboardButton("Более 4 недель", callback_data='send_29')
            ],
            [InlineKeyboardButton("Всем", callback_data='send_1')],
            [InlineKeyboardButton("❌ Отменить", callback_data='delete')]
        ])
        await update.message.reply_photo(photo=photo_id, caption=message, parse_mode=ParseMode.HTML)
        await update.message.reply_text("Выберите период, для которого будет осуществлена рассылка:",  reply_markup = reply_markup)
    else:
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Менее 1 недели", callback_data='send_7'),
                InlineKeyboardButton("Менее 3 недель", callback_data='send_21'),
                InlineKeyboardButton("Менее 4 недель", callback_data='send_28'),
                InlineKeyboardButton("Более 4 недель", callback_data='send_29')
            ],
            [InlineKeyboardButton("Всем", callback_data='send_1')],
            [InlineKeyboardButton("❌ Отменить", callback_data='delete')]
        ])
        await update.message.reply_text(text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)




async def handle_confirmation(update: Update,context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith('send_'):
        days_ago = int(query.data.split('_')[1])
        message = context.user_data['message']
        users = []

        if days_ago == 7:
            users = UserRepo.get_recent_users()
            print(users)
        elif days_ago == 21:
            users = UserRepo.get_users_2_weeks_ago()
        elif days_ago == 28:
            users = UserRepo.get_users_3_weeks_ago()
        elif days_ago == 29:
            users = UserRepo.get_users_4_weeks_ago()
        elif days_ago == 1:
            users = UserRepo.get_all_users2()

        if 'photo_id' in context.user_data:
            photo_id = context.user_data['photo_id']
            for user in users:
                user_id = user
                try:
                    await context.bot.send_photo(chat_id=user_id, photo=photo_id, caption=message)
                except Exception as e:
                    print(f"Не удалось отправить фото пользователю {user_id}: {e}")
        else:
            for user in users:
                user_id = user
                try:
                    await context.bot.send_message(chat_id=user_id, text=message)
                except Exception as e:
                    print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        await context.bot.send_message(chat_id=query.message.chat_id, text="Сообщение успешно отправлено.")

    elif query.data == 'delete':
        await context.bot.send_message(chat_id=query.message.chat_id, text="Отправка отменена, фото удалено.")
        context.user_data.clear()