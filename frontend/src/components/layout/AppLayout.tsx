import { Box } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { useSSE } from '../../hooks/useSSE';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

export default function AppLayout() {
  useSSE();

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden', bgcolor: 'background.default' }}>
      {/* Sidebar — sticky, full height */}
      <Sidebar />

      {/* Right: TopBar + scrollable content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
        <TopBar />
        <Box component="main" sx={{ flex: 1, overflowY: 'auto', p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
