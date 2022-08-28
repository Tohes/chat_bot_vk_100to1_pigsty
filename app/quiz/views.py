from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPNotAcceptable, HTTPBadRequest
from aiohttp_apispec import querystring_schema, request_schema, response_schema
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):

        title = self.data["title"]
        # ]  # TO_DO: заменить на self.data["title"] после внедрения валидации
        # TO_DO: проверять, что не существует темы с таким же именем, отдавать 409 если существует
        check_theme = await self.store.quizzes.get_theme_by_title(title=title)
        if check_theme == None:
            theme = await self.store.quizzes.create_theme(title=title)
            print('crocodile')
            print(theme)
            return json_response(data= {"id": theme.id, "title": theme.title})
            # return json_response(data=ThemeSchema().dump(theme))
        else:
            raise HTTPConflict


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema)
    async def get(self):
        ans = await self.store.quizzes.list_themes()
        resp = {"themes": ans}
        return json_response(data=ThemeListSchema().dump(resp))


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data['title']
        theme_id = self.data['theme_id']
        ans = await self.store.quizzes.get_theme_by_id(theme_id)
        if ans == None:
            raise HTTPNotFound
        answers = self.data['answers']
        correct = 0
        for answer in answers:
            if answer['is_correct'] == True:
                correct += 1

        if correct != 1 or len(answers) < 2:
            raise HTTPBadRequest
        print('kitten')
        question = await self.store.quizzes.create_question(title=title, theme_id=theme_id, answers=answers)
        print('BIG CAT')
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        print('caterpillar')
        try:
            theme_id = self.request.query["theme_id"]
        except:
            theme_id = None
        print('butterfly')
        ans = await self.store.quizzes.list_questions(theme_id)
        resp = {"questions": ans}
        return json_response(data=ListQuestionSchema().dump(resp))
