from sqlalchemy import select, insert, delete, update
from sqlalchemy.engine import ChunkedIteratorResult
from random import choice

from app.base.base_accessor import BaseAccessor
from app.store import Database
from app.quiz.models import (
    Answer,
    Question,
    AnswerModel,
    QuestionModel,
    ScoreModel,
)
from app.quiz.models import (
    AnsModel,
    QModel,
    GameModel,
    UserModel,
    ActiveModel
)
from app.store.vk_api.dataclasses import User, Game


class GameAccessor(BaseAccessor):
    # можно вытащить все id вопросов и записать в вопросы игры с id игры
    # можно вытащить все id ответов с id вопросов и записать с id игры

    async def get_games_id(self):
        Q = select(GameModel.game_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result = result.scalars().all()
        if result:
            return result
        else:
            return []

    async def get_active(self):
        Q = select(ActiveModel.user_id).where(ActiveModel.state == 'active')
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result = result.scalars().all()
        if result:
            return result
        else:
            return []

    async def get_joining(self):
        Q = select(ActiveModel.user_id).where(ActiveModel.state == 'joining')
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result = result.scalars().all()
        if result:
            return result
        else:
            return []


    async def setup_game(self, game_id: int):
        # выбрать все из таблицы вопросов
        U0 = insert(GameModel).values(game_id = game_id, state = "created")
        Q = select(QuestionModel)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(U0)
            await session.commit()
            result = await session.execute(Q)
            result = result.scalars().all()
            for res in result:
                # вставить в таблицу вопросов игры
                U = insert(QModel).values(q_id=res.id, game = game_id)
                await session.execute(U)
                await session.commit()
                # выбрать все ответы для данного вопроса
                Q2 = select(AnswerModel).where(AnswerModel.question_id == res.id )
                result3: ChunkedIteratorResult = await session.execute(Q2)
                result4 = result3.scalars().all()
                # теперь все ответы записать в таблицу игры id ответов
                for res2 in result4:
                    U2 = insert(AnsModel).values(question_id=res.id, id = res2.id )
                    await session.execute(U2)
                await session.commit()



    async def get_games(self):
        Q = select(GameModel.game_id).where(GameModel.state == "created")
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result2 = result.scalars().all()

            return result2

    async def get_one_game(self, game_id):
        Q = select(GameModel.state).where(GameModel.game_id == game_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            if result:
                return result.scalar()
            else:
                return None

    async def get_game_by_id(self, game_id):
        Q = select(GameModel).where(GameModel.game_id == game_id)
        Q2 = select(UserModel.user_id).where(UserModel.game_id == game_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result2 = await session.execute(Q2)
            if result:
                answer =  result.scalar()
                if result2:
                    answer2 = result2.scalars().all()
                else:
                    answer2 = []
                game = Game(game_id=answer.game_id, state=answer.state, user_ids=answer2, answer_id= answer.answer_id, question_id=answer.question_id)
                return game
            else:
                return None

    async def set_game_state(self, game_id, state):
        Q = update(GameModel).where(GameModel.game_id == game_id).values(state = state)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            await session.commit()

    async def set_game_answer(self, game_id, answer_id):
        Q = update(GameModel).where(GameModel.game_id == game_id).values(answer_id = str(answer_id))
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            await session.commit()

    async def set_game_question(self, game_id, question_id):
        Q = update(GameModel).where(GameModel.game_id == game_id).values(question_id = question_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            await session.commit()


    async def erase_game(self, game_id):
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(delete(GameModel).where(GameModel.game_id == game_id))
            await session.commit()

    async def add_user(self, game_id: int, user_id):
        Q = insert(UserModel).values( user_id = user_id, game_id = game_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(Q)
            await session.commit()


    async def delete_user(self, user_id):
        Q = delete(UserModel).where(UserModel.user_id == user_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(Q)
            await session.commit()

    async def get_users_by_game_id(self, game_id):
        Q = select(UserModel.user_id).where(UserModel.game_id == game_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            if result:
                answer = result.scalars().all()
                return answer
            else:
                return None



    async def check_active(self, user_id):
        Q = select(ActiveModel).where(ActiveModel.user_id == user_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result2 = result.scalar()
            if result2:
                return User(user_id = result2.user_id, state = result2.state, game_id= result2.game_id)
            else:
                return None

    async def set_active(self, user_id):
        Q = insert(ActiveModel).values( user_id = user_id, state = 'active')
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(Q)
            await session.commit()


    async def set_state(self, user_id, state, game_id = None):
        Q = update(ActiveModel).where(ActiveModel.user_id == user_id).values( state = state, game_id = game_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(Q)
            await session.commit()

    async def get_user_state(self, user_id):
        Q = select(ActiveModel).where(ActiveModel.user_id == user_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result2 = result.scalar()
            return result2.state


    async def delete_active(self, user_id):
        Q = delete(ActiveModel).where(ActiveModel.user_id == user_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(Q)
            await session.commit()

    async def get_answers(self, question_id):
        ans_list = []
        score_list = []
        id_list = []
        Q = select(AnsModel.id).where(AnsModel.question_id == question_id)

        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result = result.scalars().all()

            if result:
                for ans_id in result:
                    id_list.append(ans_id)
                    Q2 = select(AnswerModel.title).where(AnswerModel.id == ans_id)
                    result2 = await session.execute(Q2)
                    result2 = result2.scalar()
                    ans_list.append(str(result2).strip().lower())
                    Q3 = select(AnswerModel.score).where(AnswerModel.id == ans_id)
                    result3 = await session.execute(Q3)
                    result3 = result3.scalar()
                    score_list.append(result3)


            return (ans_list, score_list, id_list)

    async def get_all_answers(self, question_id):
        ans_list = []
        Q = select(AnswerModel.title).where(AnswerModel.question_id == question_id)

        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result = result.scalars().all()

            for i in range(len(result)):
                result[i] = str(result[i]).strip().lower()

            return result



    async def delete_answer(self, id):
        Q = delete(AnsModel).where(AnsModel.id == id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            await session.commit()


    async def get_question_id(self, game_id):
        Q = select(QModel.q_id).where(QModel.game == game_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result = result.scalars().all()

            if result:
                q_id = choice(result)
                return q_id
            else:
                return None

    async def get_question_title(self, id):
        Q = select(QuestionModel.title).where(QuestionModel.id == id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            result = result.scalar()
            return result


    async def delete_question(self, id):
        Q = delete(QModel).where(QModel.q_id == id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            await session.commit()

    async def set_score(self, game_id, user_id, score):
        Q = select(ScoreModel.score).where(ScoreModel.user_id == user_id and ScoreModel.game_id == game_id)
        I = insert(ScoreModel).values(game_id = game_id, user_id = user_id, score = score)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            old_score = result.scalar()
            # print('old score', old_score)
            if old_score == None:
                # print('insert')
                await session.execute(I)
                await session.commit()
            else:
                # print('update')
                U = update(ScoreModel).where(ScoreModel.user_id == user_id and ScoreModel.game_id == game_id).values(
                    score=score + old_score)
                await session.execute(U)
                await session.commit()

    async def get_scores(self, game_id):
        score_list = []
        Q = select(ScoreModel).where(ScoreModel.game_id == game_id)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result = await session.execute(Q)
            scores = result.scalars().all()

        if scores:
            for s in scores:
                score_list.append("user: " + str(s.user_id) + " , scores: " + str(s.score))
            ans = ' | '.join(score_list)
        return ans
