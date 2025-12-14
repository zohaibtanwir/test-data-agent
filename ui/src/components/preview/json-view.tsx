'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface JsonViewProps {
  data: any;
  collapsed?: boolean;
}

export function JsonView({ data, collapsed = false }: JsonViewProps) {
  const [expandedKeys, setExpandedKeys] = useState<Set<string>>(new Set());

  const toggleExpand = (key: string) => {
    const newExpanded = new Set(expandedKeys);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedKeys(newExpanded);
  };

  const renderValue = (value: any, key: string = '', depth: number = 0): React.ReactNode => {
    const indent = depth * 20;
    const fullKey = key;

    if (value === null) {
      return <span className="text-gray-600">null</span>;
    }

    if (typeof value === 'boolean') {
      return <span className="text-purple-600">{value.toString()}</span>;
    }

    if (typeof value === 'number') {
      return <span className="text-blue-600">{value}</span>;
    }

    if (typeof value === 'string') {
      return <span className="text-green-700">"{value}"</span>;
    }

    if (Array.isArray(value)) {
      const isExpanded = !collapsed && expandedKeys.has(fullKey);
      const hasItems = value.length > 0;

      return (
        <div style={{ marginLeft: indent }}>
          {hasItems ? (
            <>
              <Button
                variant="ghost"
                size="sm"
                className="p-0 h-auto hover:bg-transparent"
                onClick={() => toggleExpand(fullKey)}
              >
                {isExpanded ? (
                  <ChevronDown className="h-3 w-3 mr-1" />
                ) : (
                  <ChevronRight className="h-3 w-3 mr-1" />
                )}
                <span className="text-gray-700">[{value.length}]</span>
              </Button>
              {isExpanded && (
                <div className="mt-1">
                  {value.map((item, index) => (
                    <div key={index} className="flex items-start">
                      <span className="text-gray-600 mr-2">{index}:</span>
                      {renderValue(item, `${fullKey}[${index}]`, depth + 1)}
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <span className="text-gray-600">[]</span>
          )}
        </div>
      );
    }

    if (typeof value === 'object') {
      const keys = Object.keys(value);
      const isExpanded = !collapsed && expandedKeys.has(fullKey);
      const hasKeys = keys.length > 0;

      return (
        <div style={{ marginLeft: indent }}>
          {hasKeys ? (
            <>
              <Button
                variant="ghost"
                size="sm"
                className="p-0 h-auto hover:bg-transparent"
                onClick={() => toggleExpand(fullKey)}
              >
                {isExpanded ? (
                  <ChevronDown className="h-3 w-3 mr-1" />
                ) : (
                  <ChevronRight className="h-3 w-3 mr-1" />
                )}
                <span className="text-gray-700">{`{${keys.length}}`}</span>
              </Button>
              {isExpanded && (
                <div className="mt-1">
                  {keys.map((k) => (
                    <div key={k} className="flex items-start">
                      <span className="text-cyan-600 mr-2">"{k}":</span>
                      {renderValue(value[k], `${fullKey}.${k}`, depth + 1)}
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <span className="text-gray-600">{'{}'}</span>
          )}
        </div>
      );
    }

    return <span className="text-gray-600">{JSON.stringify(value)}</span>;
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-sm overflow-auto max-h-[600px]">
      {renderValue(data)}
    </div>
  );
}