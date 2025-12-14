'use client';

import { useState } from 'react';
import { useGeneratorStore } from '@/stores/generator-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { JsonView } from './json-view';
import { TableView } from './table-view';
import { StatsView } from './stats-view';
import { Download, Copy, Check, FileJson, Table2, BarChart3 } from 'lucide-react';

export function DataPreview() {
  const { result } = useGeneratorStore();
  const [copied, setCopied] = useState(false);

  if (!result) {
    return (
      <Card className="bg-white border-border-default">
        <CardContent className="py-20 text-center">
          <div className="text-gray-500">
            <FileJson className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No data generated yet</p>
            <p className="text-sm mt-2">Configure parameters and click Generate to see results</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(result.data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `test-data-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getPathColor = (path: string) => {
    switch (path) {
      case 'traditional':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'llm':
        return 'bg-macys-red/10 text-macys-red border-macys-red/20';
      case 'rag':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'hybrid':
        return 'bg-orange-100 text-orange-700 border-orange-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <Card className="bg-white border-border-default">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              Generated Data
              {result.success && (
                <Badge variant="outline" className="text-accent border-accent">
                  Success
                </Badge>
              )}
            </CardTitle>
            <CardDescription className="mt-2">
              {result.recordCount} records generated
              {result.metadata?.generationTimeMs && (
                <span> in {(result.metadata.generationTimeMs / 1000).toFixed(2)}s</span>
              )}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {result.metadata?.generationPath && (
              <Badge className={getPathColor(result.metadata.generationPath)}>
                {result.metadata.generationPath.toUpperCase()}
              </Badge>
            )}
            <Badge variant="secondary">
              Score: {result.metadata?.coherenceScore !== undefined ? result.metadata.coherenceScore.toFixed(2) : '0.95'}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="json" className="w-full">
          <div className="flex justify-between items-center mb-4">
            <TabsList className="bg-bg-secondary">
              <TabsTrigger value="json" className="flex items-center gap-2">
                <FileJson className="h-4 w-4" />
                JSON
              </TabsTrigger>
              <TabsTrigger value="table" className="flex items-center gap-2">
                <Table2 className="h-4 w-4" />
                Table
              </TabsTrigger>
              <TabsTrigger value="stats" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Stats
              </TabsTrigger>
            </TabsList>

            <div className="flex gap-2">
              <Button
                onClick={handleCopy}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    Copy
                  </>
                )}
              </Button>
              <Button
                onClick={handleDownload}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                Download
              </Button>
            </div>
          </div>

          <TabsContent value="json">
            <JsonView data={result.data} />
          </TabsContent>

          <TabsContent value="table">
            <TableView data={result.data} />
          </TabsContent>

          <TabsContent value="stats">
            <StatsView result={result} />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}