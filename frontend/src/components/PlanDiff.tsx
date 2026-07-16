'use client';

interface DiffChange {
  change_type: string;
  entity_type: string;
  reason: string;
  entity_data?: any;
}

interface PlanDiffProps {
  reason: string;
  changes: DiffChange[];
  previousPlan?: any;
  newPlan?: any;
}

export default function PlanDiff({ reason, changes, previousPlan, newPlan }: PlanDiffProps) {
  return (
    <div className="border border-line bg-white">
      {/* Header */}
      <div className="border-b border-line p-4 bg-light-paper">
        <div className="flex items-center gap-3 mb-2">
          <span className="font-mono text-xs text-flag">PLAN REVISION</span>
          <span className="font-mono text-xs text-muted">
            {new Date().toLocaleDateString()}
          </span>
        </div>
        <p className="font-sans text-base">{reason}</p>
      </div>

      {/* Changes summary */}
      <div className="p-4 border-b border-line">
        <h3 className="font-mono text-xs text-muted mb-3">CHANGES</h3>
        <div className="space-y-2">
          {changes.map((change, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <span className={`font-mono text-xs px-2 py-1 ${
                change.change_type === 'add' ? 'bg-signal text-white' :
                change.change_type === 'remove' ? 'bg-flag text-white' :
                change.change_type === 'delay' ? 'bg-orange-500 text-white' :
                'bg-line text-graphite'
              }`}>
                {change.change_type.toUpperCase()}
              </span>
              <div>
                <span className="font-mono text-xs text-muted uppercase">
                  {change.entity_type}
                </span>
                <p className="font-sans text-sm">{change.reason}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Diff view */}
      {(previousPlan || changes.length > 0) && (
        <div className="p-4">
          <h3 className="font-mono text-xs text-muted mb-3">BEFORE → AFTER</h3>
          <div className="font-mono text-xs space-y-1 max-h-64 overflow-y-auto">
            {/* Show removed/delayed items */}
            {changes.filter(c => c.change_type === 'remove' || c.change_type === 'delay').map((change, idx) => (
              <div key={`remove-${idx}`} className="text-flag bg-red-50 p-2 border-l-2 border-flag">
                <span className="mr-2">-</span>
                {change.entity_data?.title || change.reason}
              </div>
            ))}
            
            {/* Show added items */}
            {changes.filter(c => c.change_type === 'add').map((change, idx) => (
              <div key={`add-${idx}`} className="text-signal bg-green-50 p-2 border-l-2 border-signal">
                <span className="mr-2">+</span>
                {change.entity_data?.title || change.reason}
              </div>
            ))}
            
            {changes.length === 0 && (
              <div className="text-muted p-2">
                No specific changes recorded
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="border-t border-line p-4 flex gap-3">
        <button className="px-4 py-2 bg-signal text-white font-mono text-sm hover:bg-opacity-90">
          CONTINUE WITH REVISED PLAN
        </button>
        <button className="px-4 py-2 border border-line text-graphite font-mono text-sm hover:bg-light-paper">
          REVIEW CHANGES
        </button>
      </div>
    </div>
  );
}