from typing import List

from fastapi import APIRouter, Depends

from src.auth.services import get_current_user
from src.quiz.crud import QuizCrud
from src.quiz.models import Quiz
from src.quiz.schemes import QuizSchema, VariantSchema, QuestionSchema, TakeQuiz, GpaScheme, QuizResScheme, QuizResults

from src.company.router import get_session

quiz_router = APIRouter()


@quiz_router.post('/create_quiz', response_model=QuizSchema)
async def create_quiz(company_id: int, title: str, description: str, frequency: int,
                      current_user=Depends(get_current_user),
                      session=Depends(get_session)) -> QuizSchema:
    quiz_crud = QuizCrud(db_session=session)

    quiz = await quiz_crud.create_quiz(company_id=company_id,
                                       title=title,
                                       description=description,
                                       current_user=current_user,
                                       frequency=frequency)

    return QuizSchema(title=title,
                      description=description,
                      frequency=frequency)


@quiz_router.post("/create_question", response_model=QuestionSchema)
async def create_question(quiz_id: int, question: str,
                          current_user=Depends(get_current_user),
                          session=Depends(get_session)) -> QuestionSchema:
    quiz_crud = QuizCrud(db_session=session)

    await quiz_crud.create_question(quiz_id=quiz_id,
                                    question=question)

    return QuestionSchema(question=question,
                          quiz_id=quiz_id)


@quiz_router.post("/create_variant", response_model=VariantSchema)
async def create_variant(question_id: int, answer: str, is_correct: bool,
                         current_user=Depends(get_current_user),
                         session=Depends(get_session)) -> VariantSchema:
    quiz_crud = QuizCrud(db_session=session)

    variant = await quiz_crud.create_variant(question_id=question_id,
                                             answer=answer,
                                             is_correct=is_correct)

    return VariantSchema(answer=answer,
                         is_correct=is_correct)


@quiz_router.delete('/delete_quiz/{quiz_id}')
async def delete_quiz(quiz_id: int, current_user=Depends(get_current_user),
                      session=Depends(get_session)) -> set:
    quiz_crud = QuizCrud(db_session=session)

    await quiz_crud.delete_quiz(quiz_id=quiz_id,
                                current_user=current_user)

    return {"quiz has been successfully deleted"}


@quiz_router.put("/update_quiz/{quiz_id}", response_model=QuizSchema)
async def update_quiz(quiz_id: int, title: str, description: str, frequency: int,
                      current_user=Depends(get_current_user),
                      session=Depends(get_session)) -> QuizSchema:
    quiz_crud = QuizCrud(db_session=session)
    await quiz_crud.update_quiz(quiz_id=quiz_id,
                                title=title,
                                description=description,
                                frequency=frequency,
                                current_user=current_user)

    return QuizSchema(title=title,
                      description=description,
                      frequency=frequency)


@quiz_router.put("/update_question/{question_id}", response_model=QuestionSchema)
async def update_question(question_id: int, question: str,
                          current_user=Depends(get_current_user),
                          session=Depends(get_session)) -> QuestionSchema:
    quiz_crud = QuizCrud(db_session=session)
    await quiz_crud.update_question(question_id=question_id,
                                    question=question,
                                    current_user=current_user)

    return QuestionSchema(question=question)


@quiz_router.put("/update_variant/{variant_id}", response_model=VariantSchema)
async def update_variant(variant_id: int, answer: str, is_correct: bool,
                         current_user=Depends(get_current_user),
                         session=Depends(get_session)) -> VariantSchema:
    quiz_crud = QuizCrud(db_session=session)
    await quiz_crud.update_variant(variant_id=variant_id,
                                   answer=answer,
                                   is_correct=is_correct,
                                   current_user=current_user)

    return VariantSchema(answer=answer,
                         is_correct=is_correct)


@quiz_router.put("/pass_quiz/{quiz_id}")
async def pass_quiz(quiz: TakeQuiz, current_user = Depends(get_current_user),
                    session = Depends(get_session)) -> QuizResScheme:

    quiz_crud = QuizCrud(db_session=session)

    res = await quiz_crud.pass_quiz(quiz=quiz, current_user=current_user)

    return QuizResScheme(all_answers=res['all_answers'],
                         correct_answers=res['correct_answers'])


@quiz_router.get("get_all_results", response_model=List[QuizResults])
async def get_all_results(current_user = Depends(get_current_user),
                          session = Depends(get_session)) -> List[QuizResults]:

    quiz_crud = QuizCrud(db_session=session)

    res_from_db = await quiz_crud.get_all_results()

    res = [QuizResults(id=r.id,
                       user_id=r.user_id,
                       quiz_id=r.quiz_id,
                       correct_answers=r.correct_answers,
                       all_answers=r.all_answers,
                       gpa=r.gpa) for r in res_from_db]

    return res


@quiz_router.get("get_gpa_for_one_quiz/{quiz_id}", response_model=GpaScheme)
async def get_gpa_for_one_quiz(quiz_id: int, current_user = Depends(get_current_user),
                               session = Depends(get_session)) -> GpaScheme:

    quiz_crud = QuizCrud(db_session=session)

    gpa = await quiz_crud.get_gpa_for_one_quiz(quiz_id=quiz_id)

    return GpaScheme(gpa=gpa['gpa'])


@quiz_router.get("get_gpa_for_all_quizzes", response_model=GpaScheme)
async def get_gpa_for_all_quizzes(current_user = Depends(get_current_user),
                                  session = Depends(get_session)) -> GpaScheme:

    quiz_crud = QuizCrud(db_session=session)

    gpa = await quiz_crud.get_gpa_for_all_quizzes()

    return GpaScheme(gpa=gpa['gpa'])
