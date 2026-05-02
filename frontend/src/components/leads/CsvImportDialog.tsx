import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogContent,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { leadsApi } from '../../api/leads';
import { type BulkImportResult } from '../../types/lead';

/* ── CSV template ── */
const CSV_TEMPLATE = `first_name,last_name,email,phone,company,source
John,Doe,john.doe@example.com,+1234567890,Acme Corp,website
Jane,Smith,jane.smith@example.com,,Globex,referral`;

function downloadTemplate() {
  const blob = new Blob([CSV_TEMPLATE], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'leads_template.csv';
  a.click();
  URL.revokeObjectURL(url);
}

/* ── Parse CSV preview (first N rows) ── */
interface PreviewRow {
  [key: string]: string;
}

function parseCsvPreview(text: string, maxRows = 5): { headers: string[]; rows: PreviewRow[] } {
  const lines = text.split(/\r?\n/).filter((l) => l.trim());
  if (lines.length === 0) return { headers: [], rows: [] };
  const headers = lines[0].split(',').map((h) => h.trim().replace(/^"|"$/g, ''));
  const rows = lines.slice(1, maxRows + 1).map((line) => {
    const values = line.split(',').map((v) => v.trim().replace(/^"|"$/g, ''));
    return Object.fromEntries(headers.map((h, i) => [h, values[i] ?? '']));
  });
  return { headers, rows };
}

/* ── Result screen ── */
function ResultScreen({ result, onDone }: { result: BulkImportResult; onDone: () => void }) {
  const { t } = useTranslation();
  return (
    <Box sx={{ textAlign: 'center' }}>
      {/* Icon */}
      <Box sx={{
        width: 52, height: 52, borderRadius: '50%',
        bgcolor: result.created > 0 ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)',
        mx: 'auto', mb: 2,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
          stroke={result.created > 0 ? '#059669' : '#D97706'}
          strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20 6L9 17l-5-5" />
        </svg>
      </Box>

      <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 18, color: '#0D2144', mb: 2 }}>
        {t('leads.csvImport.resultTitle')}
      </Typography>

      {/* Stats */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 3, flexWrap: 'wrap' }}>
        <Box sx={{ px: 2.5, py: 1.5, borderRadius: '12px', bgcolor: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)' }}>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 22, fontWeight: 800, color: '#059669' }}>
            {result.created}
          </Typography>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#059669' }}>
            {t('leads.csvImport.created')}
          </Typography>
        </Box>
        {result.skipped > 0 && (
          <Box sx={{ px: 2.5, py: 1.5, borderRadius: '12px', bgcolor: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)' }}>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 22, fontWeight: 800, color: '#D97706' }}>
              {result.skipped}
            </Typography>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#D97706' }}>
              {t('leads.csvImport.skipped')}
            </Typography>
          </Box>
        )}
        {result.error_count > 0 && (
          <Box sx={{ px: 2.5, py: 1.5, borderRadius: '12px', bgcolor: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 22, fontWeight: 800, color: '#DC2626' }}>
              {result.error_count}
            </Typography>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#DC2626' }}>
              {t('leads.csvImport.errorsCount')}
            </Typography>
          </Box>
        )}
      </Box>

      {/* Error details */}
      {result.errors.length > 0 && (
        <Box sx={{ textAlign: 'left', mb: 2.5, maxHeight: 120, overflowY: 'auto' }}>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 12, fontWeight: 600, color: '#DC2626', mb: 0.5 }}>
            {t('leads.csvImport.errorList')}
          </Typography>
          {result.errors.map((err, i) => (
            <Typography key={i} sx={{ fontFamily: 'Inter', fontSize: 11, color: '#DC2626', lineHeight: 1.6 }}>
              • {err}
            </Typography>
          ))}
        </Box>
      )}

      <Button
        variant="contained"
        onClick={onDone}
        sx={{
          bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
          fontSize: 13, borderRadius: '10px', textTransform: 'none', boxShadow: 'none',
          '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
        }}
      >
        {t('leads.csvImport.done')}
      </Button>
    </Box>
  );
}

/* ── Main dialog ── */
interface CsvImportDialogProps {
  open: boolean;
  onClose: () => void;
  onImported: () => void;
}

export default function CsvImportDialog({ open, onClose, onImported }: CsvImportDialogProps) {
  const { t } = useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [previewHeaders, setPreviewHeaders] = useState<string[]>([]);
  const [previewRows, setPreviewRows] = useState<PreviewRow[]>([]);
  const [totalRows, setTotalRows] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BulkImportResult | null>(null);

  const handleFileChange = (f: File | null) => {
    if (!f) return;
    setFile(f);
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const { headers, rows } = parseCsvPreview(text);
      setPreviewHeaders(headers);
      setPreviewRows(rows);
      const lines = text.split(/\r?\n/).filter((l) => l.trim());
      setTotalRows(Math.max(0, lines.length - 1));
    };
    reader.readAsText(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f?.name.endsWith('.csv')) handleFileChange(f);
  };

  const handleSubmit = async () => {
    if (!file) { setError(t('leads.csvImport.noFile')); return; }
    setSubmitting(true);
    setError(null);
    try {
      const res = await leadsApi.bulkImport(file);
      setResult(res);
      onImported();
    } catch {
      setError(t('leads.csvImport.importError'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (submitting) return;
    setFile(null);
    setPreviewHeaders([]);
    setPreviewRows([]);
    setTotalRows(0);
    setError(null);
    setResult(null);
    onClose();
  };

  const hasRequiredCols = previewHeaders.includes('first_name') &&
    previewHeaders.includes('last_name') &&
    previewHeaders.includes('email');

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{ sx: { borderRadius: '16px', boxShadow: '0 8px 40px rgba(13,33,68,0.12)', overflow: 'hidden' } }}
    >
      {/* Header */}
      <Box sx={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        px: 3, py: 2, borderBottom: '1px solid #E8EFF7',
      }}>
        <Typography sx={{ fontFamily: 'Inter', fontWeight: 700, fontSize: 16, color: '#0D2144' }}>
          {t('leads.csvImport.title')}
        </Typography>
        <Box onClick={handleClose} sx={{ cursor: 'pointer', color: '#94A3B8', display: 'flex', '&:hover': { color: '#0D2144' } }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 6L6 18 M6 6l12 12" />
          </svg>
        </Box>
      </Box>

      <DialogContent sx={{ p: 3 }}>
        {result ? (
          <ResultScreen result={result} onDone={handleClose} />
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
            {/* Dropzone */}
            <Box
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileInputRef.current?.click()}
              sx={{
                border: `2px dashed ${file ? '#00A8E8' : '#D8E5F4'}`,
                borderRadius: '12px',
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                bgcolor: file ? 'rgba(0,168,232,0.03)' : 'transparent',
                transition: 'all 0.15s ease',
                '&:hover': { border: '2px dashed #00A8E8', bgcolor: 'rgba(0,168,232,0.03)' },
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                style={{ display: 'none' }}
                onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
              />
              <Box sx={{ mb: 1, color: file ? '#00A8E8' : '#C4D4E8', display: 'flex', justifyContent: 'center' }}>
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </Box>
              {file ? (
                <Typography sx={{ fontFamily: 'Inter', fontSize: 14, fontWeight: 600, color: '#00A8E8' }}>
                  {file.name} ({totalRows} {t('leads.csvImport.rows')})
                </Typography>
              ) : (
                <>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 14, fontWeight: 600, color: '#0D2144', mb: 0.5 }}>
                    {t('leads.csvImport.dropzone')}
                  </Typography>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#94A3B8' }}>
                    {t('leads.csvImport.supported')}
                  </Typography>
                </>
              )}
            </Box>

            {/* Column validation warning */}
            {file && !hasRequiredCols && (
              <Alert severity="warning" sx={{ borderRadius: '8px', '& .MuiAlert-message': { fontFamily: 'Inter', fontSize: 12 } }}>
                {t('leads.csvImport.parseError')}
              </Alert>
            )}

            {/* Preview table */}
            {previewRows.length > 0 && hasRequiredCols && (
              <Box>
                <Typography sx={{ fontFamily: 'Inter', fontSize: 12, fontWeight: 600, color: '#4B6080', mb: 1 }}>
                  {t('leads.csvImport.preview', { count: previewRows.length })}
                </Typography>
                <Box sx={{ overflowX: 'auto', border: '1px solid #E8EFF7', borderRadius: '8px' }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#F7F9FC' }}>
                        {previewHeaders.map((h) => (
                          <TableCell key={h} sx={{ fontFamily: 'Inter', fontSize: 11, fontWeight: 700, color: '#4B6080', py: 1 }}>
                            {h}
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {previewRows.map((row, i) => (
                        <TableRow key={i} sx={{ '&:last-child td': { borderBottom: 0 } }}>
                          {previewHeaders.map((h) => (
                            <TableCell key={h} sx={{ fontFamily: 'Inter', fontSize: 12, color: '#0D2144', py: 0.75 }}>
                              {row[h] || '—'}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Box>
                {totalRows > 5 && (
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#94A3B8', mt: 0.5 }}>
                    {t('leads.csvImport.moreRows', { count: totalRows - 5 })}
                  </Typography>
                )}
              </Box>
            )}

            {error && (
              <Alert severity="error" sx={{ borderRadius: '8px', '& .MuiAlert-message': { fontFamily: 'Inter', fontSize: 12 } }}>
                {error}
              </Alert>
            )}

            {/* Actions */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pt: 0.5 }}>
              <Button
                variant="text"
                onClick={downloadTemplate}
                sx={{
                  fontFamily: 'Inter', fontSize: 12, fontWeight: 600, textTransform: 'none',
                  color: '#00A8E8', p: 0,
                  '&:hover': { bgcolor: 'transparent', textDecoration: 'underline' },
                }}
              >
                {t('leads.csvImport.downloadTemplate')}
              </Button>

              <Box sx={{ display: 'flex', gap: 1.5 }}>
                <Button
                  variant="outlined"
                  onClick={handleClose}
                  disabled={submitting}
                  sx={{
                    fontFamily: 'Inter', fontSize: 13, fontWeight: 500, textTransform: 'none',
                    borderColor: '#E8EFF7', color: '#64748B', borderRadius: '10px',
                    '&:hover': { borderColor: '#CBD5E8', bgcolor: 'transparent' },
                  }}
                >
                  {t('leads.csvImport.cancel')}
                </Button>
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={!file || !hasRequiredCols || submitting}
                  sx={{
                    bgcolor: '#00A8E8', color: '#fff', fontFamily: 'Inter', fontWeight: 600,
                    fontSize: 13, borderRadius: '10px', textTransform: 'none', boxShadow: 'none',
                    minWidth: 160,
                    '&:hover': { bgcolor: '#0090CC', boxShadow: 'none' },
                    '&.Mui-disabled': { bgcolor: '#CBD5E8', color: '#fff' },
                  }}
                >
                  {submitting
                    ? <><CircularProgress size={14} sx={{ color: '#fff', mr: 1 }} />{t('leads.csvImport.importing')}</>
                    : t('leads.csvImport.importBtn', { count: totalRows })
                  }
                </Button>
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
}
