import BusinessIcon from '@mui/icons-material/Business';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import SourceIcon from '@mui/icons-material/Source';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  Typography,
} from '@mui/material';
import { type Lead, type LeadStatus } from '../../types/lead';

const STATUS_COLOR: Record<LeadStatus, 'default' | 'info' | 'success' | 'error' | 'warning'> = {
  new: 'info',
  contacted: 'warning',
  qualified: 'success',
  unqualified: 'error',
  converted: 'default',
};

interface InfoRowProps {
  icon: React.ReactNode;
  label: string;
  value: string | null | undefined;
}

function InfoRow({ icon, label, value }: InfoRowProps) {
  if (!value) return null;
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, py: 0.75 }}>
      <Box sx={{ color: 'text.secondary', display: 'flex' }}>{icon}</Box>
      <Box>
        <Typography variant="caption" color="text.secondary" display="block">
          {label}
        </Typography>
        <Typography variant="body2">{value}</Typography>
      </Box>
    </Box>
  );
}

interface LeadInfoCardProps {
  lead: Lead;
}

export default function LeadInfoCard({ lead }: LeadInfoCardProps) {
  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h5" fontWeight={700}>
              {lead.full_name}
            </Typography>
            {lead.company && (
              <Typography variant="body2" color="text.secondary">
                {lead.company}
              </Typography>
            )}
          </Box>
          <Chip
            label={lead.status}
            color={STATUS_COLOR[lead.status]}
            size="medium"
          />
        </Box>

        <Divider sx={{ mb: 1.5 }} />

        {/* Contact details */}
        <Grid container spacing={0}>
          <Grid item xs={12}>
            <InfoRow icon={<EmailIcon fontSize="small" />} label="Email" value={lead.email} />
          </Grid>
          <Grid item xs={12}>
            <InfoRow icon={<PhoneIcon fontSize="small" />} label="Phone" value={lead.phone} />
          </Grid>
          <Grid item xs={12}>
            <InfoRow icon={<BusinessIcon fontSize="small" />} label="Company" value={lead.company} />
          </Grid>
          <Grid item xs={12}>
            <InfoRow icon={<SourceIcon fontSize="small" />} label="Source" value={lead.source} />
          </Grid>
        </Grid>

        {lead.notes && (
          <>
            <Divider sx={{ my: 1.5 }} />
            <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
              Notes
            </Typography>
            <Typography variant="body2">{lead.notes}</Typography>
          </>
        )}

        <Divider sx={{ my: 1.5 }} />
        <Box sx={{ display: 'flex', gap: 3 }}>
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              Created
            </Typography>
            <Typography variant="body2">
              {new Date(lead.created_at).toLocaleDateString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              Updated
            </Typography>
            <Typography variant="body2">
              {new Date(lead.updated_at).toLocaleDateString()}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
