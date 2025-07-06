import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export function MainLayout() {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <main className="flex-1 overflow-x-hidden">
        <div className="min-h-screen w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
} 