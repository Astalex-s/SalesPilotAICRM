import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeadStore } from '../store/useLeadStore';
import { type LeadStatus } from '../types/lead';

const STATUS_COLOR: Record<LeadStatus, 'default' | 'info' | 'success' | 'error' | 'warning'> = {
  new: 'info',
  contacted: 'warning',
  qualified: 'success',
  unqualified: 'error',
  converted: 'default',
};

export default function LeadsPage() {
  const { leads, loading, error, fetchLeads } = useLeadStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">Leads</Typography>
        <Button variant="contained" disabled>
          + New Lead
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Company</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {leads.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No leads found.
                  </TableCell>
                </TableRow>
              ) : (
                leads.map((lead) => (
                  <TableRow
                    key={lead.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/leads/${lead.id}`)}
                  >
                    <TableCell>{`${lead.first_name} ${lead.last_name}`}</TableCell>
                    <TableCell>{lead.email}</TableCell>
                    <TableCell>{lead.company ?? '—'}</TableCell>
                    <TableCell>{lead.source}</TableCell>
                    <TableCell>
                      <Chip
                        label={lead.status}
                        color={STATUS_COLOR[lead.status]}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(lead.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
