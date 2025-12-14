'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface TableViewProps {
  data: any;
}

export function TableView({ data }: TableViewProps) {
  // Handle different data formats
  const records = Array.isArray(data) ? data : [data];

  if (records.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No data to display
      </div>
    );
  }

  // Extract all unique keys from all records
  const allKeys = new Set<string>();
  records.forEach(record => {
    if (typeof record === 'object' && record !== null) {
      Object.keys(record).forEach(key => allKeys.add(key));
    }
  });

  const columns = Array.from(allKeys);

  const renderCellValue = (value: any): React.ReactNode => {
    if (value === null || value === undefined) {
      return <span className="text-gray-500">-</span>;
    }

    if (typeof value === 'boolean') {
      return (
        <Badge variant={value ? 'default' : 'secondary'}>
          {value.toString()}
        </Badge>
      );
    }

    if (typeof value === 'object') {
      if (Array.isArray(value)) {
        return (
          <span className="text-xs font-mono">
            [{value.length} items]
          </span>
        );
      }
      return (
        <span className="text-xs font-mono">
          {JSON.stringify(value).substring(0, 50)}...
        </span>
      );
    }

    if (typeof value === 'number') {
      return <span className="font-mono">{value}</span>;
    }

    // String value
    const strValue = String(value);
    if (strValue.length > 50) {
      return (
        <span title={strValue}>
          {strValue.substring(0, 50)}...
        </span>
      );
    }

    return strValue;
  };

  return (
    <div className="rounded-lg border border-gray-800 overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-gray-900 hover:bg-gray-900">
              <TableHead className="text-gray-400 font-semibold">
                #
              </TableHead>
              {columns.map(column => (
                <TableHead key={column} className="text-gray-400 font-semibold">
                  {column}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {records.slice(0, 100).map((record, index) => (
              <TableRow key={index} className="hover:bg-gray-900/50">
                <TableCell className="font-mono text-gray-500">
                  {index + 1}
                </TableCell>
                {columns.map(column => (
                  <TableCell key={column}>
                    {renderCellValue(record[column])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {records.length > 100 && (
        <div className="p-4 text-center text-sm text-gray-500 bg-gray-900">
          Showing first 100 of {records.length} records
        </div>
      )}
    </div>
  );
}