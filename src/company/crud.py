from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.database import async_session
from src.company.models import Company, Invite, Request
from typing import List, Optional

from sqlalchemy.orm import selectinload

from src.quiz.models import Quiz
from src.user.models import User

db = async_session()


class CompanyCrudMethod:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def user_is_owner(self, user_id: int, owner_id: int) -> None:
        if user_id != owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="you have no access")

    async def if_employee_exists(self, employee: User, employee_id: int) -> None:
        if employee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no user with id {employee_id}")

    async def get_all_companies(self) -> List[Company]:
        companies = (await self.db_session.execute(select(Company)
                                                   .filter(Company.is_visible == True)))\
                                                   .scalars().all()

        return companies

    async def get_company_by_title(self, title: str) -> Company or None:
        company = (await self.db_session.execute(select(Company)
                                                 .filter(Company.title == title)))\
                                                 .scalars().first()

        if company is None:
            None

        return company

    async def get_company_by_id(self, company_id: int) -> Company or None:
        company = (await self.db_session.execute(select(Company)
                                                 .filter(Company.id == company_id)
                                                 .options(selectinload(Company.employees))))\
                                                 .scalars().first()

        if company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no company with id {company_id}")

        return company

    async def get_company_admins(self, company_id: int) -> Company or None:
        company = (await self.db_session.execute(select(Company)
                                                 .filter(Company.id == company_id)
                                                 .options(selectinload(Company.admins))))\
                                                 .scalars().first()

        if company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no company with id {company_id}")

        return company

    async def create_company(self, title: str, description: str, is_visible: bool, current_user: User) -> Company:
        company_in_db = await self.get_company_by_title(title=title)

        if company_in_db:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="company with this title already exists")

        new_company = Company(
            title=title,
            description=description,
            is_visible=is_visible,
            owner_id=current_user.id
        )
        self.db_session.add(new_company)
        await self.db_session.flush()

        return new_company

    async def change_visibility(self, company_id: int, is_visible: bool, current_user: User) -> None:
        company = await self.get_company_by_id(company_id=company_id)

        await self.user_is_owner(user_id=current_user.id, owner_id=company.owner_id)

        query = (
            update(Company)
            .where(Company.id == company_id)
            .values(
                is_visible=is_visible
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.commit()

    async def update_company(self, company_id: int, title: str, description: str, current_user: User) -> None:
        company = await self.get_company_by_id(company_id=company_id)

        await self.user_is_owner(user_id=current_user.id, owner_id=company.owner_id)

        query = (
            update(Company)
            .where(Company.id == company_id)
            .values(
                title=title,
                description=description
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.flush()

    async def delete_company(self, company_id: int, current_user: User) -> None:
        company = await self.get_company_by_id(company_id=company_id)

        await self.user_is_owner(user_id=current_user.id, owner_id=company.owner_id)

        await self.db_session.execute(delete(Company).filter(Company.id == company_id))
        await self.db_session.commit()

    async def invite_user_to_company(self, user_id: int, company_id: int, current_user: User) -> Invite:
        company = await self.get_company_by_id(company_id=company_id)

        await self.user_is_owner(user_id=current_user.id, owner_id=company.owner_id)

        new_invite = Invite(user_id=user_id,
                            company_id=company_id,
                            is_accepted=False)

        self.db_session.add(new_invite)
        await self.db_session.flush()

        return new_invite

    async def add_user_to_employees(self, user_id: int, company_id: int) -> None:
        from src.user.crud import CrudMethods

        company = await self.get_company_by_id(company_id=company_id)
        user = await CrudMethods(db_session=self.db_session).get_user_by_id(user_id=user_id)

        company.employees.append(user)

        await self.db_session.commit()

    async def remove_employee_from_company(self, employee_id: int, company_id: int, current_user: User) -> None:
        from src.user.crud import CrudMethods
        user_crud = CrudMethods(db_session=self.db_session)

        employee = await user_crud.get_user_by_id(user_id=employee_id)
        company = await self.get_company_by_id(company_id=company_id)

        await self.if_employee_exists(employee=employee, employee_id=employee_id)

        await self.user_is_owner(user_id=current_user.id, owner_id=company.owner_id)

        if employee not in company.employees:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no employee with id {employee_id} in company with id {company_id}")

        company.employees.remove(employee)
        await self.db_session.commit()

    async def get_request(self, user_id: int, company_id: int) -> Optional[Request]:
        request = (await self.db_session.execute(select(Request)
                                                 .filter(Request.user_id == user_id,
                                                         Request.company_id == company_id)))\
                                                 .scalars().first()

        if request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no request from user with id {user_id} to company with id {company_id}")

        return request

    async def accept_request(self, user_id: int, company_id: int, current_user: User) -> None:
        from src.user.crud import CrudMethods

        user_crud = CrudMethods(db_session=self.db_session)
        await user_crud.get_user_by_id(user_id=user_id)

        company = await self.get_company_by_id(company_id=company_id)

        await self.user_is_owner(user_id=current_user.id, owner_id=company.owner_id)

        await self.get_request(user_id=user_id, company_id=company_id)

        query = (
            update(Request)
            .where(Request.user_id == user_id, Request.company_id == company_id)
            .values(
                is_accepted=True
            )
            .execution_options(synchronize_session="fetch")
        )

        await self.db_session.execute(query)
        await self.db_session.commit()

    async def appoint_admin(self, user_id: int, company_id: int, current_user: User) -> None:
        from src.user.crud import CrudMethods
        user_crud = CrudMethods(db_session=self.db_session)

        user = await user_crud.get_user_by_id(user_id=user_id)

        company = await self.get_company_admins(company_id=company_id)
        company_employees = await self.get_company_by_id(company_id=company_id)

        await self.user_is_owner(user_id=current_user.id, owner_id=company.owner_id)

        if user not in company_employees.employees:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no user with id {user_id} in company with id {company_id}")

        company.admins.append(user)

        await self.db_session.commit()

    async def remove_admin_from_company(self, employee_id: int, company_id: int, current_user: User) -> None:
        from src.user.crud import CrudMethods

        user_crud = CrudMethods(db_session=self.db_session)

        employee = await user_crud.get_user_by_id(user_id=employee_id)
        company = await self.get_company_by_id(company_id=company_id)
        company_admins = await self.get_company_admins(company_id=company_id)

        await self.if_employee_exists(employee=employee, employee_id=employee_id)
        await self.user_is_owner(user_id=current_user.id, owner_id=company.owner_id)

        if employee not in company_admins.admins:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no admin with id {employee_id} in company with id {company_id}")

        company_admins.admins.remove(employee)
        await self.db_session.commit()

