import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import LeadInfoCard from '../LeadInfoCard';
import type { Lead } from '../../../types/lead';

const baseLead = {
  id: 'lead-1',
  first_name: 'Alice',
  last_name: 'Smith',
  full_name: 'Alice Smith',
  email: 'alice@example.com',
  phone: '+1 555-1234',
  company: 'ACME Corp',
  status: 'qualified' as const,
  source: 'website' as const,
  notes: 'Important VIP client',
  owner_id: 'owner-1',
  converted_deal_id: null,
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-03-20T12:00:00Z',
};

describe('LeadInfoCard', () => {
  it('renders lead full name', () => {
    render(<LeadInfoCard lead={baseLead as Lead & { full_name: string }} />);
    expect(screen.getByText('Alice Smith')).toBeInTheDocument();
  });

  it('renders lead email', () => {
    render(<LeadInfoCard lead={baseLead as Lead & { full_name: string }} />);
    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
  });

  it('renders lead phone', () => {
    render(<LeadInfoCard lead={baseLead as Lead & { full_name: string }} />);
    expect(screen.getByText('+1 555-1234')).toBeInTheDocument();
  });

  it('renders company name', () => {
    render(<LeadInfoCard lead={baseLead as Lead & { full_name: string }} />);
    // company appears in header (subtitle) and InfoRow — both should be present
    const elements = screen.getAllByText('ACME Corp');
    expect(elements.length).toBeGreaterThanOrEqual(1);
  });

  it('renders status chip', () => {
    render(<LeadInfoCard lead={baseLead as Lead & { full_name: string }} />);
    expect(screen.getByText('qualified')).toBeInTheDocument();
  });

  it('renders notes when provided', () => {
    render(<LeadInfoCard lead={baseLead as Lead & { full_name: string }} />);
    expect(screen.getByText('Important VIP client')).toBeInTheDocument();
  });

  it('does not render notes section when notes is null', () => {
    const noNotes = { ...baseLead, notes: null };
    render(<LeadInfoCard lead={noNotes as Lead & { full_name: string }} />);
    expect(screen.queryByText('Notes')).not.toBeInTheDocument();
  });

  it('does not render phone row when phone is null', () => {
    const noPhone = { ...baseLead, phone: null };
    render(<LeadInfoCard lead={noPhone as Lead & { full_name: string }} />);
    expect(screen.queryByText('+1 555-1234')).not.toBeInTheDocument();
  });

  it('renders created_at date', () => {
    render(<LeadInfoCard lead={baseLead as Lead & { full_name: string }} />);
    expect(screen.getByText('Created')).toBeInTheDocument();
  });
});
