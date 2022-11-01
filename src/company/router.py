from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.auth.services import get_current_user
from src.company.schemes import CompanyScheme, InviteScheme
from src.database import async_session
from src.company.crud import CompanyCrud
from typing import List
from src.user.crud import UserCrud

comp_router = APIRouter()


async def get_session():
    async with async_session() as session:
        async with session.begin():
            yield session


@comp_router.get('/', response_model=List[CompanyScheme])
async def get_all_companies(current_user=Depends(get_current_user),
                            session=Depends(get_session)) -> List[CompanyScheme]:
    company_crud_method = CompanyCrud(db_session=session)

    companies = await company_crud_method.get_all_companies()
    return [CompanyScheme(id=company.id,
                          title=company.title,
                          description=company.description,
                          owner_id=company.owner_id) for company in companies]


@comp_router.post('/create', response_model=CompanyScheme)
async def create_company(title: str, description: str, is_visible: bool,
                         current_user=Depends(get_current_user),
                         session=Depends(get_session)) -> CompanyScheme:
    company_crud_method = CompanyCrud(db_session=session)

    company = await company_crud_method.create_company(title=title,
                                                       description=description,
                                                       is_visible=is_visible,
                                                       current_user=current_user)
    return CompanyScheme(id=company.id,
                         title=company.title,
                         description=company.description,
                         owner_id=company.owner_id,
                         is_visible=company.is_visible)


@comp_router.put('/change_visibility/{company_id}')
async def change_visibility(company_id: int, is_visible: bool,
                            current_user=Depends(get_current_user),
                            session=Depends(get_session)) -> set:
    company_crud_method = CompanyCrud(db_session=session)

    await company_crud_method.change_visibility(company_id=company_id,
                                                is_visible=is_visible,
                                                current_user=current_user)

    return {"changes have been applied"}


@comp_router.put('/update_company/{company_id}')
async def update_company(company_id: int, title: str, description: str,
                         current_user=Depends(get_current_user),
                         session=Depends(get_session)) -> CompanyScheme:
    company_crud_method = CompanyCrud(db_session=session)

    await company_crud_method.update_company(company_id=company_id,
                                             title=title,
                                             description=description,
                                             current_user=current_user)

    return CompanyScheme(id=company_id,
                         title=title,
                         description=description,
                         owner_id=current_user.id)


@comp_router.delete('/{company_id}')
async def delete_company(company_id: int, current_user=Depends(get_current_user),
                         session=Depends(get_session)) -> set[str]:
    company_crud_method = CompanyCrud(db_session=session)

    await company_crud_method.delete_company(company_id=company_id,
                                             current_user=current_user)

    return {f"company with id {company_id} has been successfully deleted"}


@comp_router.post("/invite/{user_id}", response_model=InviteScheme)
async def invite_user_to_company(user_id: int, company_id: int,
                                 current_user=Depends(get_current_user),
                                 session=Depends(get_session)) -> InviteScheme:
    user_crud = UserCrud(db_session=session)

    company_crud_method = CompanyCrud(db_session=session)

    # to check whether user exists
    await user_crud.get_user_by_id(user_id=user_id)
    invite = await company_crud_method.invite_user_to_company(user_id=user_id,
                                                              company_id=company_id,
                                                              current_user=current_user)

    return InviteScheme(id=invite.id,
                        user_id=invite.user_id,
                        company_id=invite.company_id,
                        is_accepted=invite.is_accepted)


@comp_router.put("/remove_employee_from_company/{employee_id}")
async def remove_employee_from_company(employee_id: int, company_id: int,
                                       current_user=Depends(get_current_user),
                                       session=Depends(get_session)) -> set[str]:
    company_crud_method = CompanyCrud(db_session=session)

    await company_crud_method.remove_employee_from_company(employee_id=employee_id,
                                                           company_id=company_id,
                                                           current_user=current_user)

    return {f"employee with id {employee_id} has been successfully removed from company with id {company_id}"}


@comp_router.put("/accept_request/{user_id}")
async def accept_request(user_id: int, company_id: int,
                         current_user=Depends(get_current_user),
                         session=Depends(get_session)) -> set[str]:
    company_crud_method = CompanyCrud(db_session=session)

    await company_crud_method.accept_request(user_id=user_id,
                                             company_id=company_id,
                                             current_user=current_user)
    await company_crud_method.add_user_to_employees(user_id=user_id,
                                                    company_id=company_id)

    return {f"request from user with id {user_id} to company with id {company_id} was approved"}


@comp_router.put("/appoint_admin/{user_id}")
async def appoint_admin(user_id: int, company_id: int,
                        current_user=Depends(get_current_user),
                        session=Depends(get_session)) -> set[str]:
    company_crud_method = CompanyCrud(db_session=session)

    await company_crud_method.appoint_admin(user_id=user_id,
                                            company_id=company_id,
                                            current_user=current_user)

    return {f"user with id {user_id} was appointed as admin in company with id {company_id}"}


@comp_router.put("/remove_admin_from_company/{employee_id}")
async def remove_employee_from_company(employee_id: int, company_id: int,
                                       current_user=Depends(get_current_user),
                                       session=Depends(get_session)) -> set[str]:
    company_crud_method = CompanyCrud(db_session=session)

    await company_crud_method.remove_admin_from_company(employee_id=employee_id,
                                                        company_id=company_id,
                                                        current_user=current_user)

    return {f"employee with id {employee_id} was deprived of administrator rights in company with id {company_id}"}


@comp_router.get("get_quizzes_for_company/{company_id}")
async def get_quizzes_for_company(company_id: int, current_user=Depends(get_current_user),
                                  session=Depends(get_session)):
    from src.quiz.crud import QuizCrud

    quiz_crud_method = QuizCrud(db_session=session)

    quizzes = await quiz_crud_method.get_quizzes_for_company(company_id=company_id)

    return quizzes
