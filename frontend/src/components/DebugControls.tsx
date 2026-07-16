'use client';

import axios from 'axios';

export default function DebugControls() {
  const simulateInactivity = async () => {
    try {
      await axios.post('http://localhost:8000/activity/check-triggers');
      window.location.reload();
    } catch (error) {
      console.error('Error simulating inactivity:', error);
    }
  };

  const simulateLowScore = async () => {
    try {
      await axios.post('http://localhost:8000/activity/attempts', {
        task_id: 1,
        attempt_type: 'quiz',
        score: 45,
        notes: 'Struggled with VPC concepts'
      });
      window.location.reload();
    } catch (error) {
      console.error('Error simulating low score:', error);
    }
  };

  const simulateEarlyCompletion = async () => {
    try {
      await axios.post('http://localhost:8000/activity/log', {
        task_id: 1,
        event_type: 'completed',
        time_spent_min: 15
      });
      window.location.reload();
    } catch (error) {
      console.error('Error simulating early completion:', error);
    }
  };

  const simulateScheduleSlip = async () => {
    try {
      // Mark a milestone as overdue by updating its date
      await axios.patch('http://localhost:8000/activity/simulate-slip');
      window.location.reload();
    } catch (error) {
      console.error('Error simulating schedule slip:', error);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 bg-black/80 backdrop-blur-md text-foreground p-5 rounded-2xl border border-white/10 shadow-2xl z-50 w-72">
      <h3 className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground mb-4 font-bold flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" /> Debug Controls
      </h3>
      <div className="space-y-2">
        <button
          onClick={simulateInactivity}
          className="block w-full px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/5 text-foreground font-medium text-xs rounded-xl transition-all text-left flex items-center gap-2"
        >
          <span className="text-primary opacity-50">⊕</span> Simulate 3 Days Inactivity
        </button>
        <button
          onClick={simulateLowScore}
          className="block w-full px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/5 text-foreground font-medium text-xs rounded-xl transition-all text-left flex items-center gap-2"
        >
          <span className="text-primary opacity-50">⊕</span> Submit Low Score (45%)
        </button>
        <button
          onClick={simulateScheduleSlip}
          className="block w-full px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/5 text-foreground font-medium text-xs rounded-xl transition-all text-left flex items-center gap-2"
        >
          <span className="text-primary opacity-50">⊕</span> Simulate Schedule Slip
        </button>
        <button
          onClick={simulateEarlyCompletion}
          className="block w-full px-4 py-2.5 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 font-medium text-xs rounded-xl transition-all text-left flex items-center gap-2 mt-4"
        >
          <span className="opacity-70">✓</span> Complete Task Early
        </button>
      </div>
    </div>
  );
}