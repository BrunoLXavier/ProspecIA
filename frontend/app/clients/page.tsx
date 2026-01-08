/**
 * Clients page (root path)
 */

import { ClientsList } from '@/components/features/ClientsList';

export default function ClientsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <ClientsList />
    </div>
  );
}
