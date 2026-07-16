'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle2, Circle, Clock, Flame, BookOpen, 
  PlayCircle, LayoutDashboard, Target, ArrowRight,
  Bell, FileText, X, Plus, ChevronRight, GraduationCap, Trash2
} from 'lucide-react';
import PlanDiff from '@/components/PlanDiff';
import DebugControls from '@/components/DebugControls';

interface DashboardStats {
  completion_percent: number;
  current_streak_days: number;
  time_spent_min: number;
  time_planned_min: number;
  upcoming_tasks_count: number;
  active_milestones_count: number;
}

interface PlanOverview {
  plan_id: number;
  domain: string;
  target_outcome: string;
  completion_percent: number;
  status: string;
}

interface Milestone {
  id: number;
  order: number;
  title: string;
  status: string;
  tasks: Task[];
}

interface Task {
  id: number;
  title: string;
  task_type: string;
  est_minutes: number | null;
  description?: string;
  status: string;
}

interface Nudge {
  id: number;
  trigger_type: string;
  message: string;
  sent_at: string;
  dismissed: boolean;
}

interface PlanRevision {
  id: number;
  trigger: string;
  diff_summary: any[];
  reason: string;
  created_at: string;
}

const getTaskIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'video': return <PlayCircle className="w-5 h-5 text-blue-400" />;
    case 'reading': return <BookOpen className="w-5 h-5 text-amber-400" />;
    case 'quiz': return <Target className="w-5 h-5 text-purple-400" />;
    default: return <FileText className="w-5 h-5 text-gray-400" />;
  }
};

export default function Dashboard() {
  const [courses, setCourses] = useState<PlanOverview[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [nudges, setNudges] = useState<Nudge[]>([]);
  const [revisions, setRevisions] = useState<PlanRevision[]>([]);
  const [selectedRevision, setSelectedRevision] = useState<PlanRevision | null>(null);
  const [loading, setLoading] = useState(true);

  // 1. Fetch courses overview first
  useEffect(() => {
    fetchCourses();
  }, []);

  // 2. Whenever selectedPlanId changes, fetch specific plan details
  useEffect(() => {
    if (selectedPlanId !== null) {
      fetchDashboardData(selectedPlanId);
    }
  }, [selectedPlanId]);

  const fetchCourses = async () => {
    try {
      const res = await axios.get('http://localhost:8000/plans/overview');
      setCourses(res.data);
      if (res.data.length > 0) {
        setSelectedPlanId(res.data[0].plan_id);
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
      setLoading(false);
    }
  };

  const fetchDashboardData = async (planId: number) => {
    setLoading(true);
    try {
      const query = `?plan_id=${planId}`;
      const [statsRes, milestonesRes, nudgesRes, revisionsRes] = await Promise.all([
        axios.get(`http://localhost:8000/plans/active/dashboard${query}`).catch(() => ({ data: null })),
        axios.get(`http://localhost:8000/plans/active/milestones${query}`).catch(() => ({ data: [] })),
        axios.get(`http://localhost:8000/activity/nudges`).catch(() => ({ data: [] })), // Nudges could be global or plan-specific
        axios.get(`http://localhost:8000/plans/active/revisions${query}`).catch(() => ({ data: [] }))
      ]);
      setStats(statsRes.data);
      setMilestones(milestonesRes.data);
      setNudges(nudgesRes.data.filter((n: Nudge) => !n.dismissed));
      setRevisions(revisionsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkComplete = async (taskId: number) => {
    try {
      await axios.put(`http://localhost:8000/tasks/${taskId}/complete`);
      if (selectedPlanId) {
        fetchDashboardData(selectedPlanId);
      }
    } catch (err) {
      console.error("Failed to complete task", err);
    }
  };

  const handleDeleteCourse = async (planId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this course?')) return;
    
    try {
      await axios.delete(`http://localhost:8000/plans/${planId}`);
      if (selectedPlanId === planId) {
        setSelectedPlanId(null);
        setStats(null);
        setMilestones([]);
      }
      fetchCourses();
    } catch (err) {
      console.error("Failed to delete course", err);
    }
  };

  const dismissNudge = async (nudgeId: number) => {
    try {
      await axios.post(`http://localhost:8000/activity/nudges/${nudgeId}/dismiss`);
      setNudges(nudges.filter(n => n.id !== nudgeId));
    } catch (error) {
      console.error('Error dismissing nudge:', error);
    }
  };

  const handleTaskAction = async (taskId: number, action: 'complete' | 'skip') => {
    try {
      await axios.post('http://localhost:8000/activity/log', {
        task_id: taskId,
        event_type: action === 'complete' ? 'completed' : 'skipped',
        time_spent_min: action === 'complete' ? 30 : 0
      });
      if (selectedPlanId) {
        fetchDashboardData(selectedPlanId);
      }
    } catch (error) {
      console.error('Error logging task action:', error);
    }
  };

  if (loading && courses.length === 0) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="font-mono text-muted-foreground animate-pulse">Loading workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row overflow-hidden relative">
      {/* Background embellishments */}
      <div className="fixed top-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-primary/10 blur-[150px] pointer-events-none" />
      
      {/* Sidebar */}
      <aside className="w-full md:w-80 border-r border-white/10 bg-black/40 backdrop-blur-xl h-screen flex flex-col z-10 shrink-0">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary/20 rounded-lg">
              <LayoutDashboard className="w-5 h-5 text-primary" />
            </div>
            <h1 className="font-semibold text-lg">My Courses</h1>
          </div>

          <div className="space-y-3">
            {courses.map(course => (
              <div
                key={course.plan_id}
                onClick={() => setSelectedPlanId(course.plan_id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setSelectedPlanId(course.plan_id) }}
                className={`w-full text-left p-4 rounded-2xl border transition-all flex flex-col gap-2 relative overflow-hidden group cursor-pointer ${
                  selectedPlanId === course.plan_id 
                    ? 'bg-primary/10 border-primary shadow-[0_0_15px_rgba(16,185,129,0.15)]' 
                    : 'bg-white/5 border-white/5 hover:bg-white/10 hover:border-white/20'
                }`}
              >
                {selectedPlanId === course.plan_id && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                )}
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground truncate pr-4 text-sm">
                    {course.domain}
                  </span>
                  <div className="flex items-center gap-1 shrink-0">
                    <button 
                      onClick={(e) => handleDeleteCourse(course.plan_id, e)}
                      className="p-1.5 rounded-md text-muted-foreground hover:text-red-400 hover:bg-red-400/10 transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                    <ChevronRight className={`w-4 h-4 transition-transform ${selectedPlanId === course.plan_id ? 'text-primary translate-x-1' : 'text-muted-foreground group-hover:translate-x-1'}`} />
                  </div>
                </div>
                <div className="w-full bg-black/40 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="bg-primary h-full rounded-full"
                    style={{ width: `${course.completion_percent}%` }}
                  />
                </div>
              </div>
            ))}
            
            <Link 
              href="/"
              className="w-full text-left p-4 rounded-2xl border border-dashed border-white/20 bg-transparent hover:bg-white/5 transition-all flex items-center justify-center gap-2 text-muted-foreground hover:text-foreground font-medium text-sm mt-4"
            >
              <Plus className="w-4 h-4" /> Add New Course
            </Link>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
          {loading ? (
             <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div></div>
          ) : (
            <div className="space-y-6">
              <h2 className="font-mono text-xs text-muted-foreground mb-4 flex items-center gap-2">
                <Target className="w-3 h-3" /> JOURNEY TIMELINE
              </h2>
              {milestones.length === 0 ? (
                <p className="font-sans text-sm text-muted-foreground text-center py-4">No active milestones.</p>
              ) : (
                milestones.map((milestone, idx) => (
                  <div key={milestone.id} className="relative pl-6">
                    {/* Vertical line connecting milestones */}
                    {idx !== milestones.length - 1 && (
                      <div className="absolute left-[11px] top-6 bottom-[-24px] w-0.5 bg-white/10" />
                    )}
                    {/* Status dot */}
                    <div className={`absolute left-0 top-1 w-6 h-6 rounded-full border-4 border-background flex items-center justify-center ${
                      milestone.status === 'done' ? 'bg-primary' :
                      milestone.status === 'active' ? 'bg-blue-500 ring-2 ring-blue-500/50' :
                      'bg-muted'
                    }`}>
                      {milestone.status === 'done' && <CheckCircle2 className="w-4 h-4 text-background" />}
                    </div>
                    
                    <div className="mb-1 flex items-center justify-between">
                      <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
                        Week {milestone.order}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                        milestone.status === 'done' ? 'bg-primary/20 text-primary' :
                        milestone.status === 'delayed' ? 'bg-destructive/20 text-destructive' :
                        'bg-white/10 text-muted-foreground'
                      }`}>
                        {milestone.status}
                      </span>
                    </div>
                    <h3 className="font-sans font-medium text-foreground">{milestone.title}</h3>
                    <div className="mt-2 w-full bg-white/5 rounded-full h-1.5">
                      <div 
                        className="bg-primary h-1.5 rounded-full transition-all duration-1000"
                        style={{ 
                          width: `${milestone.tasks.length > 0 
                            ? (milestone.tasks.filter(t => t.status === 'completed').length / milestone.tasks.length) * 100 
                            : 0}%` 
                        }}
                      />
                    </div>
                    <p className="font-mono text-xs text-muted-foreground mt-2">
                      {milestone.tasks.filter(t => t.status === 'completed').length} / {milestone.tasks.length} tasks
                    </p>
                  </div>
                ))
              )}
            </div>
          )}
          
          {revisions.length > 0 && !loading && (
            <div className="mt-12 pt-6 border-t border-white/10">
              <h2 className="font-mono text-xs text-muted-foreground mb-4 flex items-center gap-2">
                <FileText className="w-3 h-3" /> PLAN REVISIONS
              </h2>
              <div className="space-y-3">
                {revisions.map((revision, idx) => (
                  <button
                    key={revision.id}
                    onClick={() => setSelectedRevision(revision)}
                    className="w-full text-left p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-primary/50 transition-all group"
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-mono text-xs font-medium text-primary">
                        v{revisions.length - idx}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        {new Date(revision.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="font-sans text-xs text-foreground/80 line-clamp-2 group-hover:text-foreground transition-colors">
                      {revision.reason}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden z-10 relative">
        {loading && courses.length > 0 && (
          <div className="absolute inset-0 z-50 bg-background/50 backdrop-blur-sm flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}
        
        {courses.length === 0 || !selectedPlanId ? (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-1000">
            <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mb-6 border border-primary/20">
              <GraduationCap className="w-12 h-12 text-primary" />
            </div>
            <h2 className="text-3xl font-bold mb-3 tracking-tight">No Active Courses</h2>
            <p className="text-muted-foreground text-lg max-w-md mb-8 leading-relaxed">
              You haven't selected a course or set a learning goal yet. Let's create an adaptive plan to get you started on your journey.
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-all hover:scale-105 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)]"
            >
              Create a Learning Goal <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        ) : (
          <>
            {/* Top Stats Bar */}
            <header className="glass px-8 py-6 border-b border-white/10 shrink-0">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="flex flex-col gap-2">
              <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider">Completion</span>
              <div className="flex items-baseline gap-1">
                <span className="text-4xl font-bold text-foreground leading-none">
                  {stats ? Math.round(stats.completion_percent) : 0}
                </span>
                <span className="text-xl text-muted-foreground font-mono leading-none">%</span>
              </div>
            </div>
            
            <div className="flex flex-col gap-2">
              <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                <Flame className="w-3 h-3 text-orange-500" /> Streak
              </span>
              <div className="flex items-baseline gap-1">
                <span className="text-4xl font-bold text-orange-500 leading-none">
                  {stats ? stats.current_streak_days : 0}
                </span>
                <span className="text-xl text-muted-foreground font-mono leading-none">days</span>
              </div>
            </div>
            
            <div className="flex flex-col gap-2 col-span-2">
              <span className="font-mono text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                <Clock className="w-3 h-3" /> Time Invested
              </span>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex-1">
                  <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-1000"
                      style={{ width: `${stats ? Math.min(100, Math.round((stats.time_spent_min / Math.max(stats.time_planned_min, 1)) * 100)) : 0}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-2 text-xs font-mono text-muted-foreground">
                    <span>{stats?.time_spent_min || 0}m spent</span>
                    <span>{stats?.time_planned_min || 0}m planned</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8 custom-scrollbar">
          <div className="max-w-4xl mx-auto">
            {selectedRevision ? (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-6 rounded-2xl"
              >
                <button
                  onClick={() => setSelectedRevision(null)}
                  className="flex items-center gap-2 mb-6 font-medium text-muted-foreground hover:text-primary transition-colors"
                >
                  <ArrowRight className="w-4 h-4 rotate-180" /> Back to dashboard
                </button>
                <PlanDiff
                  reason={selectedRevision.reason}
                  changes={selectedRevision.diff_summary || []}
                  newPlan={undefined}
                />
              </motion.div>
            ) : (
              <div className="space-y-8">
                {/* Current Course Header */}
                <div className="flex items-center gap-4 mb-8">
                   <div className="w-12 h-12 rounded-2xl bg-primary/20 flex items-center justify-center">
                     <GraduationCap className="w-6 h-6 text-primary" />
                   </div>
                   <div>
                     <h2 className="text-2xl font-bold">{courses.find(c => c.plan_id === selectedPlanId)?.domain || 'Course'}</h2>
                     <p className="text-muted-foreground">{courses.find(c => c.plan_id === selectedPlanId)?.target_outcome || 'Learning Goal'}</p>
                   </div>
                </div>

                {/* Nudges */}
                <AnimatePresence>
                  {nudges.map((nudge) => (
                    <motion.div 
                      key={nudge.id}
                      initial={{ opacity: 0, height: 0, y: -10 }}
                      animate={{ opacity: 1, height: 'auto', y: 0 }}
                      exit={{ opacity: 0, height: 0, scale: 0.95 }}
                      className="glass-card border-l-4 border-l-primary p-4 rounded-r-xl flex items-start gap-4"
                    >
                      <div className="p-2 bg-primary/20 rounded-full mt-1">
                        <Bell className="w-4 h-4 text-primary" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs text-primary uppercase font-bold tracking-wider">
                            {nudge.trigger_type.replace('_', ' ')}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(nudge.sent_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="mt-1 text-foreground/90 font-medium leading-relaxed">{nudge.message}</p>
                      </div>
                      <button 
                        onClick={() => dismissNudge(nudge.id)}
                        className="p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-white/10 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {/* Upcoming Tasks Section */}
                <section>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold">Upcoming Tasks</h2>
                  </div>
                  
                  {milestones.length === 0 || courses.length === 0 || !selectedPlanId ? (
                    <div className="glass-card p-12 rounded-3xl text-center border-dashed border-2 border-white/10">
                      <div className="w-16 h-16 mx-auto bg-white/5 rounded-full flex items-center justify-center mb-4">
                        <Target className="w-8 h-8 text-muted-foreground" />
                      </div>
                      <h3 className="text-lg font-semibold mb-2">No Plan Active</h3>
                      <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                        You haven't set a learning goal yet. Let's create an adaptive plan to get you started on your journey.
                      </p>
                      <Link
                        href="/"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-all"
                      >
                        Create a Goal <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 gap-4">
                      {milestones.flatMap(m => m.tasks)
                        .filter(t => t.status !== 'completed')
                        .slice(0, 5)
                        .map((task, index) => (
                          <motion.div
                            key={task.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="group glass-card p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-primary/50 transition-colors"
                          >
                            <div className="flex items-start sm:items-center gap-4">
                              <div className="p-3 bg-white/5 rounded-xl group-hover:bg-primary/10 transition-colors">
                                {getTaskIcon(task.task_type)}
                              </div>
                              <div>
                                <div className="flex items-center gap-3 mb-1">
                                  <span className="font-mono text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-muted-foreground uppercase tracking-widest font-bold">
                                    {task.task_type}
                                  </span>
                                  <span className="font-mono text-xs text-muted-foreground flex items-center gap-1">
                                    <Clock className="w-3 h-3" /> {task.est_minutes} min
                                  </span>
                                </div>
                                <p className="font-medium text-foreground text-lg group-hover:text-primary transition-colors">{task.title}</p>
                                {task.description && (
                                  <p className="mt-1 text-sm text-muted-foreground leading-relaxed max-w-lg">
                                    {task.description}
                                  </p>
                                )}
                              </div>
                            </div>
                            
                            <div className="flex gap-2 sm:shrink-0 w-full sm:w-auto">
                              <button
                                onClick={() => handleTaskAction(task.id, 'skip')}
                                className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-white/5 text-muted-foreground font-medium hover:bg-white/10 hover:text-foreground transition-all"
                              >
                                Skip
                              </button>
                              <button
                                onClick={() => handleTaskAction(task.id, 'complete')}
                                className="flex-1 sm:flex-none px-6 py-2 rounded-xl bg-primary/20 text-primary font-medium hover:bg-primary hover:text-primary-foreground transition-all flex items-center justify-center gap-2"
                              >
                                <CheckCircle2 className="w-4 h-4" /> Complete
                              </button>
                            </div>
                          </motion.div>
                        ))}
                    </div>
                  )}
                </section>
              </div>
            )}
          </div>
        </div>
      </>
      )}
    </main>
      
      {/* Dev Controls */}
      <div className="absolute bottom-4 right-4 z-50 opacity-20 hover:opacity-100 transition-opacity">
        <DebugControls />
      </div>
    </div>
  );
}