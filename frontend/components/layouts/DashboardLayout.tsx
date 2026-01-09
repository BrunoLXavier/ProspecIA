/**
 * DashboardLayout - Main Layout for Dashboard and Admin Pages
 * 
 * Provides consistent layout structure with:
 * - Left sidebar navigation with active state
 * - Main content area
 * - Responsive design
 * 
 * @example
 * <DashboardLayout>
 *   <YourPageContent />
 * </DashboardLayout>
 */

'use client';

import { ReactNode } from 'react';
import { MainNavigation } from '@/components/navigation/MainNavigation';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header */}
      <Header />

      <div className="flex flex-1">
        {/* Sidebar Navigation */}
        <MainNavigation />

        {/* Main Content */}
        <main className="flex-1">
          {children}
        </main>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
}
