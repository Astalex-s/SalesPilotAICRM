import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AddDealDialog from '../AddDealDialog';
import { dealsApi } from '../../../api/deals';
import { useLeadStore } from '../../../store/useLeadStore';
import { useAuthStore } from '../../../store/useAuthStore';
import type { Lead } from '../../../types/lead';
import type { Pipeline } from '../../../types/pipeline';
import type { Deal } from '../../../types/deal';

// ── Hoisted mocks (available inside vi.mock factories) ────────────────────────
const mockNavigate = vi.hoisted(() => vi.fn());

// ── Module mocks ──────────────────────────────────────────────────────────────

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en', changeLanguage: vi.fn() },
  }),
}));

vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

vi.mock('../../../api/deals', () => ({
  dealsApi: { create: vi.fn() },
}));

vi.mock('../../../api/ai', () => ({
  aiApi: { scoreLead: vi.fn(), nextBestAction: vi.fn(), generateEmail: vi.fn() },
}));

vi.mock('../../../api/gmail', () => ({
  gmailApi: { sendEmail: vi.fn() },
}));

vi.mock('../../../store/useLeadStore', () => ({
  useLeadStore: vi.fn(),
}));

vi.mock('../../../store/useAuthStore', () => ({
  useAuthStore: vi.fn(),
}));

// ── Fixtures ──────────────────────────────────────────────────────────────────

const mockUser = {
  id: 'user-1', first_name: 'Admin', last_name: 'User',
  email: 'admin@example.com', role: 'admin' as const, is_active: true,
};

const qualifiedLead: Lead = {
  id: 'lead-1', first_name: 'Alice', last_name: 'Smith',
  email: 'alice@example.com', phone: null, company: 'ACME',
  status: 'qualified', source: 'website', notes: null,
  owner_id: 'owner-1', converted_deal_id: null,
  created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z',
};

const newLead: Lead = {
  ...qualifiedLead,
  id: 'lead-2', first_name: 'Bob', last_name: 'Jones',
  status: 'new', company: null,
};

const mockPipeline: Pipeline = {
  id: 'pipeline-1', name: 'Sales Pipeline', owner_id: 'owner-1',
  is_active: true, created_at: '2024-01-01T00:00:00Z',
  stages: [
    { id: 'stage-1', name: 'Qualification', order: 1, probability: 0.3, pipeline_id: 'pipeline-1', color: null },
    { id: 'stage-2', name: 'Proposal', order: 2, probability: 0.6, pipeline_id: 'pipeline-1', color: null },
  ],
};

const mockDeal: Deal = {
  id: 'deal-1', title: 'Alice Smith — ACME', owner_id: 'owner-1',
  stage_id: 'stage-1', pipeline_id: 'pipeline-1',
  value_amount: '0', value_currency: 'USD', status: 'open',
  contact_name: null, company: 'ACME', source_lead_id: 'lead-1',
  expected_close_date: null, closed_at: null,
  created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z',
};

// ── Helpers ───────────────────────────────────────────────────────────────────

const mockFetchLeads = vi.fn();
const mockUpdateLead = vi.fn();

function setupStore(leads: Lead[] = [qualifiedLead, newLead]) {
  vi.mocked(useLeadStore).mockImplementation((selector: any) =>
    selector({ leads, fetchLeads: mockFetchLeads, updateLead: mockUpdateLead }),
  );
  vi.mocked(useAuthStore).mockImplementation((selector: any) =>
    selector({ user: mockUser }),
  );
}

function renderDialog(props: Partial<React.ComponentProps<typeof AddDealDialog>> = {}) {
  const onClose = props.onClose ?? vi.fn();
  const onDealCreated = props.onDealCreated ?? vi.fn();
  return {
    onClose,
    onDealCreated,
    ...render(
      <AddDealDialog
        open={true}
        onClose={onClose}
        pipeline={mockPipeline}
        onDealCreated={onDealCreated}
        {...props}
      />,
    ),
  };
}

/** Opens the Lead combobox and selects the given option text. */
async function selectLead(user: ReturnType<typeof userEvent.setup>, name: string) {
  const comboboxes = screen.getAllByRole('combobox');
  await user.click(comboboxes[0]); // Lead is always first combobox
  const option = await screen.findByRole('option', { name: new RegExp(name, 'i') });
  await user.click(option);
}

/** Navigates from form step to success step by selecting qualified lead and submitting. */
async function reachSuccessStep(user: ReturnType<typeof userEvent.setup>) {
  vi.mocked(dealsApi.create).mockResolvedValueOnce(mockDeal);
  await selectLead(user, 'Alice Smith');
  await user.click(screen.getByText('deals.dialog.submit').closest('button')!);
  // Header + body both show this key when step=success; wait for any match
  await waitFor(() =>
    expect(screen.getAllByText('deals.success.title').length).toBeGreaterThan(0),
  );
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe('AddDealDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupStore();
  });

  // ── Initial render ────────────────────────────────────────────────────────

  describe('initial render', () => {
    it('renders the dialog title', () => {
      renderDialog();
      expect(screen.getByText('deals.dialog.title')).toBeInTheDocument();
    });

    it('renders lead selector label', () => {
      renderDialog();
      // MUI InputLabel renders text in both <label> and animation <span>
      expect(screen.getAllByText('deals.dialog.leadLabel').length).toBeGreaterThan(0);
    });

    it('renders stage selector label', () => {
      renderDialog();
      expect(screen.getAllByText('deals.dialog.stageLabel').length).toBeGreaterThan(0);
    });

    it('renders cancel button', () => {
      renderDialog();
      expect(screen.getByText('deals.dialog.cancel')).toBeInTheDocument();
    });

    it('submit button is disabled when no lead is selected', () => {
      renderDialog();
      const submit = screen.getByText('deals.dialog.submit').closest('button');
      expect(submit).toBeDisabled();
    });
  });

  // ── Leads loading ─────────────────────────────────────────────────────────

  describe('leads loading', () => {
    it('calls fetchLeads when dialog opens with empty leads', () => {
      setupStore([]);
      renderDialog();
      expect(mockFetchLeads).toHaveBeenCalledTimes(1);
    });

    it('does not call fetchLeads when leads are already present', () => {
      setupStore([qualifiedLead]);
      renderDialog();
      expect(mockFetchLeads).not.toHaveBeenCalled();
    });
  });

  // ── Lead selection ────────────────────────────────────────────────────────

  describe('lead selection', () => {
    it('auto-fills title when a lead is selected', async () => {
      const user = userEvent.setup();
      renderDialog();
      await selectLead(user, 'Alice Smith');
      expect(screen.getByDisplayValue('Alice Smith — ACME')).toBeInTheDocument();
    });

    it('shows qualification warning for unqualified lead', async () => {
      const user = userEvent.setup();
      renderDialog();
      await selectLead(user, 'Bob Jones');
      expect(screen.getByText('deals.dialog.notQualifiedWarning')).toBeInTheDocument();
    });

    it('submit is disabled for unqualified lead', async () => {
      const user = userEvent.setup();
      renderDialog();
      await selectLead(user, 'Bob Jones');
      const submit = screen.getByText('deals.dialog.submit').closest('button');
      expect(submit).toBeDisabled();
    });

    it('enables submit button after selecting a qualified lead', async () => {
      const user = userEvent.setup();
      renderDialog();
      await selectLead(user, 'Alice Smith');
      const submit = screen.getByText('deals.dialog.submit').closest('button');
      expect(submit).not.toBeDisabled();
    });
  });

  // ── Qualify lead ──────────────────────────────────────────────────────────

  describe('qualify lead button', () => {
    it('calls updateLead with qualified status when Qualify Lead is clicked', async () => {
      const user = userEvent.setup();
      mockUpdateLead.mockResolvedValueOnce({ ...newLead, status: 'qualified' });
      renderDialog();

      await selectLead(user, 'Bob Jones');
      const qualifyBtn = screen.getByText('deals.dialog.qualifyLead').closest('button');
      await user.click(qualifyBtn!);

      expect(mockUpdateLead).toHaveBeenCalledWith('lead-2', { status: 'qualified' });
    });
  });

  // ── Deal creation ─────────────────────────────────────────────────────────

  describe('deal creation', () => {
    it('calls dealsApi.create with correct payload', async () => {
      const user = userEvent.setup();
      vi.mocked(dealsApi.create).mockResolvedValueOnce(mockDeal);
      renderDialog();

      await selectLead(user, 'Alice Smith');
      await user.click(screen.getByText('deals.dialog.submit').closest('button')!);

      expect(dealsApi.create).toHaveBeenCalledWith(
        expect.objectContaining({
          lead_id: 'lead-1',
          stage_id: 'stage-1',
          pipeline_id: 'pipeline-1',
        }),
      );
    });

    it('transitions to success step after successful creation', async () => {
      const user = userEvent.setup();
      vi.mocked(dealsApi.create).mockResolvedValueOnce(mockDeal);
      renderDialog();

      await selectLead(user, 'Alice Smith');
      await user.click(screen.getByText('deals.dialog.submit').closest('button')!);

      await waitFor(() =>
        expect(screen.getAllByText('deals.success.title').length).toBeGreaterThan(0),
      );
    });

    it('calls onDealCreated with the new deal', async () => {
      const user = userEvent.setup();
      const onDealCreated = vi.fn();
      vi.mocked(dealsApi.create).mockResolvedValueOnce(mockDeal);
      renderDialog({ onDealCreated });

      await selectLead(user, 'Alice Smith');
      await user.click(screen.getByText('deals.dialog.submit').closest('button')!);

      await waitFor(() => expect(onDealCreated).toHaveBeenCalledWith(mockDeal));
    });

    it('shows API error detail on failure', async () => {
      const user = userEvent.setup();
      vi.mocked(dealsApi.create).mockRejectedValueOnce({
        response: { data: { detail: 'Lead already has a deal' } },
      });
      renderDialog();

      await selectLead(user, 'Alice Smith');
      await user.click(screen.getByText('deals.dialog.submit').closest('button')!);

      await waitFor(() =>
        expect(screen.getByText('Lead already has a deal')).toBeInTheDocument(),
      );
    });

    it('shows generic error when API response has no detail', async () => {
      const user = userEvent.setup();
      vi.mocked(dealsApi.create).mockRejectedValueOnce(new Error('Network error'));
      renderDialog();

      await selectLead(user, 'Alice Smith');
      await user.click(screen.getByText('deals.dialog.submit').closest('button')!);

      await waitFor(() =>
        expect(screen.getByText('deals.dialog.error')).toBeInTheDocument(),
      );
    });
  });

  // ── Success step ──────────────────────────────────────────────────────────

  describe('success step', () => {
    it('renders success title', async () => {
      const user = userEvent.setup();
      renderDialog();
      await reachSuccessStep(user);
      // Both header and body display this key; use getAllByText
      expect(screen.getAllByText('deals.success.title').length).toBeGreaterThanOrEqual(2);
    });

    it('shows AI score card', async () => {
      const user = userEvent.setup();
      renderDialog();
      await reachSuccessStep(user);
      expect(screen.getByText('deals.success.aiCard.title')).toBeInTheDocument();
    });

    it('shows email card', async () => {
      const user = userEvent.setup();
      renderDialog();
      await reachSuccessStep(user);
      expect(screen.getByText('deals.success.emailCard.title')).toBeInTheDocument();
    });

    it('shows telegram card', async () => {
      const user = userEvent.setup();
      renderDialog();
      await reachSuccessStep(user);
      expect(screen.getByText('deals.success.telegramCard.title')).toBeInTheDocument();
    });

    it('calls onClose when Done button is clicked', async () => {
      const user = userEvent.setup();
      const onClose = vi.fn();
      renderDialog({ onClose });
      await reachSuccessStep(user);

      await user.click(screen.getByText('deals.success.done').closest('button')!);
      expect(onClose).toHaveBeenCalled();
    });

    it('navigates to pipeline page when View Pipeline is clicked', async () => {
      const user = userEvent.setup();
      renderDialog();
      await reachSuccessStep(user);

      await user.click(screen.getByText('deals.success.viewPipeline').closest('button')!);
      expect(mockNavigate).toHaveBeenCalledWith('/pipeline/pipeline-1');
    });
  });

  // ── Dialog controls ───────────────────────────────────────────────────────

  describe('dialog controls', () => {
    it('calls onClose when Cancel button is clicked', async () => {
      const user = userEvent.setup();
      const onClose = vi.fn();
      renderDialog({ onClose });

      await user.click(screen.getByText('deals.dialog.cancel').closest('button')!);
      expect(onClose).toHaveBeenCalled();
    });
  });

  // ── defaultStageId prop ───────────────────────────────────────────────────

  describe('defaultStageId', () => {
    it('pre-selects the specified stage', async () => {
      renderDialog({ defaultStageId: 'stage-2' });
      // stage-2 "Proposal" should be auto-selected in the stage combobox
      await waitFor(() =>
        expect(screen.getByText('Proposal')).toBeInTheDocument(),
      );
    });
  });
});
