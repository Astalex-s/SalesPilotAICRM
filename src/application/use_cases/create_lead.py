"""
CreateLeadUseCase — use case создания нового лида.

Единственная ответственность: провалидировать входные данные, убедиться
в уникальности e-mail и сохранить новый лид в хранилище.
"""
from __future__ import annotations

from src.application.dtos.lead_dtos import CreateLeadInput, LeadOutput
from src.application.exceptions import LeadEmailAlreadyExistsError, PipelineNotFoundByNameError
from src.domain.entities.lead import Lead
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.repositories.pipeline_repository import IPipelineRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.phone import Phone


class CreateLeadUseCase:
    """Создаёт нового лида, проверяя уникальность e-mail."""

    def __init__(
        self,
        lead_repo: ILeadRepository,
        pipeline_repo: IPipelineRepository,
    ) -> None:
        self._lead_repo = lead_repo
        self._pipeline_repo = pipeline_repo

    async def execute(self, data: CreateLeadInput) -> LeadOutput:
        """Выполняет создание лида.

        Последовательность:
        1. Проверяет, что e-mail ещё не занят.
        2. Если передано target_pipeline_name — резолвит название воронки в UUID.
        3. Конструирует доменные value objects Email и Phone.
        4. Создаёт доменную сущность Lead.
        5. Сохраняет лид через репозиторий.
        6. Возвращает DTO с данными нового лида.

        Вызывает:
            LeadEmailAlreadyExistsError: Если лид с таким e-mail уже существует.
            PipelineNotFoundByNameError: Если воронка с таким названием не найдена.
            InvalidEmailError: Если формат e-mail некорректен.
            InvalidPhoneError: Если формат телефона некорректен.
        """
        # Шаг 1: проверка уникальности e-mail
        existing = await self._lead_repo.find_by_email(data.email)
        if existing is not None:
            raise LeadEmailAlreadyExistsError(data.email)

        # Шаг 2: резолвинг названия воронки → UUID
        target_pipeline_id = None
        if data.target_pipeline_name:
            pipeline = await self._pipeline_repo.find_by_name(data.target_pipeline_name)
            if pipeline is None:
                raise PipelineNotFoundByNameError(data.target_pipeline_name)
            target_pipeline_id = pipeline.id

        # Шаг 3: построение value objects (выбросят доменное исключение при невалидных данных)
        email = Email(data.email)
        phone = Phone(data.phone) if data.phone else None

        # Шаг 4: создание доменной сущности через фабрику
        lead = Lead.create(
            first_name=data.first_name,
            last_name=data.last_name,
            email=email,
            owner_id=data.owner_id,
            source=data.source,
            phone=phone,
            company=data.company,
            target_pipeline_id=target_pipeline_id,
        )
        if data.tags:
            lead.update_tags(data.tags)
        if data.category is not None:
            lead.update_category(data.category)

        # Шаг 5: сохранение (репозиторий возвращает актуальное состояние сущности)
        lead = await self._lead_repo.save(lead)

        # Шаг 6: возврат DTO
        return LeadOutput.from_entity(lead)
