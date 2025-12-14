'use client';

import { GeneratorForm } from '@/components/generator/generator-form';
import { DataPreview } from '@/components/preview/data-preview';

export default function Home() {
  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Test Data Generator</h1>
        <p className="text-gray-400">
          Generate realistic test data using AI-powered generation paths
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GeneratorForm />
        <DataPreview />
      </div>
    </div>
  );
}