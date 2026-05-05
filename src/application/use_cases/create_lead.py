"""
CreateLeadUseCase — use case создания нового лида.

Единственная ответственность: провалидировать входные данные, убедиться
в уникальности e-mail и сохранить новый лид в хранилище.
"""
from __future__ import annotations

from src.application.dtos.lead_dtos import CreateLeadInput, LeadOutput
from src.application.exceptions import LeadEmailAlreadyExistsError
from src.domain.entities.lead import Lead
from src.domain.repositories.lead_repository import ILeadRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.phone import Phone


class CreateLeadUseCase:
    """Создаёт нового лида, проверяя уникальность e-mail."""

    def __init__(self, lead_repo: ILeadRepository) -> None:
        # Репозиторий лидов — единственная зависимость
        self._lead_repo = lead_repo

    async def execute(self, data: CreateLeadInput) -> LeadOutput:
        """Выполняет создание лида.

        Последовательность:
        1. Проверяет, что e-mail ещё не занят.
        2. Конструирует доменные value objects Email и Phone.
        3. Создаёт доменную сущность Lead.
        4. Сохраняет лид через репозиторий.
        5. Возвращает DTO с данными нового лида.

        Вызывает:
            LeadEmailAlreadyExistsError: Если лид с таким e-mail уже существует.
            InvalidEmailError: Если формат e-mail некорректен.
            InvalidPhoneError: Если формат телефона некорректен.
        """
        # Шаг 1: проверка уникальности e-mail
        existing = await self._lead_repo.find_by_email(data.email)
        if existing is not None:
            raise LeadEmailAlreadyExistsError(data.email)

        # Шаг 2: построение value objects (выбросят доменное исключение при невалидных данных)
        email = Email(data.email)
        phone = Phone(data.phone) if data.phone else None

        # Шаг 3: создание доменной сущности через фабрику
        lead = Lead.create(
            first_name=data.first_name,
            last_name=data.last_name,
            email=email,
            owner_id=data.owner_id,
            source=data.source,
            phone=phone,
            company=data.company,
        )
        if data.tags:
            lead.update_tags(data.tags)
        if data.category is not None:
            lead.update_category(data.category)

        # Шаг 4: сохранение (репозиторий возвращает актуальное состояние сущности)
        lead = await self._lead_repo.save(lead)

        # Шаг 5: возврат DTO
        return LeadOutput.from_entity(lead)
