import { Outlet } from 'react-router-dom';
import { StudentLayout } from './StudentLayout';

export function StudentLayoutRoute() {
  return (
    <StudentLayout>
      <Outlet />
    </StudentLayout>
  );
} 