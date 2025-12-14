'use client';

import { useState } from 'react';
import { useGeneratorStore } from '@/stores/generator-store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Plus, Trash2 } from 'lucide-react';
import type { Scenario } from '@/types/api';

export function ScenarioManager() {
  const { scenarios, addScenario, removeScenario, updateScenario } = useGeneratorStore();
  const [newScenario, setNewScenario] = useState<Partial<Scenario>>({
    name: '',
    description: '',
    weight: 1,
  });

  const totalWeight = scenarios.reduce((sum, s) => sum + s.weight, 0);

  const handleAddScenario = () => {
    if (newScenario.name && newScenario.description) {
      addScenario({
        name: newScenario.name,
        description: newScenario.description,
        weight: newScenario.weight || 1,
      });
      setNewScenario({ name: '', description: '', weight: 1 });
    }
  };

  return (
    <div className="space-y-4">
      {/* Add New Scenario */}
      <Card className="p-4 bg-gray-900 border-gray-800">
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="scenario-name">Scenario Name</Label>
              <Input
                id="scenario-name"
                value={newScenario.name || ''}
                onChange={(e) => setNewScenario({ ...newScenario, name: e.target.value })}
                placeholder="e.g., Holiday Sale"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="scenario-weight">Weight</Label>
              <div className="flex items-center gap-2">
                <Slider
                  id="scenario-weight"
                  min={1}
                  max={10}
                  step={1}
                  value={[newScenario.weight || 1]}
                  onValueChange={([value]) => setNewScenario({ ...newScenario, weight: value })}
                  className="flex-1"
                />
                <Badge variant="secondary" className="min-w-[2rem] text-center">
                  {newScenario.weight || 1}
                </Badge>
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="scenario-description">Description</Label>
            <Input
              id="scenario-description"
              value={newScenario.description || ''}
              onChange={(e) => setNewScenario({ ...newScenario, description: e.target.value })}
              placeholder="Describe the scenario characteristics..."
            />
          </div>
          <Button
            onClick={handleAddScenario}
            disabled={!newScenario.name || !newScenario.description}
            size="sm"
            className="w-full"
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Scenario
          </Button>
        </div>
      </Card>

      {/* Existing Scenarios */}
      {scenarios.length > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <Label>Active Scenarios</Label>
            {totalWeight > 0 && (
              <Badge variant="outline">Total Weight: {totalWeight}</Badge>
            )}
          </div>
          <div className="space-y-2">
            {scenarios.map((scenario, index) => (
              <Card key={index} className="p-3 bg-gray-900 border-gray-800">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{scenario.name}</span>
                      <Badge variant="secondary">
                        {Math.round((scenario.weight / totalWeight) * 100)}%
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">{scenario.description}</p>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <Slider
                      min={1}
                      max={10}
                      step={1}
                      value={[scenario.weight]}
                      onValueChange={([value]) => updateScenario(index, { weight: value })}
                      className="w-24"
                    />
                    <Badge variant="outline" className="min-w-[2rem] text-center">
                      {scenario.weight}
                    </Badge>
                    <Button
                      onClick={() => removeScenario(index)}
                      size="icon"
                      variant="ghost"
                      className="text-red-500 hover:text-red-400"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {scenarios.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No scenarios defined</p>
          <p className="text-sm mt-1">Add scenarios to generate varied test data</p>
        </div>
      )}
    </div>
  );
}