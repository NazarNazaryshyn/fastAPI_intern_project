from fastapi import HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session, selectinload

from src.quiz.models import Quiz, Question, Variant, Result
from src.user.models import User

from src.quiz.schemes import QuizWithQuestion

from typing import List


class QuizCrud:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_quiz(self, company_id: int, title: str, description: str, current_user: User) -> Quiz:
        from src.company.crud import CompanyCrud
        company_crud_method = CompanyCrud(db_session=self.db_session)

        company = await company_crud_method.get_company_admins(company_id=company_id)

        admins_id = [admin.id for admin in company.admins]

        if company.owner_id != current_user.id:
            if current_user.id not in admins_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="you have no access to create quiz")

        new_quiz = Quiz(
            company_id=company_id,
            title=title,
            description=description,
            frequency=0
        )

        self.db_session.add(new_quiz)
        await self.db_session.flush()

        return new_quiz

    async def get_quiz_by_id(self, quiz_id: int) -> Quiz or None:
        quiz = (await self.db_session.execute(select(Quiz)
                                              .filter(Quiz.id == quiz_id))) \
            .scalars().first()

        if quiz is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no quiz with id {quiz_id}")

        return quiz

    async def get_quizzes_for_company(self, company_id: int) -> List[Quiz]:
        from src.company.crud import CompanyCrud
        company_crud = CompanyCrud(db_session=self.db_session)

        await company_crud.get_company_by_id(company_id=company_id)

        quizzes = (await self.db_session.execute(select(Quiz).filter(company_id == company_id))).scalars().all()

        return quizzes

    async def create_question(self, quiz_id: int, question: str) -> Question:
        quiz = await self.get_quiz_by_id(quiz_id=quiz_id)

        new_question = Question(quiz_id=quiz_id,
                                question=question)

        self.db_session.add(new_question)
        await self.db_session.flush()

        return new_question

    async def get_question_by_id(self, question_id: int) -> Question or None:
        question = (await self.db_session.execute(select(Question)
                                                  .filter(Question.id == question_id))) \
            .scalars().first()

        if question is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no question with id {question_id}")

        return question

    async def create_variant(self, question_id: int, answer: str, is_correct: bool) -> Variant:
        await self.get_question_by_id(question_id=question_id)

        new_variant = Variant(question_id=question_id,
                              answer=answer,
                              is_correct=is_correct)

        self.db_session.add(new_variant)
        await self.db_session.flush()

        return new_variant

    async def delete_quiz(self, quiz_id: int, current_user: User) -> None:
        from src.company.crud import CompanyCrud

        quiz = await self.get_quiz_by_id(quiz_id=quiz_id)

        company_crud_method = CompanyCrud(db_session=self.db_session)

        company = await company_crud_method.get_company_by_id(company_id=quiz.company_id)
        comp = await company_crud_method.get_company_admins(company_id=quiz.company_id)

        admins_ids = [admin.id for admin in comp.admins]

        if current_user.id != company.owner_id:
            if current_user.id not in admins_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="you have no access")

        await self.db_session.execute(delete(Quiz).filter(Quiz.id == quiz_id))
        await self.db_session.commit()

    async def update_quiz(self, quiz_id: int, title: str, description: str, frequency: int, current_user: User) -> None:
        from src.company.crud import CompanyCrud

        quiz = await self.get_quiz_by_id(quiz_id=quiz_id)

        company_crud_method = CompanyCrud(db_session=self.db_session)

        company = await company_crud_method.get_company_by_id(company_id=quiz.company_id)
        comp = await company_crud_method.get_company_admins(company_id=quiz.company_id)

        admins_ids = [admin.id for admin in comp.admins]

        if current_user.id != company.owner_id:
            if current_user.id not in admins_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="you have no access")

        query = (
            update(Quiz)
                .where(Quiz.id == quiz_id)
                .values(
                title=quiz.title if title is None else title,
                description=quiz.description if description is None else description,
                frequency=quiz.frequency if frequency is None else frequency
            )
                .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.flush()

    async def update_question(self, question_id: int, question: str, current_user: User) -> None:
        from src.company.crud import CompanyCrud

        question_from_db = await self.get_question_by_id(question_id=question_id)

        company_crud_method = CompanyCrud(db_session=self.db_session)

        quiz = await self.get_quiz_by_id(quiz_id=question_from_db.quiz_id)
        company = await company_crud_method.get_company_by_id(company_id=quiz.company_id)
        comp = await company_crud_method.get_company_admins(company_id=quiz.company_id)

        admins_ids = [admin.id for admin in comp.admins]

        if current_user.id != company.owner_id:
            if current_user.id not in admins_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="you have no access")

        query = (
            update(Question)
                .where(Question.id == question_id)
                .values(
                question=question_from_db.question if question is None else question,
            )
                .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.flush()

    async def get_variant(self, variant_id: int) -> Variant or None:
        variant = (await self.db_session.execute(select(Variant)
                                                 .filter(Variant.id == variant_id))) \
            .scalars().first()

        if variant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no variant with id {variant_id}")

        return variant

    async def update_variant(self, variant_id: int, answer: str, is_correct: bool, current_user: User) -> None:
        from src.company.crud import CompanyCrud

        variant_from_db = await self.get_variant(variant_id=variant_id)

        question_from_db = await self.get_question_by_id(question_id=variant_from_db.question_id)

        company_crud_method = CompanyCrud(db_session=self.db_session)

        quiz = await self.get_quiz_by_id(quiz_id=question_from_db.quiz_id)
        company = await company_crud_method.get_company_by_id(company_id=quiz.company_id)
        comp = await company_crud_method.get_company_admins(company_id=quiz.company_id)

        admins_ids = [admin.id for admin in comp.admins]

        if current_user.id != company.owner_id:
            if current_user.id not in admins_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="you have no access")

        query = (
            update(Variant)
                .where(Variant.id == variant_id)
                .values(
                answer=variant_from_db.answer if answer is None else answer,
                is_correct=variant_from_db.is_correct if is_correct is None else is_correct
            )
                .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.flush()

    async def pass_quiz(self, quiz_id: int, company_id: int, question_id: int, answer: str, current_user: User):
        quiz = await self.get_quiz_by_id(quiz_id=quiz_id)

        if quiz.id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no quiz with id {quiz_id} in company with id {company_id}")

        await self.get_question_by_id(question_id=question_id)

        answer = (await self.db_session.execute(select(Variant)
                                                .filter(Variant.answer == answer,
                                                        Variant.question_id == question_id))) \
                                                .scalars().first()

        result = (await self.db_session.execute(select(Result)
                                                .filter(Result.user_id == current_user.id,
                                                        Result.quiz_id == quiz_id)))\
                                                .scalars().first()

        if result is None:
            if answer.is_correct:
                new_result = Result(
                    user_id=current_user.id,
                    quiz_id=quiz_id,
                    correct_answers=1,
                    all_answers=1,
                    gpa=1
                )
            else:
                new_result = Result(
                    user_id=current_user.id,
                    quiz_id=quiz_id,
                    correct_answers=0,
                    all_answers=1,
                    gpa=0
                )
        else:
            if answer.is_correct:
                query = (
                    update(Result)
                    .where(Result.user_id == current_user.id,
                           Result.quiz_id == quiz_id)
                    .values(
                        correct_answers=result.correct_answers + 1,
                        all_answers=result.all_answers + 1,
                        gpa=(result.correct_answers + 1)/(result.all_answers + 1)
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await self.db_session.execute(query)
                await self.db_session.flush()
            else:
                query = (
                    update(Result)
                        .where(Result.user_id == current_user.id,
                               Result.quiz_id == quiz_id)
                        .values(
                        all_answers=result.all_answers + 1,
                        gpa=result.correct_answers/(result.all_answers + 1)
                    )
                    .execution_options(synchronize_session="fetch")
                )
                await self.db_session.execute(query)
                await self.db_session.flush()

        return result


