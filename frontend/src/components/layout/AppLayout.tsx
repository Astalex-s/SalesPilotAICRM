import { useEffect } from 'react';
import { Box, Drawer, useMediaQuery, useTheme } from '@mui/material';
import { Outlet, useLocation } from 'react-router-dom';
import { useSSE } from '../../hooks/useSSE';
import { useUIStore } from '../../store/useUIStore';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

export default function AppLayout() {
  useSSE();

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { mobileSidebarOpen, setMobileSidebarOpen } = useUIStore();
  const { pathname } = useLocation();

  // Close mobile drawer whenever the route changes
  useEffect(() => {
    if (isMobile) setMobileSidebarOpen(false);
  }, [pathname, isMobile, setMobileSidebarOpen]);

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden', bgcolor: 'background.default' }}>

      {/* Desktop — permanent sidebar */}
      {!isMobile && <Sidebar />}

      {/* Mobile — temporary drawer */}
      {isMobile && (
        <Drawer
          open={mobileSidebarOpen}
          onClose={() => setMobileSidebarOpen(false)}
          variant="temporary"
          ModalProps={{ keepMounted: true }}
          PaperProps={{ sx: { width: 220, border: 'none' } }}
        >
          <Sidebar forceExpanded inDrawer />
        </Drawer>
      )}

      {/* Right: TopBar + scrollable content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
        <TopBar />
        <Box component="main" sx={{ flex: 1, overflowY: 'auto', p: { xs: 2, sm: 2.5, md: 3 } }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
