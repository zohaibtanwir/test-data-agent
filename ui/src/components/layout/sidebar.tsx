'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  Database,
  FileJson,
  History,
  Settings,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Code2,
  GitBranch,
  Layers,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const navigation = [
  { name: 'Generator', href: '/', icon: Sparkles },
  { name: 'Schemas', href: '/schemas', icon: Database },
  { name: 'History', href: '/history', icon: History },
  { name: 'Templates', href: '/templates', icon: FileJson },
  { name: 'Documentation', href: '/docs', icon: BookOpen },
  { name: 'Settings', href: '/settings', icon: Settings },
];

const generationPaths = [
  { name: 'Traditional', icon: Code2, color: 'text-info' },
  { name: 'LLM', icon: Sparkles, color: 'text-macys-red' },
  { name: 'RAG', icon: GitBranch, color: 'text-green-600' },
  { name: 'Hybrid', icon: Layers, color: 'text-warning' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        'fixed left-0 top-16 h-[calc(100vh-4rem)] bg-bg-secondary border-r border-border-default transition-all duration-300 z-40',
        isCollapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex flex-col h-full">
        {/* Toggle Button */}
        <div className="flex justify-end p-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hover:bg-bg-tertiary"
          >
            {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 pb-4">
          <TooltipProvider>
            <ul className="space-y-2">
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <li key={item.name}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Link
                          href={item.href}
                          className={cn(
                            'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                            isActive
                              ? 'bg-macys-red/10 text-macys-red'
                              : 'text-macys-gray hover:text-macys-black hover:bg-bg-tertiary'
                          )}
                        >
                          <item.icon size={20} className="flex-shrink-0" />
                          {!isCollapsed && (
                            <span className="text-sm font-medium">{item.name}</span>
                          )}
                        </Link>
                      </TooltipTrigger>
                      {isCollapsed && (
                        <TooltipContent side="right">
                          <p>{item.name}</p>
                        </TooltipContent>
                      )}
                    </Tooltip>
                  </li>
                );
              })}
            </ul>
          </TooltipProvider>
        </nav>

        {/* Generation Paths Indicator */}
        {!isCollapsed && (
          <div className="p-4 border-t border-border-default">
            <h3 className="text-xs font-semibold text-macys-gray uppercase mb-3">
              Generation Paths
            </h3>
            <div className="space-y-2">
              {generationPaths.map((path) => (
                <div key={path.name} className="flex items-center gap-2">
                  <path.icon size={16} className={path.color} />
                  <span className="text-xs text-macys-gray">{path.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}