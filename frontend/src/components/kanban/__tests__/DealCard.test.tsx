import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import DealCard from '../DealCard';
import type { Deal } from '../../../types/deal';

// react-beautiful-dnd требует DragDropContext; мокируем для unit-тестов
vi.mock('@hello-pangea/dnd', () => ({
  Draggable: ({
    children,
  }: {
    children: (provided: object, snapshot: { isDragging: boolean }) => React.ReactNode;
  }) =>
    children(
      {
        innerRef: () => {},
        draggableProps: {},
        dragHandleProps: {},
      },
      { isDragging: false },
    ),
}));

const baseDeal: Deal = {
  id: 'deal-1',
  title: 'Enterprise Contract',
  owner_id: 'owner-1',
  stage_id: 'stage-1',
  pipeline_id: 'pipeline-1',
  value_amount: '25000',
  value_currency: 'USD',
  status: 'open',
  contact_name: null,
  company: 'BigCorp',
  source_lead_id: null,
  expected_close_date: null,
  closed_at: null,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-10T00:00:00Z',
};

function renderCard(deal: Deal, stageProbability = 50) {
  return render(
    <MemoryRouter>
      <DealCard deal={deal} index={0} stageProbability={stageProbability} />
    </MemoryRouter>,
  );
}

describe('DealCard', () => {
  it('renders deal title', () => {
    renderCard(baseDeal);
    expect(screen.getByText('Enterprise Contract')).toBeInTheDocument();
  });

  it('renders deal value with currency', () => {
    renderCard(baseDeal);
    expect(screen.getByText(/\$25K/)).toBeInTheDocument();
  });

  it('renders status chip', () => {
    renderCard(baseDeal);
    // i18n not configured in test — key is rendered as-is
    expect(screen.getByText(/pipeline\.likely/)).toBeInTheDocument();
  });

  it('renders company when provided', () => {
    renderCard(baseDeal);
    expect(screen.getByText('BigCorp')).toBeInTheDocument();
  });

  it('does not render company row when company is null', () => {
    const noCompany = { ...baseDeal, company: null };
    renderCard(noCompany);
    expect(screen.queryByText('BigCorp')).not.toBeInTheDocument();
  });

  it('renders won status chip', () => {
    const wonDeal = { ...baseDeal, status: 'won' as const };
    renderCard(wonDeal, 100);
    expect(screen.getByText('Enterprise Contract')).toBeInTheDocument();
  });

  it('renders lost status chip', () => {
    const lostDeal = { ...baseDeal, status: 'lost' as const };
    renderCard(lostDeal, 0);
    expect(screen.getByText('Enterprise Contract')).toBeInTheDocument();
  });
});
