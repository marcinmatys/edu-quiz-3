import type { ReactNode } from 'react';
import { NavBar } from './NavBar';

interface StudentLayoutProps {
  children: ReactNode;
}

export function StudentLayout({ children }: StudentLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1 container mx-auto p-4">
        {children}
      </main>
    </div>
  );
} 