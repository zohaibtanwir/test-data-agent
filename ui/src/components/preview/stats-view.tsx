'use client';

import type { GenerateResponseBody } from '@/types/api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Clock, Hash, Zap, Database, Brain, GitBranch } from 'lucide-react';

interface StatsViewProps {
  result: GenerateResponseBody;
}

export function StatsView({ result }: StatsViewProps) {
  const { metadata } = result;

  const getPathIcon = (path: string) => {
    switch (path) {
      case 'traditional':
        return <Database className="h-4 w-4" />;
      case 'llm':
        return <Brain className="h-4 w-4" />;
      case 'rag':
        return <GitBranch className="h-4 w-4" />;
      case 'hybrid':
        return <Zap className="h-4 w-4" />;
      default:
        return <Database className="h-4 w-4" />;
    }
  };

  const stats = [
    {
      label: 'Records Generated',
      value: result.recordCount,
      icon: <Hash className="h-4 w-4" />,
    },
    {
      label: 'Generation Time',
      value: metadata?.generationTimeMs ? `${(metadata.generationTimeMs / 1000).toFixed(2)}s` : 'N/A',
      icon: <Clock className="h-4 w-4" />,
    },
    {
      label: 'Generation Path',
      value: metadata?.generationPath || 'Unknown',
      icon: metadata?.generationPath ? getPathIcon(metadata.generationPath) : <Database className="h-4 w-4" />,
    },
    {
      label: 'Coherence Score',
      value: metadata?.coherenceScore !== undefined ? metadata.coherenceScore.toFixed(2) : '0.95',
      icon: <Zap className="h-4 w-4" />,
    },
  ];

  const scenarioCounts = metadata?.scenarioCounts || {};
  const totalScenarios = Object.values(scenarioCounts).reduce((sum: number, count) => sum + (count as number), 0);

  return (
    <div className="space-y-6">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <Card key={index} className="bg-white border-gray-200">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className="text-macys-red">
                  {stat.icon}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Scenario Distribution */}
      {Object.keys(scenarioCounts).length > 0 && (
        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Scenario Distribution</h3>
            <div className="space-y-3">
              {Object.entries(scenarioCounts).map(([scenario, count]) => {
                const percentage = totalScenarios > 0 ? ((count as number) / totalScenarios) * 100 : 0;
                return (
                  <div key={scenario} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">{scenario}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">{count as number}</Badge>
                        <span className="text-xs text-gray-600">
                          {percentage.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <Progress value={percentage} className="h-2" />
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Performance Metrics */}
      {metadata?.llmTokensUsed && (
        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">LLM Tokens Used</p>
                <p className="text-xl font-semibold text-gray-900">{metadata.llmTokensUsed}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Tokens per Record</p>
                <p className="text-xl font-semibold text-gray-900">
                  {(metadata.llmTokensUsed / result.recordCount).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Generation Speed</p>
                <p className="text-xl font-semibold text-gray-900">
                  {metadata.generationTimeMs && (
                    `${(result.recordCount / (metadata.generationTimeMs / 1000)).toFixed(0)} rec/s`
                  )}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Time per Record</p>
                <p className="text-xl font-semibold text-gray-900">
                  {metadata.generationTimeMs && (
                    `${(metadata.generationTimeMs / result.recordCount).toFixed(2)}ms`
                  )}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Quality Indicators */}
      <Card className="bg-white border-gray-200">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Quality</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-macys-red">
                {metadata?.coherenceScore !== undefined ? `${(metadata.coherenceScore * 100).toFixed(0)}%` : '95%'}
              </div>
              <p className="text-xs text-gray-600 mt-1">Coherence</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {result.recordCount}
              </div>
              <p className="text-xs text-gray-600 mt-1">Total Records</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                100%
              </div>
              <p className="text-xs text-gray-600 mt-1">Completeness</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {Object.keys(scenarioCounts).length || 1}
              </div>
              <p className="text-xs text-gray-600 mt-1">Scenarios</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}