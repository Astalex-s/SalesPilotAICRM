import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import StatCard from '../StatCard';

const icon = <span data-testid="test-icon">★</span>;

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard label="Total Leads" value={42} icon={icon} />);
    expect(screen.getByText('Total Leads')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('renders string value', () => {
    render(<StatCard label="Win Rate" value="75%" icon={icon} />);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('renders subtext when provided', () => {
    render(<StatCard label="Revenue" value={1000} icon={icon} subtext="vs last month" />);
    expect(screen.getByText('vs last month')).toBeInTheDocument();
  });

  it('does not render subtext when not provided', () => {
    render(<StatCard label="Revenue" value={1000} icon={icon} />);
    expect(screen.queryByText('vs last month')).not.toBeInTheDocument();
  });

  it('renders skeleton when loading=true', () => {
    render(<StatCard label="Leads" value={0} icon={icon} loading={true} />);
    // Value should not be visible during loading
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('hides subtext when loading', () => {
    render(<StatCard label="Leads" value={10} icon={icon} subtext="subtitle" loading={true} />);
    expect(screen.queryByText('subtitle')).not.toBeInTheDocument();
  });

  it('renders the icon', () => {
    render(<StatCard label="Test" value={1} icon={icon} />);
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });
});
