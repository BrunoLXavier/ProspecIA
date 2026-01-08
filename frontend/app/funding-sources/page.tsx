/**
 * Funding Sources page (root path)
 */

import { FundingSourceList } from '@/components/features/FundingSourceList';

export default function FundingSourcesPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <FundingSourceList />
    </div>
  );
}
