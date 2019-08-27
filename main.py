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

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

import logging
import numpy as np

import random



from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot

bot = Bot(token=env('bot_token'))

REQUEST_KWARGS = {
    'proxy_url': 'socks5://88.198.55.164:1080',
    # Optional, if you need authentication:
    # 'urllib3_proxy_kwargs': {
    #     'username': 'PROXY_USER',
    #     'password': 'PROXY_PASS',
    # }
}

# updater = Updater(token=env('bot_token'), request_kwargs=REQUEST_KWARGS)
updater = Updater(token=env('bot_token'), use_context=True, request_kwargs=REQUEST_KWARGS)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
def rollback_group_chat(group_chat_id):
    for u in ChatUser.objects.filter(group_chat_id = group_chat_id):
        u.is_in_game = False
        u.score = 0
        u.number_of_vote = 0
        u.is_vote = False
        u.is_answer = False
        u.answer = ""
        u.save()

def check_error(update, text):
    ans_text = "Что то пошло не так, потому что: \n"
    ans_text += text
    # update.message.reply_text("Что то пошло не так, потому что")
    update.message.reply_text(text)

def get_group_id(update):
    return update.message.chat['id']

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет я бот для игры в плохие шутки, добавь меня в чат и мы начнем игру')
    update.message.reply_text('Все доступные команды ты можешь посмотреть по /help')

def rollback(update, context):
    user = update.message.from_user
    group_id = get_group_id(update)

    if is_admin(user['id'], group_id):
        rollback_group_chat(group_id)
        update.message.reply_text('Finish Rollback')

def set_chat(update, context):
    user = update.message.from_user
    # group_id = get_group_id(update)

    if len(context.args) == 0:
        update.message.reply_text("Тебе нужно написать цифру чата например /set_chat 1")
        return

    int_ans = int(context.args[0])
    int_ans = int_ans - 1
    chat_users = ChatUser.objects.filter(chat_id=user["id"]).order_by('-id')


    try:
        ChatUser.objects.filter(chat_id = user['id']).update(current_group_id = chat_users[int_ans].group_chat_id)
        text_ans = "Мы обновили информацию \n "
        text_ans += "Текущий чат теперь: " + chat_users[int_ans].group_chat_title
        update.message.reply_text(text_ans)

    except IndexError:
        update.message.reply_text("Чата с таким номером нет")

    except AssertionError:
        update.message.reply_text("Чата с таким номером нет")


def list_chat(update, context):
    user = update.message.from_user
    # group_id = get_group_id(update)

    chat_users = ChatUser.objects.filter(chat_id=user["id"]).order_by('-id')

    list_text = ""
    i = 0
    for u in chat_users:
        i += 1
        list_text += str(i) + ": "+ str(u.group_chat_title) + ". \n"
    list_text += "Ты можешь выбрать чат в котором будешь отвечать с помошью /set_chat [ номер чата ]"
    update.message.reply_text(update.message.reply_text(list_text))


def set_joke(update, context):
    user = update.message.from_user
    group_id = get_group_id(update)

    text_ans = ""
    for i in np.arange(len(context.args)):
        text_ans += context.args[i] + " "

    if len(text_ans) == 0:
        text_ans = "Ты любишь Егора Крида, скрытный гей, а еще я не умеешь пользоваться командой /set_joke !"
        update.message.reply_text(text_ans)
        return

    chat_user = ChatUser.objects.get(chat_id = user["id"], group_chat_id = group_id)
    if chat_user.is_winner:
        tj = JokeText()
        tj.group_chat_id = group_id
        tj.joke_text = text_ans
        tj.save()

        chat_user.is_winner = False
        chat_user.save()

        update.message.reply_text('Такая себе шутка, ну да ладно')
    else:
        update.message.reply_text('Ты не победитель!')


from numpy.random import randint
def start_joke(update, context):
    group_id = get_group_id(update)
    users_count = ChatUser.objects.filter(group_chat_id = group_id).count()
    try:

        if int(ChatUser.objects.filter(group_chat_id = str(group_id)).count()) < 3:
            print( "количество зареганых пользователей в: " + str(group_id) + str(int(ChatUser.objects.filter(group_chat_id = str(group_id)).count())))
            check_error(update, "Недостаточно зарегистрированных пользователей, нужно минимум 3")
            return

        items = ChatUser.objects.filter(is_in_game = True, group_chat_id = group_id)
        if items.exists():
            update.message.reply_text('Игра еще не закончилась!')
            return

        pks = ChatUser.objects.filter(group_chat_id = group_id).values_list('pk', flat=True)
        # pks = np.asarray(pks)
        # random_idx = randint(3, len(pks))
        random_idx = random.sample(list(pks), 3)
        # print(random_idx)
        random_items = ChatUser.objects.filter(pk__in=random_idx, group_chat_id = group_id)


        # change 3 to how many random items you want
        # random_items = random.sample(items, 3)
        # text_joke = "Заходит как то Еврей, и собака, а бармен им и говорит!"
        text_joke = JokeText.objects.filter(group_chat_id = group_id).last().joke_text
        update.message.reply_text('Игра началась!')
        i = 0
        for u in random_items:
            # i += 1
            # u.is_in_game = True
            # u.is_answer = True
            # u.number_of_vote = i
            # u.save()
            chat_title = str(ChatUser.objects.get(group_chat_id = u.current_group_id, chat_id = u.chat_id).group_chat_title)
            text_to_use = "Привет, " + str(u.first_name) + "! \n"
            text_to_use = "Сейчас ты играешь в чате: , " + chat_title + "! \n"
            text_to_use += "Дополни как вот такую шутку: \n"
            text_to_use += " " + text_joke +  " \n"
            text_to_use += "Ты можешь ответить через /answer команду \n "
            text_to_use += "Чтобы посмотреть или сменить чат используй команды /list_chat  /set_chat \n"
            updater.bot.send_message(chat_id=u.chat_id, text=text_to_use)
        update.message.reply_text('Вопросики отосланы!')

        for u in random_items:
            i += 1
            u.is_in_game = True
            u.is_answer = True
            u.number_of_vote = i
            u.save()

    except TelegramError as e:
        rollback_group_chat(group_id)
        updater.bot.send_message(chat_id=268495107, text=str(e))

        updater.bot.send_message(chat_id=group_id, text="Игра не может начаться, так как кто то из участников не написал боту /start в личке, по соглашению принятому Telegramm, бот не может начать писать первым человку в лс")


def help(update, context):
    """Send a message when the command /help is issued."""
    text = "Игра такая тупая, но тебе понравится! \n"
    text += "Список команд \n"
    text += "/register : для регистрации \n"
    text += "/answer [тут ответ]:  для ответа на заданные вопросы \n"
    text += "/help : для справки \n"
    text += "/score : Узнать статус набранных очков \n"
    text += "/votes : Узнать статус глосования \n"
    text += "/end_game : Закончить игру[ может только админ ] \n"
    text += "/set_joke : Установить текст шутки [ Может делать только победитель ] \n"
    text += "/set_chat : Установить чат в котором будешь играть в тупые шутки  \n"
    text += "/list_chat : Список чатов в котором играешь в тупые шутки \n"
    text += "/start_joke : НАЧАТЬ ИГРУ  \n"
    # text += "@ogoltelyi_tusovshik по вопросам и ошибкам"
    # update.message.chat["id"]
    updater.bot.send_message(chat_id=update.message.chat["id"], text=text)

def register(update, context):
    user = update.message.from_user
    group_id = get_group_id(update)
    # print(group_id)
    if user['id'] == group_id:
        update.message.reply_text("Необходимо закинуть бота в чат и продолжить регистрирацию внутри чата")
        return

    new_user = ChatUser.objects.filter(chat_id = user["id"], group_chat_id = group_id)
    group_chat_users = ChatUser.objects.filter(group_chat_id = group_id)

    is_admin = False
    if group_chat_users.count() == 0:
        is_admin = True
        tj = JokeText()
        tj.group_chat_id = group_id
        tj.joke_text = "Шел медведь по лесу, видит машина горит..."
        tj.save()


    if not(new_user.exists()):
        if is_admin:
            update.message.reply_text("Ты админ")
        u = ChatUser()
        u.first_name = user["first_name"]
        u.last_name = user["last_name"]
        u.chat_id = user["id"]
        u.group_chat_id = group_id
        u.current_group_id = group_id
        u.group_chat_title = update.message.chat['title']
        u.is_admin = is_admin
        u.save()

        text_ans = "Успешно зарегистрировано \n "
        text_ans += "Не забудь написать боту(@BadJokesRanimogoBot) в лс /start чтобы он мог отсылать тебе сообщения"

        update.message.reply_text(text_ans)

        users = ChatUser.objects.filter(chat_id=user["id"])

        if int(users.count()) > 1:
            users.update(current_group_id = group_id)
    else:
        update.message.reply_text("Что то пошло не так, потому что")
        update.message.reply_text("Юзер уже есть")

def score(update, context):
    group_id = get_group_id(update)

    all_users = ChatUser.objects.filter(group_chat_id = group_id).order_by('-game_score')

    answer = " Статистика по победам  \n"
    for user in all_users:
        answer += str(user.first_name) + " " + str(user.last_name)+ ": " + str(user.game_score) + "\n"

    update.message.reply_text(answer)
    # updater.bot.send_message(chat_id=group_id, text=answer)

def is_end_game(group_chat_id):
    all_users = ChatUser.objects.filter(is_vote=False, group_chat_id = group_chat_id)

    if all_users.exists():
        return False
    else:
        return True

def is_admin(chat_id, group_chat_id):
    u = ChatUser.objects.get(chat_id=chat_id, group_chat_id=group_chat_id)
    if u.is_admin:
        return True
    else:
        False

def votes(update, context):
    group_id = get_group_id(update)
    all_users = ChatUser.objects.filter(is_in_game = True, group_chat_id = group_id).order_by('number_of_vote')
    if not(all_users.exists()):
        updater.bot.send_message(chat_id=group_id, text="Игра еще не началась")
        return

    text_joke = str(JokeText.objects.filter(group_chat_id = group_id).last().joke_text)

    # bot.send_message(chat_id=group_id, text='Вопрос был такой')
    # bot.send_message(chat_id=group_id, text=text_joke)
    text = ""
    text += "Вопрос был такой \n"
    text += str(text_joke)
    text += "\n"
    text += "Номер для голосования: Ответ [ Проголосовало за ответ ]"

    updater.bot.send_message(chat_id=group_id, text=text)
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
        updater.bot.send_message(chat_id=group_id, text=str(user.number_of_vote) + " : "  + str(ans) +  "[ "+ str(user.score) + " ]")

def end_game(update, context):
    user = update.message.from_user
    group_id = get_group_id(update)
    if is_admin(user["id"], group_id):
        end_game_func(group_id)
    else:
        update.message.reply_text("Ты не админ, и не можешь вызвать эту команду")

def end_game_func(group_chat_id):
    max_score = ChatUser.objects.filter(group_chat_id = group_chat_id).aggregate(Max('score'))['score__max']

    winner = ChatUser.objects.filter(score = max_score, group_chat_id = group_chat_id)
    w = winner[0]
    w.is_winner = True
    w.game_score = int(w.game_score) + 1
    w.save()

    updater.bot.send_message(chat_id=group_chat_id, text= "Победил: " +  str(w.first_name + " " + w.last_name + " ! \n Можешь поставить новую шутку через /set_joke" ))

    for u in ChatUser.objects.filter(group_chat_id = group_chat_id):
        u.is_in_game = False
        u.score = 0
        u.number_of_vote = 0
        u.is_vote = False
        u.is_answer = False
        u.answer = ""
        u.save()

def vote(update, context):
    user = update.message.from_user
    group_id = get_group_id(update)
    if len(context.args) == 0:
        update.message.reply_text("После /vote необходимо указать цифру")

    vote_num = context.args[0]

    vote_user = ChatUser.objects.get(chat_id = user["id"], group_chat_id = group_id)
    if vote_user.is_vote:
        update.message.reply_text("Ты уже проголосовал")
        return
    try:
        chat_user = ChatUser.objects.get(number_of_vote = vote_num, group_chat_id = group_id)
    except ChatUser.DoesNotExist:
        check_error(update, "Юзер не найден с таким номером")
        return
    else:
        chat_user.score = int(chat_user.score) + 1
        chat_user.save()

        vote_user.is_vote = True
        vote_user.save()
        update.message.reply_text("Твой голос учтен")
        if is_end_game(group_id):
            end_game_func(group_id)

def answer(update, context):
    user = update.message.from_user
    # group_id = get_group_id(update)
    text_ans = ""
    for i in np.arange(len(context.args)):
        text_ans += context.args[i] + " "

    if len(text_ans) == 0:
        update.message.reply_text("Ты не умеешь пользоваться командой /answer \n после /answer должны идти буковки чтобы бот мог записать твой несмешной ответ")
        return

    chat_users = ChatUser.objects.filter(chat_id = user["id"])

    if chat_users.exists():
        chat_user = ChatUser.objects.get( chat_id = user["id"], group_chat_id = chat_users[0].current_group_id )
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
    else:
        check_error(update, "Ты еще не зарегестрировался")


def options(update, context):
    user = update.message.from_user
    # updater.bot.send_message(chat_id=update.message.chat['id'], text =  "test")
    # print(update.message.chat.id)
    # print(update)
    # print(update.message.chat['id'])
    # bot.send_message(chat_id='-1001436950929', text='hello there')
    # bot.send_message(chat_id='-390768652', text='hello there')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    updater.bot.send_message(chat_id=268495107, text=context.error)

def main():

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("options", options))
    dp.add_handler(CommandHandler("register", register))
    dp.add_handler(CommandHandler("start_joke", start_joke))
    dp.add_handler(CommandHandler("answer", answer, pass_args=True))
    dp.add_handler(CommandHandler("vote", vote, pass_args=True))
    dp.add_handler(CommandHandler("score", score))
    dp.add_handler(CommandHandler("votes", votes))
    dp.add_handler(CommandHandler("end_game", end_game))
    dp.add_handler(CommandHandler("set_joke", set_joke, pass_args=True))
    dp.add_handler(CommandHandler("rollback", rollback))
    dp.add_handler(CommandHandler("set_chat", set_chat, pass_args=True))
    dp.add_handler(CommandHandler("list_chat", list_chat))

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