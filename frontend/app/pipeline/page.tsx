/**
 * Pipeline page (root path)
 */

import { OpportunitiesPipeline } from '@/components/features/OpportunitiesPipeline';

export default function PipelinePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <OpportunitiesPipeline />
    </div>
  );
}
