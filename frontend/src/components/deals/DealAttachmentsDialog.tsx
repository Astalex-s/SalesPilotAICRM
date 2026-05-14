import AttachFileIcon from '@mui/icons-material/AttachFile';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import DownloadIcon from '@mui/icons-material/Download';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import {
  Alert,
  Box,
  CircularProgress,
  Dialog,
  DialogContent,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { attachmentsApi } from '../../api/attachments';
import type { DealAttachment } from '../../types/attachment';

const MAX_SIZE_MB = 10;

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface Props {
  open: boolean;
  onClose: () => void;
  dealId: string;
  dealTitle: string;
}

export default function DealAttachmentsDialog({ open, onClose, dealId, dealTitle }: Props) {
  const { t } = useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [attachments, setAttachments] = useState<DealAttachment[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    if (!open) return;
    setError(null);
    setLoading(true);
    attachmentsApi.list(dealId)
      .then(setAttachments)
      .catch(() => setError(t('attachments.loadError')))
      .finally(() => setLoading(false));
  }, [open, dealId, t]);

  const handleUpload = async (file: File) => {
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(t('attachments.fileTooLarge', { max: MAX_SIZE_MB }));
      return;
    }
    setError(null);
    setUploading(true);
    try {
      const att = await attachmentsApi.upload(dealId, file);
      setAttachments((prev) => [att, ...prev]);
    } catch {
      setError(t('attachments.uploadError'));
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    e.target.value = '';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleUpload(file);
  };

  const handleDelete = async (att: DealAttachment) => {
    setDeletingId(att.id);
    try {
      await attachmentsApi.delete(dealId, att.id);
      setAttachments((prev) => prev.filter((a) => a.id !== att.id));
    } catch {
      setError(t('attachments.deleteError'));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        elevation: 0,
        sx: { borderRadius: '16px', border: '1px solid', borderColor: 'divider', boxShadow: '0 16px 48px rgba(13,33,68,0.14)' },
      }}
    >
      {/* Header */}
      <Box sx={{ px: 3, pt: 3, pb: 2, borderBottom: '1px solid #F3F6FA', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AttachFileIcon sx={{ color: '#00A8E8', fontSize: 20 }} />
          <Box>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 16, fontWeight: 700, color: 'text.primary', lineHeight: 1.2 }}>
              {t('attachments.title')}
            </Typography>
            <Typography sx={{ fontFamily: 'Inter', fontSize: 12, color: '#8FA3B8' }}>
              {dealTitle}
            </Typography>
          </Box>
        </Box>
        <Box onClick={onClose} sx={{ cursor: 'pointer', color: '#8FA3B8', p: '6px', borderRadius: '8px', display: 'flex', '&:hover': { color: '#3E4850', bgcolor: 'action.hover' } }}>
          <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </Box>
      </Box>

      <DialogContent sx={{ p: 3 }}>
        {error && <Alert severity="error" sx={{ mb: 2, borderRadius: '10px' }} onClose={() => setError(null)}>{error}</Alert>}

        {/* Drop zone / upload button */}
        <Box
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !uploading && fileInputRef.current?.click()}
          sx={{
            border: `2px dashed ${dragOver ? '#00A8E8' : '#D1DCE9'}`,
            borderRadius: '12px',
            p: 3,
            mb: 3,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 1,
            cursor: uploading ? 'default' : 'pointer',
            bgcolor: dragOver ? 'rgba(0,168,232,0.04)' : '#FAFBFD',
            transition: 'all 0.15s',
            '&:hover': { borderColor: uploading ? '#D1DCE9' : '#00A8E8', bgcolor: uploading ? '#FAFBFD' : 'rgba(0,168,232,0.04)' },
          }}
        >
          {uploading ? (
            <CircularProgress size={24} sx={{ color: '#00A8E8' }} />
          ) : (
            <UploadFileIcon sx={{ fontSize: 32, color: '#8FA3B8' }} />
          )}
          <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#5E6E82', fontWeight: 500 }}>
            {uploading ? t('attachments.uploading') : t('attachments.dropzone')}
          </Typography>
          <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#B0BEC5' }}>
            {t('attachments.maxSize', { max: MAX_SIZE_MB })}
          </Typography>
          <input ref={fileInputRef} type="file" hidden onChange={handleFileChange} />
        </Box>

        {/* File list */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={24} sx={{ color: '#00A8E8' }} />
          </Box>
        ) : attachments.length === 0 ? (
          <Box sx={{ py: 5, textAlign: 'center' }}>
            <AttachFileIcon sx={{ fontSize: 40, color: '#D1DCE9', mb: 1 }} />
            <Typography sx={{ fontFamily: 'Inter', fontSize: 13, color: '#B0BEC5' }}>
              {t('attachments.empty')}
            </Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {attachments.map((att) => (
              <Box
                key={att.id}
                sx={{
                  display: 'flex', alignItems: 'center', gap: 1.5,
                  p: '10px 12px', borderRadius: '10px',
                  border: '1px solid', borderColor: 'divider', bgcolor: 'background.default',
                  '&:hover': { bgcolor: 'action.hover' },
                }}
              >
                <AttachFileIcon sx={{ fontSize: 18, color: '#8FA3B8', flexShrink: 0 }} />
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 13, fontWeight: 600, color: 'text.primary', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {att.filename}
                  </Typography>
                  <Typography sx={{ fontFamily: 'Inter', fontSize: 11, color: '#8FA3B8' }}>
                    {formatBytes(att.size_bytes)} · {new Date(att.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
                <Tooltip title={t('attachments.download')}>
                  <IconButton
                    component="a"
                    href={attachmentsApi.downloadUrl(dealId, att.id)}
                    download={att.filename}
                    size="small"
                    sx={{ color: '#00A8E8', '&:hover': { bgcolor: 'rgba(0,168,232,0.08)' } }}
                  >
                    <DownloadIcon sx={{ fontSize: 18 }} />
                  </IconButton>
                </Tooltip>
                <Tooltip title={t('attachments.delete')}>
                  <IconButton
                    size="small"
                    disabled={deletingId === att.id}
                    onClick={() => handleDelete(att)}
                    sx={{ color: '#EF4444', '&:hover': { bgcolor: 'rgba(239,68,68,0.08)' } }}
                  >
                    {deletingId === att.id
                      ? <CircularProgress size={16} sx={{ color: '#EF4444' }} />
                      : <DeleteOutlineIcon sx={{ fontSize: 18 }} />
                    }
                  </IconButton>
                </Tooltip>
              </Box>
            ))}
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
}
