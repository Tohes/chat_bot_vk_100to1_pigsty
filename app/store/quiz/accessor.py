from sqlalchemy import select, insert
from sqlalchemy.engine import ChunkedIteratorResult

from app.base.base_accessor import BaseAccessor
from app.store import Database
from app.quiz.models import (
    Answer,
    Question,
    Theme,
    AnswerModel,
    QuestionModel,
    ThemeModel
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        title_ = title
        U2 = insert(ThemeModel).values(title = title_)
        Q2 = select(ThemeModel).where(title == title_)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(U2)
            await session.commit()
            result = await session.execute(Q2)

        result2 = result.scalars().all()
        if result2:
            ans = Theme(result2[0].id, result2[0].title)

        else:
            ans = None

        return ans


    async def get_theme_by_title(self, title: str) -> Theme | None:

        Q2 = select(ThemeModel).where(ThemeModel.title == title)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result: ChunkedIteratorResult = await session.execute(Q2)

        result2 = result.scalars().all()
        if result2:
            ans = Theme(id = result2[0].id, title = result2[0].title)
        else:
            ans = None

        return ans

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        Q3 = select(ThemeModel).where(ThemeModel.id == id_)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result: ChunkedIteratorResult = await session.execute(Q3)

        result2 = result.scalars().all()
        if result2:
            ans = Theme(id=result2[0].id, title=result2[0].title)
        else:
            ans = None

        return ans

    async def list_themes(self) -> list[Theme]:
        ans = []
        Q3 = select(ThemeModel)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result: ChunkedIteratorResult = await session.execute(Q3)

        result2 = result.scalars().all()
        for res in result2:
            ans.append(Theme(id=res.id, title=res.title))

        return ans


    async def create_answers(
        self, question_id: int, answers: list[Answer]
    ) -> list[Answer]:
        raise NotImplemented

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        title_ = title
        theme_id_ = theme_id
        ans_list = answers

        U2 = insert(QuestionModel).values(title=title_, theme_id = theme_id_ )

        Q2 = select(QuestionModel).where(QuestionModel.title == title_)

        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            await session.execute(U2)
            await session.commit()
            result = await session.execute(Q2)
            result2 = result.scalars().all()

            for answer in ans_list:

                try:
                    U3 = insert(AnswerModel).values(title = answer.title, is_correct = answer.is_correct,
                                                    question_id = result2[0].id)
                except:

                    U3 = insert(AnswerModel).values(title=answer['title'], is_correct=answer['is_correct'],
                                                    question_id=result2[0].id)

                await session.execute(U3)
                await session.commit()

            Q3 = select(AnswerModel).where(AnswerModel.question_id == result2[0].id)

            result3 = await session.execute(Q3)
            result4 = result3.scalars().all()
            resp_list = []
            for rs2 in result4:
                resp_list.append(Answer(title = rs2.title, is_correct=rs2.is_correct))
            ans = Question(id=result2[0].id, title=result2[0].title, theme_id=result2[0].theme_id,
                           answers=resp_list)



        return ans


    async def get_question_by_title(self, title: str) -> Question | None:

        Q4 = select(QuestionModel).where(QuestionModel.title == title)
        dbs = Database(self.app)
        await dbs.connect()
        async with dbs.session() as session:
            result: ChunkedIteratorResult = await session.execute(Q4)
            result2 = result.scalars().all()

            if result2:
                Q3 = select(AnswerModel).where(AnswerModel.question_id == result2[0].id)
                result3 = await session.execute(Q3)
                result4 = result3.scalars().all()
                resp_list = []
                for rs2 in result4:
                    resp_list.append(Answer(title=rs2.title, is_correct=rs2.is_correct))

                ans = Question(id=result2[0].id, title=result2[0].title, theme_id=result2[0].theme_id,
                               answers=resp_list)

            else:
                ans = None

            return ans


    async def list_questions(self, theme_id: int | None = None) -> list[Question]:
        if theme_id == None:
            Q4 = select(QuestionModel)
        else:
            Q4 = select(QuestionModel).where(QuestionModel.theme_id == theme_id)
        dbs = Database(self.app)
        ans_list = []
        await dbs.connect()
        async with dbs.session() as session:
            result: ChunkedIteratorResult = await session.execute(Q4)
            result2 = result.scalars().all()

            for element in result2:
                Q3 = select(AnswerModel).where(AnswerModel.question_id == element.id)
                result3 = await session.execute(Q3)
                result4 = result3.scalars().all()
                resp_list = []
                for rs2 in result4:
                    resp_list.append(Answer(title=rs2.title, is_correct=rs2.is_correct))

                ans_list.append(Question(id=element.id, title=element.title, theme_id=element.theme_id,
                               answers=resp_list))

        return ans_list
