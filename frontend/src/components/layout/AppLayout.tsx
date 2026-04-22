import { Box, Toolbar } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { useUIStore } from '../../store/useUIStore';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

const DRAWER_WIDTH = 240;

export default function AppLayout() {
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <Box sx={{ display: 'flex' }}>
      <TopBar onMenuClick={toggleSidebar} />
      <Sidebar open={sidebarOpen} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          ml: sidebarOpen ? `${DRAWER_WIDTH}px` : 0,
          transition: (theme) =>
            theme.transitions.create('margin', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
