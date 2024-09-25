import json
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.helpers import escape_markdown
from telegram.ext import ContextTypes
from user_repository import UserRepository
from google_sheets import GoogleSheets

with open('config.json', 'r') as file:
    config = json.load(file)
from datetime import datetime
from regular_repository import RegularPostRepository
ADMIN_ID = config['ADMIN_ID']
from telegram.constants import ParseMode

google_sheets = GoogleSheets('credentials.json', 'BeautifulBodyBotData')
UserRepo = UserRepository(google_sheets)
RegularPostRepo = RegularPostRepository()

async def admin_send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фотографию.")
        return

    photo_id = update.message.photo[-1].file_id
    context.user_data['photo_id'] = photo_id  # Сохраняем photo_id в user_data
    await update.message.reply_text("Теперь отправьте команду /admin_send с текстом сообщения или команду /admin_send_regular с текстом сообщения и временным интервалом")

async def admin_send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if not update.message.video:
        await update.message.reply_text("Пожалуйста, отправьте видео.")
        return

    video_id = update.message.video.file_id
    context.user_data['video_id'] = video_id  # Сохраняем video_id в user_data
    await update.message.reply_text(f"Теперь отправьте команду /admin_send с текстом сообщения или команду /admin_send_regular с текстом сообщения и временным интервалом. \nfile_id: {video_id}")

async def send_regular_posts(context: ContextTypes.DEFAULT_TYPE):
    users = UserRepo.get_all_users()
    now = datetime.now()

    for user in users:
        user_id = user.user_id
        workout_choice = user.workout_choice  # Получаем выбор тренировки из БД

        # Если у пользователя не указана тренировка, пропускаем его
        if not workout_choice:
            continue

        start_date = datetime.fromtimestamp(user.start_date)
        hours_since_join = round((now - start_date).total_seconds() // 3600)
       # hours_since_join = 1  # Для теста. Убрать это в реальной логике[]'4re5748

        # Получаем все посты для указанного промежутка времени
        series_posts = RegularPostRepo.get_post_for_hours(hours_since_join)

        if not series_posts:
            continue  # Если постов для указанного времени нет, продолжаем со следующим пользователем

        for series_post in series_posts:
            post_workout_choice = series_post.get('workout_choice')

            # Если пост предназначен для всех, отправляем его всем
            if post_workout_choice != "Всем" and post_workout_choice != workout_choice:
                continue  # Пропускаем пост, если он не для выбранной тренировки и не для всех

            message = series_post['message']
            photo_id = series_post.get('photo_id')
            video_id = series_post.get('video_id')

            try:
                # Отправляем сообщение в зависимости от наличия фото или видео
                if photo_id:
                    await context.bot.send_photo(chat_id=user_id, photo=photo_id, caption=message, parse_mode=ParseMode.HTML)
                elif video_id:
                    await context.bot.send_video(chat_id=user_id, video=video_id, caption=message, parse_mode=ParseMode.HTML)
                else:
                    await context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                UserRepo.update_user_status_to_false(user_id)

# async def send_regular_posts(context: ContextTypes.DEFAULT_TYPE, workout_choice=0):
#     users = UserRepo.get_all_users()
#     now = datetime.now()
#
#     for user in users:
#         if workout_choice == 1 and user.workout_choice != '🧘‍♀️ Осанка':
#             continue
#         if workout_choice == 2 and user.workout_choice != '🤸‍♀️ Тренировка от целлюлита':
#             continue
#
#         user_id = user.user_id
#         start_date = datetime.fromtimestamp(user.start_date)
#         hours_since_join = round((now - start_date).total_seconds() // 3600)
#         hours_since_join = 1
#         print(f'User {user_id} joined {hours_since_join} hours ago.')
#         series_posts = RegularPostRepo.get_post_for_hours(hours_since_join)
#
#         if series_posts:
#             for series_post in series_posts:
#
#                 post_workout_choice = series_post.get('workout_choice')  # Добавим поле workout_choice в посты
#                 if post_workout_choice and post_workout_choice != user.workout_choice:
#                     continue  # Пропускаем пост, если он не для выбранной тренировки
#
#                 message = series_post['message']
#                 photo_id = series_post.get('photo_id')
#                 video_id = series_post.get('video_id')
#
#                 try:
#                     if photo_id:
#                         await context.bot.send_photo(chat_id=user_id, photo=photo_id, caption=message,
#                                                      parse_mode=ParseMode.HTML)
#                     elif video_id:
#                         await context.bot.send_video(chat_id=user_id, video=video_id, caption=message,
#                                                      parse_mode=ParseMode.HTML)
#                     else:
#                         await context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
#                 except Exception as e:
#                     print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
#                     UserRepo.update_user_status_to_false(user_id)

async def admin_send_regular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Пожалуйста, укажите сообщение, через сколько часов его отправлять и целевую аудиторию (0 - всем, 1 - осанка, 2 - целлюлит).")
        return

    try:
        hours = int(context.args[-2])
        workout_choice = int(context.args[-1])
        message = ' '.join(context.args[:-2])
    except ValueError:
        await update.message.reply_text("Пожалуйста, укажите корректное количество часов и выбор аудитории (0 - всем, 1 - осанка, 2 - целлюлит).")
        return

        # Преобразуем числовой workout_choice в текстовый
    workout_choice_text = ''
    if workout_choice == 0:
        workout_choice_text = 'Всем'
    elif workout_choice == 1:
        workout_choice_text = '🧘‍♀️ Осанка'
    elif workout_choice == 2:
        workout_choice_text = '🤸‍♀️ Тренировка от целлюлита'
    else:
        await update.message.reply_text(
            "Некорректный выбор аудитории. Допустимые значения: 0 - всем, 1 - осанка, 2 - целлюлит.")
        return

    context.user_data['regular_message'] = message
    context.user_data['regular_hours'] = hours
    context.user_data['workout_choice'] = workout_choice_text

    # Проверяем наличие фото или видео
    if 'photo_id' in context.user_data:
        media_id = context.user_data['photo_id']
        RegularPostRepo.insert_post(hours, message, photo_id=media_id, workout_choice=workout_choice_text)
    elif 'video_id' in context.user_data:
        media_id = context.user_data['video_id']
        RegularPostRepo.insert_post(hours, message, video_id=media_id, workout_choice=workout_choice_text)
    else:
        RegularPostRepo.insert_post(hours, message, workout_choice=workout_choice_text)

    await update.message.reply_text(
        f"Регулярное сообщение установлено на {hours} часов для целевой аудитории {workout_choice}.")

async def admin_delete_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
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

async def admin_delete_all_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return
    RegularPostRepo.delete_all_posts()
    await update.message.reply_text(f"Все посты удалены")

async def admin_get_regular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    posts = RegularPostRepo.get_all_posts()
    if not posts:
        await update.message.reply_text("Регулярные сообщения отсутствуют.")
        return

    response = "Список регулярных постов:\n\n"
    for post in posts:
        post_id, message, workout_choice = post
        response += f"ID: {post_id}, Тренировка: {workout_choice}, Текст: {message[:50]}...\n"  # Выводим первые 50 символов сообщения

    await update.message.reply_text(response)

async def admin_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Пожалуйста, укажите сообщение для рассылки.")
        return

    message = update.message.text[len('/admin_send '):]
    context.user_data['message'] = message

    # Check if a photo or video is present
    if 'photo_id' in context.user_data:
        media_id = context.user_data['photo_id']
        media_type = 'photo'
    elif 'video_id' in context.user_data:
        media_id = context.user_data['video_id']
        media_type = 'video'
    else:
        media_id = None
        media_type = None

    # Create the reply markup with buttons
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

    # Send the media or the message based on availability
    if media_type == 'photo':
        await update.message.reply_photo(photo=media_id, caption=message, parse_mode=ParseMode.HTML)
    elif media_type == 'video':
        await update.message.reply_video(video=media_id, caption=message, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    # Ask the admin to select the user group for broadcasting
    await update.message.reply_text("Выберите период, для которого будет осуществлена рассылка:", reply_markup=reply_markup)


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith('send_'):
        days_ago = int(query.data.split('_')[1])
        message = context.user_data['message']
        users = []

        # Fetch the appropriate user list based on days_ago
        if days_ago == 7:
            users = UserRepo.get_less_then_users(7)
        elif days_ago == 21:
            users = UserRepo.get_less_then_users(21)
        elif days_ago == 28:
            users = UserRepo.get_less_then_users(28)
        elif days_ago == 29:
            users = UserRepo.get_more_then_users(28)
        elif days_ago == 1:
            users = UserRepo.get_all_users2()

        # Send either a photo, video, or text message to the users
        if 'photo_id' in context.user_data:
            photo_id = context.user_data['photo_id']
            for user in users:
                user_id = user
                try:
                    await context.bot.send_photo(chat_id=user_id, photo=photo_id, caption=message, parse_mode=ParseMode.HTML)
                except Exception as e:
                    print(f"Не удалось отправить фото пользователю {user_id}: {e}")
                    UserRepo.update_user_status_to_false(user_id)
        elif 'video_id' in context.user_data:
            video_id = context.user_data['video_id']
            for user in users:
                user_id = user
                try:
                    await context.bot.send_video(chat_id=user_id, video=video_id, caption=message, parse_mode=ParseMode.HTML)
                except Exception as e:
                    print(f"Не удалось отправить видео пользователю {user_id}: {e}")
                    UserRepo.update_user_status_to_false(user_id)
        else:
            for user in users:
                user_id = user
                try:
                    await context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
                except Exception as e:
                    print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                    UserRepo.update_user_status_to_false(user_id)

        # Notify the admin that the message was successfully sent
        await context.bot.send_message(chat_id=query.message.chat_id, text="Сообщение успешно отправлено.")

    elif query.data == 'delete':
        # Clear user data and notify that sending was canceled
        await context.bot.send_message(chat_id=query.message.chat_id, text="Отправка отменена, фото или видео удалено.")
        context.user_data.clear()