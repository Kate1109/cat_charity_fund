from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_name_duplicate,
                                check_charity_project_invested_sum,
                                check_charity_project_exists,
                                check_charity_project_already_invested,
                                check_charity_project_closed)
from app.crud.charity_project import charity_project_crud
from app.crud.base import CRUDBase
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.models import CharityProject, Donation
from app.services.investing import (new_investing_process,
                                    get_not_full_invested_objects)
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)


router = APIRouter()
charity_project_crud = CRUDBase(CharityProject)


@router.get(
    path='/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    """Возвращает список всех проектов."""
    return await charity_project_crud.get_multi(session=session)


@router.post(
    path='/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=(Depends(current_superuser),)
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Только для суперюзеров.
    Создаёт благотворительный проект.
    """
    await check_name_duplicate(
        charity_project.name,
        session
    )
    await charity_project_crud.get_project_by_name(
        CharityProject, charity_project.name, session)

    new_project = await charity_project_crud.create(
        charity_project, session)

    target_objects = await get_not_full_invested_objects(
        Donation, session)
    new_project = new_investing_process(
        new_project, target_objects)

    await session.commit()
    await session.refresh(new_project)

    return new_project


@router.delete(
    path='/{project_id}',
    response_model=CharityProjectDB,
    dependencies=(Depends(current_superuser),)
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Только для суперюзеров.
    Удаляет проект. Нельзя удалить проект, в который уже были инвестированы
     средства, его можно только закрыть.
    """
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    check_charity_project_already_invested(charity_project=charity_project)
    return await charity_project_crud.remove(db_obj=charity_project,
                                             session=session)


@router.patch(
    path='/{project_id}',
    response_model=CharityProjectDB,
    dependencies=(Depends(current_superuser),)
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Только для суперюзеров.
    Закрытый проект нельзя редактировать. Нельзя установить требуемую сумму
     меньше уже вложенной.
    """
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    check_charity_project_closed(charity_project=charity_project)
    if obj_in.name is not None:
        await check_name_duplicate(
            obj_in.name,
            session
        )
    if obj_in.full_amount is not None:
        check_charity_project_invested_sum(
            charity_project,
            obj_in.full_amount
        )
    return await charity_project_crud.update(db_obj=charity_project,
                                             obj_in=obj_in,
                                             session=session)
