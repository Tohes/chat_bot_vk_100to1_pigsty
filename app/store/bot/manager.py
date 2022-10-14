import json
import typing
from logging import getLogger
from random import choice

from app.store.vk_api.dataclasses import Message, Update, Buttons, User, Game

if typing.TYPE_CHECKING:
    from app.web.app import Application



class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")


    async def handle_updates(self, updates: list[Update], startup = None):
        # эта функция создает кнопку с нужным содержанием. цвет у всех белый пока
        def get_button(content):
            btn = {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"start_game\"}",
                    "label": str(content)
                },
                "color": "secondary"
            }
            return btn

        # эта функция создает "клавиатуру" для передачи в сообщении пользователю с заданными кнопками
        # часть кнопок можно получить из объекта Button, часть сгенерировать в get_button (к примеру, когда нужно
        # передать кнопку номером игры к которой пользователь хочет присоединиться
        def get_keyboard(*args):
            btns = []
            for arg in args:
                btns.append(arg)
            kbd = {"keyboard":
                json.dumps(
                    {
                        "one_time": True,
                        "buttons": [btns]
                    })
            }
            return kbd

        # Создать экзепляр класса Buttons
        buttons = Buttons()
        keyboard = get_keyboard(buttons.start,
                                buttons.end,
                                buttons.join,
                                buttons.answer)

        # вот эта строчка нужна для того, чтобы при перезапуске восстанавливать исходное состояние игры
        if startup == 'started':
            print('Send initial message to all active users')
            print('Game active')
            games = await self.app.store.game.get_games_id()
            actives = await self.app.store.game.get_active()
            joining = await self.app.store.game.get_joining()
            for a in actives:
                board = get_keyboard(buttons.create, buttons.join, buttons.exit)
                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=a,
                        text="Продолжим? /create - создать  /join - присоединиться  /exit - выйти",
                    ), board
                )
            for a in joining:
                board = get_keyboard(buttons.create, buttons.join, buttons.exit)
                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=a,
                        text="Продолжим? /create - создать  /join - присоединиться  /exit - выйти",
                    ), board
                )

            for id_game in games:
                game_obj = await self.app.store.game.get_game_by_id(id_game)
                game_state = game_obj.state
                user_ids = game_obj.user_ids
                question_id = game_obj.question_id
                answer_id = game_obj.answer_id
                if game_state == 'created':
                    keyboard = get_keyboard(buttons.start, buttons.exit)
                    for u in user_ids:

                        await self.app.store.vk_api.send_message(
                            Message(
                                user_id=u,
                                text="Продолжим? Вы присоединились к игре. /start - начать. /exit - выйти",
                            ), keyboard
                        )
                elif game_state == 'started':
                    keyboard = get_keyboard(buttons.answer, buttons.end, buttons.exit)
                    question = await self.app.store.game.get_question_title(question_id)
                    for u in user_ids:
                        await self.app.store.vk_api.send_message(
                            Message(
                                user_id=u,
                                text="Продолжим? Итак, вопрос :-) : " + str(question),
                            ), keyboard
                        )

                elif game_state == 'answer':
                    question = await self.app.store.game.get_question_title(question_id)
                    for u in user_ids:
                        if str(u) == str(answer_id):
                            keyboard = get_keyboard(buttons.end, buttons.exit)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=u,
                                    text="Продолжим? Вы отвечали на вопрос :-) : " + str(question),
                                ), keyboard
                            )
                        else:
                            keyboard = get_keyboard(buttons.end, buttons.exit)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=u,
                                    text="Продолжим? На вопрос отвечает user " + str(answer_id),
                                ), keyboard
                            )





        # здесь обрабатываем каждое полученное сообщение.
        # вообще, вся игра строится как реакция на полученные сообщения

        for update in updates:
            # тут достаем, от кого сообщение получено и считываем текст
            # это id пользователя
            user_id = update['object']['message']['from_id']
            # это текст его сообщения
            text = update['object']['message']['text']

            # если пользователь только пришел в игру написав боту /start
            # запишем его в список активных
            # и вернем набор доступных действий в кнопках
            # создать игру
            is_active = await self.app.store.game.check_active(user_id)
            if not is_active:
            # if user_id not in storage['users']:
                if text == '/start':
                    # пользователь активен, но не присоединился к игре. Поэтому она None
                    await self.app.store.game.set_active(user_id)
                    board = get_keyboard(buttons.create, buttons.join, buttons.exit)
                    await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update["object"]["message"]["from_id"],
                            text="/create - создать игру, /join - присоединиться, /exit - завершить сеанс",
                        ) , board
                    )
            # если пользователь активен, то у есть 5 возможных вариантов:
            # 1. user: Active. game_id: None.
            # 2. user: joining. game_id: None.
            # 3. user: joined. game_id: int, game: "created"
            # 4. user: joined. game_id: int, game: "started"
            # 5. user: joined. game_id: int, game: "answer"
            # тут будет один большой else, где мы обработаем все варианты когда пользователь есть в списке.

            else:
                user = await self.app.store.game.check_active(user_id)

                # вариант когда пользователь вошел в приложение или вышел из игры
                # и не подключен ни к одной игре
                if user.state == 'active':
                    if text == '/create':
                        no_games = await self.app.store.game.get_games_id()
                        if len(no_games) > 1:
                            board = get_keyboard(buttons.create, buttons.join, buttons.exit)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=update["object"]["message"]["from_id"],
                                    text="уже создана игра. попробуйте присоединиться к существующей",
                                ), board
                            )


                        else:
                            numbers = [8844,3322,1155,9977]
                            for ng in no_games:
                                numbers.remove(ng)

                            _game_id = choice(numbers)
                            await self.app.store.game.setup_game(_game_id)
                            await self.app.store.game.add_user(_game_id, user.user_id)
                            await self.app.store.game.set_state(user.user_id, 'joined', game_id=_game_id)
                            await self.app.store.game.set_score(_game_id, user.user_id, 0)

                            keyboard = get_keyboard(buttons.start, buttons.exit)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=user.user_id,
                                    text="вы успешно создали и вошли в игру",
                                ), keyboard
                            )
                            active_users = await self.app.store.game.get_active()
                            for ac in active_users:
                                keyboard = get_keyboard(buttons.create, buttons.join, buttons.exit)
                                await self.app.store.vk_api.send_message(
                                    Message(
                                        user_id=ac,
                                        text="создана игра №" + str(_game_id) + " присоединяйтесь!",
                                    ), keyboard
                                )


                    elif text == '/join':
                        # выдать список игр, к которым можно присоединиться
                        game_list = await self.app.store.game.get_games()
                        if game_list:
                            for i in range(len(game_list)):
                                game_list[i] = get_button(str(game_list[i]))
                            game_list.append(buttons.exit)
                            keyboard = get_keyboard(*game_list)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=user.user_id,
                                    text="выберите игру",
                                ), keyboard
                            )
                            # user.state = 'joining'
                            await self.app.store.game.set_state(user.user_id, 'joining')
                        else:
                            board = get_keyboard(buttons.create, buttons.join, buttons.exit)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=update["object"]["message"]["from_id"],
                                    text="нет доступных игр. попробуйте еще раз или создайте новую",
                                ), board
                            )



                    elif text == '/exit':
                        await self.app.store.game.delete_active(user_id)
                        await self.app.store.vk_api.send_message(
                            Message(
                                user_id=update["object"]["message"]["from_id"],
                                text="сеанс завершен",
                            ), {}
                        )
                    else:
                        board = get_keyboard(buttons.create, buttons.join, buttons.exit)
                        await self.app.store.vk_api.send_message(
                            Message(
                                user_id=update["object"]["message"]["from_id"],
                                text="choose your destiny!",
                            ), board
                        )


                 # из состояния выбора игры
                elif user.state == 'joining':
                    if text == '/exit':
                        # возврат к главному экрану
                        # user.state = 'active'
                        await self.app.store.game.set_state(user.user_id, 'active')
                        board = get_keyboard(buttons.create, buttons.join, buttons.exit)
                        await self.app.store.vk_api.send_message(
                            Message(
                                user_id=user.user_id,
                                text="/create - создать игру, /join - присоединиться, /exit - завершить сеанс",
                            ), board
                        )

                    elif text.isdigit():
                        _game_id = int(text)
                        game_state = await self.app.store.game.get_one_game(_game_id)
                        if game_state and game_state == 'created':
                            await self.app.store.game.add_user(_game_id, user.user_id)
                            await self.app.store.game.set_state(user.user_id, 'joined', game_id=_game_id)
                            await self.app.store.game.set_score(_game_id,user.user_id,0)
                            keyboard = get_keyboard(buttons.start, buttons.exit)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=user.user_id,
                                    text="вы присоединились к игре",
                                ), keyboard
                            )
                        else:
                            await self.app.store.game.set_state(user.user_id, 'active')
                            keyboard = get_keyboard(buttons.create, buttons.join, buttons.exit)
                            await self.app.store.vk_api.send_message(
                            Message(
                                user_id=user.user_id,
                                text="эта игра уже началась или была удалена",
                            ), keyboard
                        )
                        # если да, то подключиться
                        # если нет, то сказать, что эта уже началась и надо
                        # и вернуть экран create join перевести состояние в active

                    else:
                        # если какая-то ерунда, то вернуть стандартную клавиатуру

                        await self.app.store.game.set_state(user.user_id, 'active')
                        board = get_keyboard(buttons.create, buttons.join, buttons.exit)
                        await self.app.store.vk_api.send_message(
                            Message(
                                user_id=user.user_id,
                                text="/create - создать игру, /join - присоединиться, /exit - завершить сеанс",
                            ), board
                        )


                # пользователь подключен к игре, далее возможны три состояния игры:
                # 1. created - игра создана и ждет других участников или начала
                # 2. started - игра началась. Вопрос задан и ожидается нажатие кнопки ответить
                # 3. answer - выбран пользователь, который будет отвечать. Ожидается ответ.
                elif user.state == 'joined':

                    # получим доступ к объекту Game и прочитаем state
                    game_id = user.game_id
                    game = await self.app.store.game.get_game_by_id(game_id)
                    # print(game.state)
                #     исходя из состояния игры будем действовать
                    if game.state == 'created':
                        if text == '/start':

                            await self.app.store.game.set_game_state(game.game_id, 'started')
                            await self.app.store.game.set_state(user.user_id,'joined', game.game_id)
                            question_id = await self.app.store.game.get_question_id(game.game_id)
                            if question_id:
                                await self.app.store.game.set_game_question(game.game_id, question_id)
                                title = await self.app.store.game.get_question_title(question_id)
                                user_list = game.user_ids
                                for _user in user_list:
                                    await self.app.store.vk_api.send_message(
                                        Message(
                                            user_id=_user,
                                            text="Вопрос: " + str(title) + " (Чтобы ответить нажмите /answer)",
                                        ), get_keyboard(buttons.answer, buttons.end, buttons.exit)
                                    )
                            # тут это не должно сработать, но для теста пустой базы нужно
                            else:
                                await self.app.store.game.erase_game(game.game_id)
                                user_list = game.user_ids
                                for _user in user_list:
                                    await self.app.store.game.set_state(_user,'active')
                                    await self.app.store.vk_api.send_message(
                                        Message(
                                            user_id=_user,
                                            text="это были все вопросы. игра завершена",
                                        ), get_keyboard(buttons.create, buttons.join, buttons.exit)
                                    )


                        elif text == '/exit':

                            # если пользователь вышел из игры,
                            # он переходит в статус 'active'

                            await self.app.store.game.delete_user(user.user_id)
                            users = await self.app.store.game.get_users_by_game_id(game.game_id)
                            # если это был последний пользователь в игре, то игра удаляется
                            if users == []:
                                await self.app.store.game.erase_game(game.game_id)
                            await self.app.store.game.set_state(user.user_id, 'active')
                            await self.app.store.vk_api.send_message(
                                Message(
                                user_id=user.user_id,
                                text="вы вышли из игры",
                                ), get_keyboard(buttons.create, buttons.join, buttons.exit)
                                )



                        else:
                    #   если пользователь написал какую-то ерунду, то
                    #   вернуть те же кнопки, что и были, т.е. /start и /exit
                            await self.app.store.vk_api.send_message(
                                Message(
                                    # user_id = update.object.message.from_id,
                                    user_id=update["object"]["message"]["from_id"],
                                    text="доступные опции: /start или /exit",
                                ), get_keyboard(buttons.start, buttons.exit)
                            )


                    elif game.state == 'started':

                    #если игра началась, значит всем пользователям разослан вопрос
                    #но никто еще не вызвался отвечать
                        if text == '/end':
                            # если игра завершается, всех пользователей переводим в активные
                            ranking = await self.app.store.game.get_scores(game.game_id)
                            users = await self.app.store.game.get_users_by_game_id(game.game_id)
                            for u in users:
                                await self.app.store.game.set_state(u, "active")
                                await self.app.store.vk_api.send_message(
                                    Message(
                                        user_id=u,
                                        text="игра завершена. " + str(ranking),
                                    ), get_keyboard(buttons.create, buttons.join, buttons.exit)
                                )
                            await self.app.store.game.erase_game(game.game_id)

                        elif text == '/answer':

                            await self.app.store.game.set_game_answer(game.game_id, user.user_id)
                            await self.app.store.game.set_game_state(game.game_id, "answer")
                            # print('game object', game)
                            question_id = game.question_id
                            title = await self.app.store.game.get_question_title(question_id)
                            user_list = game.user_ids

                            if user_list:
                                for _user in user_list:
                                    if _user != user.user_id:
                                        await self.app.store.vk_api.send_message(
                                            Message(
                                                user_id=_user,
                                                text="на вопрос отвечает user " + str(user.user_id),
                                            ), get_keyboard(buttons.dummy, buttons.end, buttons.exit)
                                        )

                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=user.user_id,
                                    text="Введите ваш ответ на вопрос: " + str(title),
                                ), get_keyboard(buttons.end, buttons.exit)
                            )
                        elif text == '/exit':
                            # удаляем пользователя из игры и проверяем, не последний ли он
                            await self.app.store.game.delete_user(user.user_id)
                            users = await self.app.store.game.get_users_by_game_id(game.game_id)
                            # если это был последний пользователь в игре, то игра удаляется
                            if users == []:
                                await self.app.store.game.erase_game(game.game_id)
                            await self.app.store.game.set_state(user.user_id, 'active')
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=user.user_id,
                                    text="вы вышли из игры",
                                ), get_keyboard(buttons.create, buttons.join, buttons.exit)
                            )

                        else:
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=user.user_id,
                                    text="чтобы ответить, нажмите /answer",
                                ), get_keyboard(buttons.answer, buttons.end, buttons.exit)
                            )


                    # если пользователь первым нажал кнопку, то игра переходит в state = answer
                    # у всех остальных должно появиться оповещение, какой пользователь отвечает на вопрос
                    elif game.state == 'answer':

                        if text == '/answer' and user.user_id != game.answer_id:
                            txt = 'на вопрос отвечает user' + str(game.answer_id)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id = user.user_id,
                                    text = txt,
                                ), get_keyboard(buttons.dummy, buttons.exit, buttons.end)
                            )

                        elif text == '/exit':
                            # если выходит отвечающий пользователь
                            last = False
                            # удаляем пользователя из игры и проверяем, не последний ли он
                            await self.app.store.game.set_state(user.user_id, "active")
                            await self.app.store.game.delete_user(user.user_id)
                            users = await self.app.store.game.get_users_by_game_id(game.game_id)
                            # если это был последний пользователь в игре, то игра удаляется
                            if users == []:
                                await self.app.store.game.erase_game(game.game_id)
                                last = True

                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=user.user_id,
                                    text="вы вышли из игры",
                                ), get_keyboard(buttons.create, buttons.join, buttons.exit)
                            )
                            if not last:
                                # если после выхода в игре остались пользователи то нужно обработать два
                                # варианта. Вышел отвечающий или нет.
                                if str(user.user_id) == str(game.answer_id):
                                    await self.app.store.game.set_game_state(game.game_id, 'started')
                                    # если из игры выходит пользователь, который отвечал
                                    for _user in users:
                                        await self.app.store.vk_api.send_message(
                                            Message(
                                                user_id=_user,
                                                text="отвечающий покинул игру, кто хочет ответить на вопрос?",
                                            ), get_keyboard(buttons.answer, buttons.exit)
                                        )

                                else:
                                    for _user in users:
                                        if _user != user.user_id and _user != game.answer_id:
                                            await self.app.store.vk_api.send_message(
                                                Message(
                                                    user_id=_user,
                                                    text="пользователь" + str(user.user_id) + 'покинул игру',
                                                ), get_keyboard(buttons.dummy, buttons.end, buttons.exit)
                                            )

                        elif text == '/end':
                            # если игра завершается, всех пользователей переводим в активные
                            users = await self.app.store.game.get_users_by_game_id(game.game_id)
                            ranking = await self.app.store.game.get_scores(game.game_id)
                            for u in  users:
                                await self.app.store.game.set_state(u, "active")
                                await self.app.store.vk_api.send_message(
                                    Message(
                                        user_id=u,
                                        text="игра завершена " + str(ranking),
                                    ), get_keyboard(buttons.create, buttons.join, buttons.exit)
                                )
                            await self.app.store.game.erase_game(game.game_id)


                        elif str(user.user_id) == str(game.answer_id):
                            answer = text.strip().lower()
                            answers_scores = await self.app.store.game.get_answers(game.question_id)
                            answers = answers_scores[0]
                            scores = answers_scores[1]
                            ids = answers_scores[2]
                            all_answers = await self.app.store.game.get_all_answers(game.question_id)


                            if answer in answers:
                            # если ответ правильный.
                                ind = answers.index(answer)
                                add_score = scores[ind]
                                await self.app.store.game.set_score(game.game_id, user.user_id,add_score)
                            #   нужно удалить id из ответов
                                await self.app.store.game.delete_answer(ids[ind])
                            # проверить, есть ли еще ответы. Если есть, играем с этим вопросом.
                                check_answers = await self.app.store.game.get_answers(game.question_id)
                                if check_answers[0] != []:
                                    count = len(check_answers[0])
                                    question = await self.app.store.game.get_question_title(game.question_id)
                                    await self.app.store.game.set_game_state(game.game_id,'started')
                                    await self.app.store.game.set_game_answer(game.game_id, None)
                                    users = await self.app.store.game.get_users_by_game_id(game.game_id)
                                    for u in users:
                                        await self.app.store.vk_api.send_message(
                                            Message(
                                                user_id=u,
                                                text="пользователь " + str(user.user_id) +
                                                " получил " + str(add_score) + " за ответ: " + str(answer)+ ". Осталось вариантов: " +
                                                     str(count) + ". Вопрос: " + str(question) + " (чтобы ответить нажмите /answer)",
                                            ), get_keyboard(buttons.answer, buttons.end, buttons.exit)
                                        )



                            # если нет, то проверить, если ли еще вопросы, если есть задать новый
                                else:
                                    await self.app.store.game.delete_question(game.question_id)
                                    new_question_id = await self.app.store.game.get_question_id(game.game_id)
                                    if new_question_id:
                                        await self.app.store.game.set_game_question(game.game_id, new_question_id)
                                        new_title = await self.app.store.game.get_question_title(new_question_id)
                                        await self.app.store.game.set_game_state(game.game_id, 'started')
                                        await self.app.store.game.set_game_answer(game.game_id, None)
                                        users = await self.app.store.game.get_users_by_game_id(game.game_id)
                                        string = "пользователь " + str(user.user_id) + \
                                                         " получил " + str(add_score) + " за ответ: " + str(answer) + ". Новый вопрос: " + \
                                                         str(new_title) + " (чтобы ответить нажмите /answer)"
                                        for u in users:
                                            await self.app.store.vk_api.send_message(
                                                Message(
                                                    user_id=u,
                                                    text = string,
                                                    # text="пользователь " + str(user.user_id) +
                                                    #      " получил " + str(add_score) + ". Новый вопрос: " +
                                                    #      str(new_title),
                                                ), get_keyboard(buttons.answer, buttons.end, buttons.exit)
                                            )

                                    else:
                                        users = await self.app.store.game.get_users_by_game_id(game.game_id)
                                        ranking = await self.app.store.game.get_scores(game.game_id)
                                        for u in users:
                                            await self.app.store.game.set_state(u, "active")
                                            await self.app.store.vk_api.send_message(
                                                Message(
                                                    # маркер
                                                    user_id=user.user_id,
                                                    text="игра завершена " + str(ranking),
                                                ), get_keyboard(buttons.create, buttons.join, buttons.exit)
                                            )
                                        await self.app.store.game.erase_game(game.game_id)
                                    # если нет - завершить игру и разослать всем очки




                                # await self.app.store.game.set_game_state(game.game_id)
                                # users = await self.app.store.game.get_users_by_game_id(game.game_id)
                                # for u in users:
                                #     pass
                            elif answer in all_answers:
                            #     если ответ неправильный но уже был назван
                                await self.app.store.vk_api.send_message(
                                    Message(
                                        user_id=user.user_id,
                                        text="Этот ответ уже отвечен. Ответьте неотвеченным ответом!",
                                    ), get_keyboard(buttons.end, buttons.exit)
                                )
                                pass
                            else:
                                #если ответ неправильный!
                                await self.app.store.game.set_state(user.user_id, "active")
                                await self.app.store.game.delete_user(user.user_id)
                                await self.app.store.vk_api.send_message(
                                    Message(
                                        user_id=user.user_id,
                                        text="поздравляю,вы продули!",
                                    ), get_keyboard(buttons.create, buttons.join, buttons.exit)
                                )

                                users = await self.app.store.game.get_users_by_game_id(game.game_id)
                                # если это был последний пользователь в игре, то игра удаляется
                                if users == []:
                                    await self.app.store.game.erase_game(game.game_id)

                                else:
                                    await self.app.store.game.set_game_state(game.game_id, 'started')
                                    # если отвечающий пользователь продул
                                    for _user in users:
                                        await self.app.store.vk_api.send_message(
                                            Message(
                                                user_id=_user,
                                                text="отвечающий продул, кто хочет ответить на вопрос?",
                                            ), get_keyboard(buttons.answer, buttons.end, buttons.exit)
                                        )

                        else:
                            txt = 'на вопрос отвечает user' + str(game.answer_id)
                            await self.app.store.vk_api.send_message(
                                Message(
                                    user_id=user.user_id,
                                    text=txt,
                                ), get_keyboard(buttons.dummy, buttons.exit, buttons.end)
                            )





