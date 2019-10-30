import logging
from google_api import get_api
from telegram.ext import run_async, Updater, CommandHandler, MessageHandler, \
    Filters
from telegram import ParseMode
from get_stat import get_alumni_stat
from config import TOKEN, PORT, HEROKU_APP_NAME, MODE, GOOGLE_FORM_URL, image_path
from face_rec import face_rec
from config import PHOTO_PATH


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def handlers(updater):
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo |
                                                  Filters.text, echo))


if MODE == "prod":
    def run():
        updater = Updater(TOKEN, use_context=True)
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        handlers(updater)
        updater.bot.set_webhook(
            "https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))

elif MODE == "dev":
    def run():
        import requests
        get_request = requests.get('http://pubproxy.com/api/proxy?limit=1&'
                                   'format=txt&port=8080&level=anonymous&'
                                   'type=socks5&country=FI|NO|US&https=True')

        logger.info(f"Using proxy: {get_request.text}")
        # Current working proxy: 157.245.56.246:8080
        # updater = Updater(TOKEN, use_context=True, request_kwargs={
        #                   'proxy_url': f'https://{get_request.text}'})
        updater = Updater(TOKEN, use_context=True, request_kwargs={
            'proxy_url': f'https://157.245.56.246:8080'})
        handlers(updater)
        updater.start_polling()

else:
    logger.error('No MODE specified')
    exit(1)


all_users = {}


@run_async
def start(update, context):
    logger.info(
        f"Starting char with {update.effective_user.name} at {update.effective_message.date}")
    chat_id = update.effective_chat.id
    username = update.effective_user.name[1:]  # Without @
    if chat_id not in all_users:
        all_users[chat_id] = username

    start_text = (f'Привет, {update.effective_user.first_name}! '
                  'Данный бот поможет Вам понять, готовы ли Вы обучаться '
                  'на магистерской программе *Software Engineering* в ИТМО. '
                  f'Пройдите, пожалуйста, тест в '
                  f'[Google Form]({GOOGLE_FORM_URL}?entry.182475645={username}).')

    context.bot.send_message(parse_mode=ParseMode.MARKDOWN,
                             chat_id=chat_id,
                             text=start_text)

    try:
        pic_name, pashalki, comments = get_api(
            username, update.effective_message.date)
    except TimeoutError as te:
        context.bot.send_message(chat_id=chat_id, text=str(te))
        logger.info(
            f"User {update.effective_user.name} at {update.effective_message.date} doesn't finish test")
        return
    except InterruptedError as be:
        context.bot.send_message(chat_id=chat_id, text=str(be))
        logger.info(
            f"User {update.effective_user.name} at {update.effective_message.date} got now time")
        return

    pre_pashalki = ('*Почитайте наши рекомендации, основанные на Ваших ответах '
                    'на общие вопросы:*')

    comments_text = '\n'.join(comments)

    context.bot.send_photo(chat_id=chat_id, photo=open(pic_name, "rb"))
    context.bot.send_message(parse_mode=ParseMode.MARKDOWN,
                             chat_id=chat_id, text=pre_pashalki)
    for recommendation in pashalki:
        context.bot.send_message(parse_mode=ParseMode.MARKDOWN,
                                 chat_id=chat_id, text=recommendation)
    context.bot.send_message(parse_mode=ParseMode.MARKDOWN,
                             chat_id=chat_id, text=comments_text)

    logger.info(
        f"Start ready for {update.effective_user.name} at {update.effective_message.date}")


def echo(update, context):
    logger.info(
        f"Waiting for echo function for {update.effective_user.name} at {update.effective_message.date}")
    chat_id = update.effective_chat.id

    if len(update.message.photo) == 0:
        context.bot.send_sticker(
            chat_id=chat_id, sticker='http://b.webpurr.com/anY5.webp')
        response = ('Напишите боту /start или загрузите свою фотографию, '
                    'чтобы посмотреть на кого из наших выпускников Вы похожи больше всего.')
    else:
        context.bot.send_sticker(
            chat_id=chat_id, sticker='http://b.webpurr.com/dyDz.webp')

        file_id = update.message.photo[-1].file_id
        file_info = context.bot.get_file(file_id)
        input_photo_name = 'face_rec_' + \
            image_path(update.effective_message.date,
                       update.effective_user.name[1:])
        file_info.download(input_photo_name)

        logger.info(
            f"Waiting face recognition for {update.effective_user.name} at {update.effective_message.date}")
        pic_name, alumni_id = face_rec(input_photo_name)
        response = get_alumni_stat(alumni_id)
        context.bot.send_photo(chat_id=chat_id, photo=open(
            ''.join(PHOTO_PATH) + pic_name, "rb"))

    context.bot.send_message(parse_mode=ParseMode.MARKDOWN,
                             chat_id=chat_id, text=response)
    logger.info(
        f"Echo ready for {update.effective_user.name} at {update.effective_message.date}")


if __name__ == '__main__':
    logger.info("Starting bot")
    run()
