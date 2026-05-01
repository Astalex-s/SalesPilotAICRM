import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DealCard from '../DealCard';
import type { Deal } from '../../../types/deal';

// react-beautiful-dnd требует DragDropContext; мокируем для unit-тестов
vi.mock('react-beautiful-dnd', () => ({
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

describe('DealCard', () => {
  it('renders deal title', () => {
    render(<DealCard deal={baseDeal} index={0} stageProbability={50} />);
    expect(screen.getByText('Enterprise Contract')).toBeInTheDocument();
  });

  it('renders deal value with currency', () => {
    render(<DealCard deal={baseDeal} index={0} stageProbability={50} />);
    // Value may be locale-formatted; just verify currency is visible
    expect(screen.getByText(/USD/)).toBeInTheDocument();
  });

  it('renders status chip', () => {
    render(<DealCard deal={baseDeal} index={0} stageProbability={50} />);
    expect(screen.getByText('open')).toBeInTheDocument();
  });

  it('renders company when provided', () => {
    render(<DealCard deal={baseDeal} index={0} stageProbability={50} />);
    expect(screen.getByText('BigCorp')).toBeInTheDocument();
  });

  it('does not render company row when company is null', () => {
    const noCompany = { ...baseDeal, company: null };
    render(<DealCard deal={noCompany} index={0} stageProbability={50} />);
    expect(screen.queryByText('BigCorp')).not.toBeInTheDocument();
  });

  it('renders won status chip', () => {
    const wonDeal = { ...baseDeal, status: 'won' as const };
    render(<DealCard deal={wonDeal} index={0} stageProbability={100} />);
    expect(screen.getByText('won')).toBeInTheDocument();
  });

  it('renders lost status chip', () => {
    const lostDeal = { ...baseDeal, status: 'lost' as const };
    render(<DealCard deal={lostDeal} index={0} stageProbability={0} />);
    expect(screen.getByText('lost')).toBeInTheDocument();
  });
});
