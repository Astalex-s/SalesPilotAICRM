"""
Юнит-тесты use case CreateLeadUseCase.
Репозиторий заменён AsyncMock — зависимости от I/O отсутствуют.
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.dtos.lead_dtos import CreateLeadInput, LeadOutput
from src.application.exceptions import LeadEmailAlreadyExistsError
from src.application.use_cases.create_lead import CreateLeadUseCase
from src.domain.value_objects.enums import LeadSource, LeadStatus


# ── Фикстуры ───────────────────────────────────────────────────────────────────

@pytest.fixture
def lead_repo() -> AsyncMock:
    """Мок репозитория лидов."""
    repo = AsyncMock()
    # По умолчанию e-mail не занят
    repo.find_by_email.return_value = None
    # save возвращает сохранённую сущность (контракт BaseRepository)
    repo.save.side_effect = lambda entity: entity
    return repo


@pytest.fixture
def use_case(lead_repo: AsyncMock) -> CreateLeadUseCase:
    return CreateLeadUseCase(lead_repo=lead_repo)


@pytest.fixture
def valid_input() -> CreateLeadInput:
    return CreateLeadInput(
        first_name="Alice",
        last_name="Walker",
        email="alice@corp.com",
        owner_id=uuid4(),
        source=LeadSource.WEBSITE,
        phone="+79991234567",
        company="Corp Ltd",
    )


# ── Успешный путь ───────────────────────────────────────────────────────────────

class TestCreateLeadHappyPath:
    async def test_returns_lead_output(
        self, use_case: CreateLeadUseCase, valid_input: CreateLeadInput
    ) -> None:
        """execute возвращает LeadOutput при корректных данных."""
        result = await use_case.execute(valid_input)
        assert isinstance(result, LeadOutput)

    async def test_output_contains_correct_names(
        self, use_case: CreateLeadUseCase, valid_input: CreateLeadInput
    ) -> None:
        """Имя и фамилия в DTO совпадают со входными данными."""
        result = await use_case.execute(valid_input)
        assert result.first_name == "Alice"
        assert result.last_name == "Walker"

    async def test_output_full_name(
        self, use_case: CreateLeadUseCase, valid_input: CreateLeadInput
    ) -> None:
        """full_name собирается из first_name + last_name."""
        result = await use_case.execute(valid_input)
        assert result.full_name == "Alice Walker"

    async def test_output_status_is_new(
        self, use_case: CreateLeadUseCase, valid_input: CreateLeadInput
    ) -> None:
        """Новый лид создаётся в статусе NEW."""
        result = await use_case.execute(valid_input)
        assert result.status == LeadStatus.NEW

    async def test_output_email_matches(
        self, use_case: CreateLeadUseCase, valid_input: CreateLeadInput
    ) -> None:
        """E-mail в DTO совпадает с входным значением."""
        result = await use_case.execute(valid_input)
        assert result.email == "alice@corp.com"

    async def test_output_owner_id_matches(
        self, use_case: CreateLeadUseCase, valid_input: CreateLeadInput
    ) -> None:
        """owner_id в DTO совпадает со входным значением."""
        result = await use_case.execute(valid_input)
        assert result.owner_id == valid_input.owner_id

    async def test_output_has_uuid(
        self, use_case: CreateLeadUseCase, valid_input: CreateLeadInput
    ) -> None:
        """Возвращаемый лид имеет непустой UUID."""
        result = await use_case.execute(valid_input)
        assert result.id is not None

    async def test_repo_save_called_once(
        self,
        use_case: CreateLeadUseCase,
        valid_input: CreateLeadInput,
        lead_repo: AsyncMock,
    ) -> None:
        """Репозиторий save() вызывается ровно один раз."""
        await use_case.execute(valid_input)
        lead_repo.save.assert_called_once()

    async def test_repo_find_by_email_called(
        self,
        use_case: CreateLeadUseCase,
        valid_input: CreateLeadInput,
        lead_repo: AsyncMock,
    ) -> None:
        """Проверка уникальности e-mail вызывается перед сохранением."""
        await use_case.execute(valid_input)
        lead_repo.find_by_email.assert_called_once_with(valid_input.email)

    async def test_lead_without_phone(
        self, use_case: CreateLeadUseCase, lead_repo: AsyncMock
    ) -> None:
        """Лид может быть создан без телефона."""
        data = CreateLeadInput(
            first_name="Bob",
            last_name="Smith",
            email="bob@example.com",
            owner_id=uuid4(),
        )
        result = await use_case.execute(data)
        assert result.phone is None

    async def test_lead_without_company(
        self, use_case: CreateLeadUseCase, lead_repo: AsyncMock
    ) -> None:
        """Лид может быть создан без компании."""
        data = CreateLeadInput(
            first_name="Bob",
            last_name="Smith",
            email="bob@example.com",
            owner_id=uuid4(),
        )
        result = await use_case.execute(data)
        assert result.company is None


# ── Защитные условия ───────────────────────────────────────────────────────────

class TestCreateLeadGuards:
    async def test_duplicate_email_raises(
        self,
        use_case: CreateLeadUseCase,
        valid_input: CreateLeadInput,
        lead_repo: AsyncMock,
    ) -> None:
        """Повторный e-mail вызывает LeadEmailAlreadyExistsError."""
        # Имитируем: e-mail уже занят
        from src.domain.entities.lead import Lead
        from src.domain.value_objects.email import Email
        existing = Lead.create(
            first_name="Other",
            last_name="User",
            email=Email("alice@corp.com"),
            owner_id=uuid4(),
        )
        lead_repo.find_by_email.return_value = existing

        with pytest.raises(LeadEmailAlreadyExistsError):
            await use_case.execute(valid_input)

    async def test_duplicate_email_does_not_save(
        self,
        use_case: CreateLeadUseCase,
        valid_input: CreateLeadInput,
        lead_repo: AsyncMock,
    ) -> None:
        """При дублирующемся e-mail save() не вызывается."""
        from src.domain.entities.lead import Lead
        from src.domain.value_objects.email import Email
        existing = Lead.create(
            first_name="Other",
            last_name="User",
            email=Email("alice@corp.com"),
            owner_id=uuid4(),
        )
        lead_repo.find_by_email.return_value = existing

        with pytest.raises(LeadEmailAlreadyExistsError):
            await use_case.execute(valid_input)

        lead_repo.save.assert_not_called()
