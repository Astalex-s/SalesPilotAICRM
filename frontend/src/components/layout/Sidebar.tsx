import DashboardIcon from '@mui/icons-material/Dashboard';
import GroupIcon from '@mui/icons-material/Group';
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
import { useAuthStore } from '../../store/useAuthStore';

const DRAWER_WIDTH = 240;

/** Pipeline ID is a placeholder — replace with dynamic selection in a future step. */
const DEMO_PIPELINE_ID = '00000000-0000-0000-0000-000000000001';

const NAV_ITEMS = [
  { label: 'Дашборд', path: '/', icon: <DashboardIcon /> },
  { label: 'Воронка', path: `/pipeline/${DEMO_PIPELINE_ID}`, icon: <ViewKanbanIcon /> },
  { label: 'Лиды', path: '/leads', icon: <PeopleIcon /> },
  { label: 'Сделки', path: '/deals', icon: <WorkIcon /> },
];

interface SidebarProps {
  open: boolean;
}

export default function Sidebar({ open }: SidebarProps) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const user = useAuthStore((s) => s.user);

  const items = user?.role === 'admin'
    ? [...NAV_ITEMS, { label: 'Пользователи', path: '/users', icon: <GroupIcon /> }]
    : NAV_ITEMS;

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
        {items.map(({ label, path, icon }) => (
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
