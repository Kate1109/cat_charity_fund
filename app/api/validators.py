from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


charity_project_crud = CRUDBase(CharityProject)


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
):
    project_id = await charity_project_crud.get_project_by_name(
        CharityProject, project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


def check_charity_project_invested_sum(project: CharityProject,
                                       full_amount: int):
    if project.invested_amount > full_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нелья установить значение'
            'full_amount меньше уже вложенной суммы.'
        )


async def check_charity_project_exists(
    project_id: int,
    session: AsyncSession,
):
    project = await charity_project_crud.get(
        obj_id=project_id, session=session
    )
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!'
        )
    return project


def check_charity_project_already_invested(charity_project: CharityProject):
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )


def check_charity_project_closed(charity_project: CharityProject):
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )
