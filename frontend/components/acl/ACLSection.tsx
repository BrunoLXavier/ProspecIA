/**
 * ACLSection - Access Control List Section Component
 * 
 * Renders a section only if the current user has the specified permission.
 * Shows loading skeleton during permission check, hides section if access denied.
 * 
 * Useful for conditionally rendering entire page sections, forms, or panels
 * based on user permissions.
 * 
 * @example
 * <ACLSection resource="clients" action="read">
 *   <ClientDetailsPanel />
 * </ACLSection>
 */

import { ReactNode } from 'react';
import { useACL } from '@/lib/hooks/useACL';

interface ACLSectionProps {
  resource: string;
  action: string;
  children: ReactNode;
  fallback?: ReactNode;
  showSkeleton?: boolean;
  className?: string;
}

export function ACLSection({
  resource,
  action,
  children,
  fallback = null,
  showSkeleton = true,
  className = '',
}: ACLSectionProps) {
  const { allowed, loading } = useACL(resource, action);

  // Show loading skeleton during permission check
  if (loading && showSkeleton) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    );
  }

  // Show fallback or nothing if no permission
  if (!loading && !allowed) {
    return <>{fallback}</>;
  }

  return <div className={className}>{children}</div>;
}
