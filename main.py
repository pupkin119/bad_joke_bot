# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_bots")

import environ

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env('.env')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Your application specific imports
from bad_joke.models import ChatUser, JokeText
from django.db.models import Max
from telegram.ext import Updater

import logging
import numpy as np

import random



from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot

bot = Bot(token=env('bot_token'))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def check_error(update, text):
    update.message.reply_text("Что то пошло не так, потому что")
    update.message.reply_text(text)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет я бот для игры в плохие шутки')
    update.message.reply_text('Все доступные команды ты можешь посмотреть по /help')

def set_stupid_joke(update, context):
    user = update.message.from_user

    text_ans = ""
    for i in np.arange(len(context.args)):
        text_ans += context.args[i] + " "

    if len(text_ans) == 0:
        text_ans = "мдэ"

    chat_user = ChatUser.objects.get(chat_id = user["id"])
    if chat_user.is_winner:
        tj = JokeText()
        tj.joke_text = text_ans
        tj.save()

        chat_user.is_winner = False
        chat_user.save()

        update.message.reply_text('Такая себе шутка, ну да ладно')
    else:
        update.message.reply_text('Ты не победитель!')


from numpy.random import randint
def bad_joke_start(update, context):

    users_count = ChatUser.objects.count()

    if users_count < 4:
        check_error(update, "Недостаточно зарегистрированных пользователей")
        return

    items = ChatUser.objects.filter(is_in_game = True)
    if items.exists():
        update.message.reply_text('Игра еще не закончилась, а ты получаешь в очко!')
        return
        # user = update.message.from_user
        # bad_user = ChatUser.objects.filter(chat_id = user["id"])
        # for u in bad_user:
        #     u.


    # items = ChatUser.objects.all()

    pks = ChatUser.objects.values_list('pk', flat=True)
    # pks = np.asarray(pks)
    # random_idx = randint(3, len(pks))
    random_idx = random.sample(list(pks), 3)
    print(random_idx)
    random_items = ChatUser.objects.filter(pk__in=random_idx)


    # change 3 to how many random items you want
    # random_items = random.sample(items, 3)
    # text_joke = "Заходит как то Еврей, и собака, а бармен им и говорит!"
    text_joke = JokeText.objects.last().joke_text
    update.message.reply_text('Игра началась!')
    i = 0
    for u in random_items:
        i += 1
        u.is_in_game = True
        u.is_answer = True
        u.number_of_vote = i
        u.save()
        bot.send_message(chat_id=u.chat_id, text="Привет, " + u.first_name + "!")
        bot.send_message(chat_id=u.chat_id, text='Дополни как вот такую шутку:')
        bot.send_message(chat_id=u.chat_id, text=str(text_joke))
        bot.send_message(chat_id=u.chat_id, text="Ты можешь ответить через /answer команду")

    update.message.reply_text('Вопросики отосланы!')



    # bot.send_message(chat_id='397622734', text='Привет Владимир!')
    # bot.send_message(chat_id='397622734', text='Дополни как вот такую хуебень:')
    # bot.send_message(chat_id='397622734', text='На столе стоит корова мылом умывается...')
    #
    # bot.send_message(chat_id='423801182', text='Привет Александр!')
    # bot.send_message(chat_id='423801182', text='Дополни как вот такую хуебень:')
    # bot.send_message(chat_id='423801182', text='На столе стоит корова мылом умывается...')

def help(update, context):
    """Send a message when the command /help is issued."""
    text = "Игра такая тупая, но тебе понравится! \n"
    text += "Список команд \n"
    text += "/register : для регистрации \n"
    text += "/answer [тут ответ]:  для ответа на заданные вопросы \n"
    text += "/help : для справки \n"
    text += "/get_score : Узнать статус набранных очков \n"
    text += "/get_vote_game : Узнать статус глосования \n"
    text += "/end_joke_game : Закончить игру[ может только админ ] \n"
    text += "/set_stupid_joke : Установить текст шутки [ Может делать только победитель ] \n"
    text += "/bad_joke_start : НАЧАТЬ ИГРУ  \n"
    # update.message.chat["id"]
    bot.send_message(chat_id=update.message.chat["id"], text=text)
    # update.message.reply_text('Игра такая тупая, но тебе понравится!')
    # update.message.reply_text('Список команд')
    # update.message.reply_text('/register : для регистрации')
    # update.message.reply_text('/answer [тут ответ]:  для ответа на заданные вопросы')
    # update.message.reply_text('/help : для справки')
    # update.message.reply_text('/get_score : Узнать статус набранных очков')
    # update.message.reply_text('/get_vote_game : Узнать статус глосования')
    # update.message.reply_text('/end_joke_game : Закончить игру[ может только админ ]')
    # update.message.reply_text('/set_stupid_joke : Установить текст шутки [ Может делать только победитель ]')




def register(update, context):
    user = update.message.from_user

    new_user = ChatUser.objects.filter(chat_id = user["id"])
    if not(new_user.exists()):
        u = ChatUser()
        u.first_name = user["first_name"]
        u.last_name = user["last_name"]
        u.chat_id = user["id"]
        u.save()

        update.message.reply_text("Успешно зарегистрировано")
    else:
        update.message.reply_text("Что то пошло не так, потому что")
        update.message.reply_text("Юзер уже есть")

def get_score(update, context):
    all_users = ChatUser.objects.all().order_by('-game_score')
    update.message.reply_text(" Статистика по победам ")
    answer = ""
    for user in all_users:
        answer += str(user.first_name) + " " + str(user.last_name)+ ": " + str(user.game_score) + "\n"

    bot.send_message(chat_id=update.message.chat["id"], text=answer)

def is_end_game(chat_id):
    all_users = ChatUser.objects.filter(is_vote=False)

    if all_users.exists():
        return False
    else:
        return True

def is_admin(chat_id):
    u = ChatUser.objects.get(chat_id=chat_id)
    if u.is_admin:
        return True
    else:
        False

def get_vote_game(update, context):
    all_users = ChatUser.objects.filter(is_in_game = True).order_by('number_of_vote')

    text_joke = str(JokeText.objects.last().joke_text)

    bot.send_message(chat_id=update.message.chat["id"], text='Вопрос был такой')
    bot.send_message(chat_id=update.message.chat["id"], text=text_joke)
    bot.send_message(chat_id=update.message.chat["id"], text='Номер для голосования: Ответ [ Сколько проголосовало за ответ ] ')
    # update.message.reply_text("Вопрос был такой")
    # update.message.reply_text("Заходит как то Еврей, и собака, а бармен им и говорит!")
    # update.message.reply_text("Номер для голосования: Ответ [ Сколько проголосовало за ответ ] ")
    for user in all_users:
        ans = ""
        if user.answer:
            ans = user.answer
        else:
            ans = " Пользователь не ответил"
        # update.message.reply_text(str(user.number_of_vote) + " : "  + str(ans) +  "[ "+ str(user.score) + " ]" )
        bot.send_message(chat_id=update.message.chat["id"], text=str(user.number_of_vote) + " : "  + str(ans) +  "[ "+ str(user.score) + " ]")

def end_joke_game(update, context):
    user = update.message.from_user
    if is_admin(user["id"]):
        end_game(update.message.chat["id"])
    else:
        update.message.reply_text("Ты не админ, и не можешь вызвать эту команду")

def end_game(chat_id):
    max_score = ChatUser.objects.all().aggregate(Max('score'))['score__max']

    winner = ChatUser.objects.filter(score = max_score)
    w = winner[0]
    w.is_winner = True
    w.game_score = w.game_score + 1
    w.save()

    bot.send_message(chat_id=chat_id, text= "Победил: " +  str(w.first_name + " " + w.last_name + " !" ))

    for u in ChatUser.objects.all():
        u.is_in_game = False
        u.score = 0
        u.number_of_vote = 0
        u.is_vote = False
        u.is_answer = False
        u.answer = ""
        u.save()

def vote(update, context):
    user = update.message.from_user
    vote_num = context.args[0]

    vote_user = ChatUser.objects.get(chat_id = user["id"])
    if vote_user.is_vote:
        update.message.reply_text("Ты уже проголосовал")
        return
    try:
        chat_user = ChatUser.objects.get(number_of_vote = vote_num)
    except ChatUser.DoesNotExist:
        update.message.reply_text("Что то пошло не так, потому что")
        update.message.reply_text("Юзер не найден с таким номером")
        return
    else:
        chat_user.score = chat_user.score + 1
        chat_user.save()

        vote_user.is_vote = True
        vote_user.save()
        update.message.reply_text("Твой голос учтен")
        if is_end_game(update.message.chat["id"]):
            end_game(update.message.chat["id"])

def answer(update, context):
    user = update.message.from_user
    text_ans = ""
    for i in np.arange(len(context.args)):
        text_ans += context.args[i] + " "

    if len(text_ans) == 0:
        text_ans = "мдэ"

    try:
        chat_user = ChatUser.objects.get(chat_id = user["id"])
    except ChatUser.DoesNotExist:
        update.message.reply_text("Что то пошло не так, потому что")
        update.message.reply_text("Ты еще не зарегестрировался")
    else:
        if chat_user.is_in_game:
            if not(chat_user.is_answer):
                update.message.reply_text("Ты уже ответил")
            else:
                chat_user.answer = text_ans
                chat_user.is_answer = False
                chat_user.save()
                update.message.reply_text("Ответ успешно записан")
        else:
            update.message.reply_text("Ты не в игре")

def options(update, context):
    user = update.message.from_user
    # print(update.message.chat.id)
    # print(update)
    # print(user)
    # bot.send_message(chat_id='-1001436950929', text='hello there')
    # bot.send_message(chat_id='-390768652', text='hello there')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=env('bot_token'), use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("options", options))
    dp.add_handler(CommandHandler("register", register))
    dp.add_handler(CommandHandler("bad_joke_start", bad_joke_start))
    dp.add_handler(CommandHandler("answer", answer, pass_args=True))
    dp.add_handler(CommandHandler("vote", vote, pass_args=True))
    dp.add_handler(CommandHandler("get_score", get_score))
    dp.add_handler(CommandHandler("get_vote_game", get_vote_game))
    dp.add_handler(CommandHandler("end_joke_game", end_joke_game))
    dp.add_handler(CommandHandler("set_stupid_joke", set_stupid_joke, pass_args=True))

    # dp.add_handler(MessageHandler(Filters.text | Filters.photo, get_input))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()