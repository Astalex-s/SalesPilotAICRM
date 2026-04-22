import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import ViewKanbanIcon from '@mui/icons-material/ViewKanban';
import WorkIcon from '@mui/icons-material/Work';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';

const DRAWER_WIDTH = 240;

/** Pipeline ID is a placeholder — replace with dynamic selection in a future step. */
const DEMO_PIPELINE_ID = '00000000-0000-0000-0000-000000000001';

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Pipeline', path: `/pipeline/${DEMO_PIPELINE_ID}`, icon: <ViewKanbanIcon /> },
  { label: 'Leads', path: '/leads', icon: <PeopleIcon /> },
  { label: 'Deals', path: '/deals', icon: <WorkIcon /> },
];

interface SidebarProps {
  open: boolean;
}

export default function Sidebar({ open }: SidebarProps) {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar />
      <List disablePadding>
        {NAV_ITEMS.map(({ label, path, icon }) => (
          <ListItem key={path} disablePadding>
            <ListItemButton
              selected={path === '/' ? pathname === '/' : pathname.startsWith(path)}
              onClick={() => navigate(path)}
            >
              <ListItemIcon>{icon}</ListItemIcon>
              <ListItemText primary={label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}
