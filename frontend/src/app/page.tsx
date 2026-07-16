'use client';

import { useState } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, ArrowRight, BrainCircuit, Target, Clock, 
  AlertCircle, ChevronLeft, ChevronRight, BookOpen, 
  TrendingUp, Award, Calendar, Timer
} from 'lucide-react';

interface ParsedIntent {
  domain: string;
  current_skill_level: string;
  target_outcome: string;
  timeline_weeks: number;
  constraints: string[];
}

interface Goal {
  id: number;
  raw_input: string;
  domain: string | null;
  current_level: string | null;
  target_outcome: string | null;
  status: string;
  created_at: string;
}

export default function Home() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    topic: '',
    outcome: '',
    level: 'beginner',
    timeline_weeks: 8,
    hours_per_week: 10
  });

  const [parsedIntent, setParsedIntent] = useState<ParsedIntent | null>(null);
  const [goal, setGoal] = useState<Goal | null>(null);
  const [loading, setLoading] = useState(false);
  const [showIntent, setShowIntent] = useState(false);

  const handleNext = () => setStep(s => Math.min(s + 1, 3));
  const handlePrev = () => setStep(s => Math.max(s - 1, 1));

  const handleSubmit = async () => {
    setLoading(true);
    
    // Construct rich natural language prompt for the LLM
    const constructedInput = `I want to learn ${formData.topic}. My ultimate goal is: ${formData.outcome}. My current experience level is ${formData.level}. I want to complete this in ${formData.timeline_weeks} weeks, and I can dedicate ${formData.hours_per_week} hours per week.`;

    try {
      const response = await axios.post('http://localhost:8000/goals/', {
        raw_input: constructedInput
      });
      setGoal(response.data);
      if (response.data.domain) {
        setParsedIntent({
          domain: response.data.domain,
          current_skill_level: response.data.current_level || formData.level,
          target_outcome: response.data.target_outcome || formData.outcome,
          timeline_weeks: formData.timeline_weeks,
          constraints: [`${formData.hours_per_week} hours/week`]
        });
        setShowIntent(true);
      }
    } catch (error) {
      console.error('Error creating goal:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    if (!goal) return;
    
    setLoading(true);
    try {
      await axios.post('http://localhost:8000/plans/', {
        goal_id: goal.id
      });
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Error generating plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const isStep1Valid = formData.topic.trim().length > 0 && formData.outcome.trim().length > 0;

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col items-center justify-center p-6">
      
      {/* Background gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="w-full max-w-3xl z-10"
      >
        <header className="mb-12 text-center">
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center justify-center p-3 mb-6 rounded-2xl glass"
          >
            <BrainCircuit className="w-8 h-8 text-primary" />
          </motion.div>
          <h1 className="text-4xl md:text-6xl font-bold mb-4 tracking-tight text-foreground">
            Master anything, <span className="text-primary">faster.</span>
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-xl mx-auto font-sans">
            Tell us what you want to learn. Our AI agent will build a highly adaptive, personalized plan just for you.
          </p>
        </header>

        <main>
          <AnimatePresence mode="wait">
            {!showIntent && !goal ? (
              <motion.div 
                key="wizard-form"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="glass-card p-6 md:p-8 rounded-3xl relative overflow-hidden"
              >
                {/* Progress Bar */}
                <div className="absolute top-0 left-0 w-full h-1 bg-white/5">
                  <div 
                    className="h-full bg-primary transition-all duration-500" 
                    style={{ width: `${(step / 3) * 100}%` }}
                  />
                </div>

                <div className="mb-8 mt-2 flex items-center justify-between">
                  <span className="font-mono text-xs text-primary uppercase tracking-wider font-semibold">
                    Step {step} of 3
                  </span>
                  <div className="flex gap-1">
                    {[1, 2, 3].map(s => (
                      <div key={s} className={`w-2 h-2 rounded-full ${step >= s ? 'bg-primary' : 'bg-white/10'}`} />
                    ))}
                  </div>
                </div>

                {/* Step 1: Topic & Outcome */}
                {step === 1 && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-6"
                  >
                    <div>
                      <label className="flex items-center gap-2 font-mono text-sm text-foreground mb-3 font-semibold">
                        <BookOpen className="w-4 h-4 text-primary" />
                        What do you want to learn?
                      </label>
                      <input
                        type="text"
                        className="w-full px-5 py-4 bg-black/40 border border-white/10 rounded-2xl focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all font-sans text-foreground placeholder:text-muted-foreground text-lg"
                        placeholder="e.g., Python Programming, Graphic Design, Calculus"
                        value={formData.topic}
                        onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="flex items-center gap-2 font-mono text-sm text-foreground mb-3 font-semibold">
                        <Target className="w-4 h-4 text-primary" />
                        What is your ultimate goal?
                      </label>
                      <textarea
                        rows={3}
                        className="w-full px-5 py-4 bg-black/40 border border-white/10 rounded-2xl focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all font-sans text-foreground placeholder:text-muted-foreground text-lg resize-none"
                        placeholder="e.g., Build my own startup web app, Pass an exam, Get a job"
                        value={formData.outcome}
                        onChange={(e) => setFormData({ ...formData, outcome: e.target.value })}
                      />
                    </div>
                  </motion.div>
                )}

                {/* Step 2: Experience Level */}
                {step === 2 && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <label className="flex items-center gap-2 font-mono text-sm text-foreground mb-6 font-semibold">
                      <TrendingUp className="w-4 h-4 text-primary" />
                      What is your current experience level?
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {[
                        { id: 'beginner', title: 'Beginner', desc: 'Starting from scratch' },
                        { id: 'intermediate', title: 'Intermediate', desc: 'Have some basic knowledge' },
                        { id: 'advanced', title: 'Advanced', desc: 'Looking to master complex concepts' }
                      ].map((lvl) => (
                        <button
                          key={lvl.id}
                          onClick={() => setFormData({ ...formData, level: lvl.id })}
                          className={`p-5 rounded-2xl border text-left transition-all ${
                            formData.level === lvl.id 
                              ? 'bg-primary/10 border-primary text-primary' 
                              : 'bg-black/40 border-white/10 text-muted-foreground hover:border-white/30 hover:bg-white/5'
                          }`}
                        >
                          <h3 className={`font-bold mb-1 ${formData.level === lvl.id ? 'text-foreground' : 'text-foreground'}`}>{lvl.title}</h3>
                          <p className="text-xs font-mono opacity-80">{lvl.desc}</p>
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* Step 3: Time Commitment */}
                {step === 3 && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-8"
                  >
                    <div>
                      <label className="flex justify-between font-mono text-sm text-foreground mb-3 font-semibold">
                        <span className="flex items-center gap-2"><Calendar className="w-4 h-4 text-primary" /> Timeline</span>
                        <span className="text-primary">{formData.timeline_weeks} Weeks</span>
                      </label>
                      <input 
                        type="range" 
                        min="1" max="52" 
                        value={formData.timeline_weeks} 
                        onChange={(e) => setFormData({ ...formData, timeline_weeks: parseInt(e.target.value) })}
                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-primary"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground mt-2 font-mono">
                        <span>1 Week</span>
                        <span>1 Year</span>
                      </div>
                    </div>
                    <div>
                      <label className="flex justify-between font-mono text-sm text-foreground mb-3 font-semibold">
                        <span className="flex items-center gap-2"><Timer className="w-4 h-4 text-primary" /> Commitment</span>
                        <span className="text-primary">{formData.hours_per_week} Hrs / Week</span>
                      </label>
                      <input 
                        type="range" 
                        min="1" max="40" 
                        value={formData.hours_per_week} 
                        onChange={(e) => setFormData({ ...formData, hours_per_week: parseInt(e.target.value) })}
                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-primary"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground mt-2 font-mono">
                        <span>1 Hour</span>
                        <span>40 Hours</span>
                      </div>
                    </div>
                  </motion.div>
                )}

                {loading && (
                  <div className="absolute inset-0 z-50 bg-background/50 backdrop-blur-sm rounded-3xl flex flex-col items-center justify-center gap-4">
                    <Sparkles className="w-8 h-8 text-primary animate-pulse" />
                    <p className="font-mono text-sm text-primary uppercase tracking-widest font-bold animate-pulse">Analyzing...</p>
                  </div>
                )}

                {/* Navigation Buttons */}
                <div className="mt-8 pt-6 border-t border-white/10 flex justify-between">
                  <button
                    onClick={handlePrev}
                    disabled={step === 1 || loading}
                    className={`flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all ${
                      step === 1 ? 'opacity-0 cursor-default' : 'text-muted-foreground hover:bg-white/5 hover:text-foreground border border-white/10'
                    }`}
                  >
                    <ChevronLeft className="w-4 h-4" /> Back
                  </button>
                  
                  {step < 3 ? (
                    <button
                      onClick={handleNext}
                      disabled={!isStep1Valid}
                      className="group flex items-center gap-2 px-6 py-3 bg-white/10 text-foreground border border-white/10 rounded-full font-medium hover:bg-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next Step
                      <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmit}
                      disabled={loading}
                      className="group flex items-center gap-2 px-8 py-3 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Analyze Goal
                      <Sparkles className="w-4 h-4 group-hover:rotate-12 transition-transform" />
                    </button>
                  )}
                </div>
              </motion.div>
            ) : null}

            {showIntent && parsedIntent && (
              <motion.div 
                key="parsed-intent"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-6 md:p-8 rounded-3xl border-primary/20 shadow-[0_0_40px_rgba(16,185,129,0.1)]"
              >
                <div className="flex items-center gap-3 mb-8 pb-6 border-b border-white/10">
                  <div className="p-2 rounded-full bg-primary/20 text-primary">
                    <Award className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-foreground">Curriculum Parameters Set</h2>
                    <p className="text-sm text-muted-foreground font-mono mt-1">Review the AI's understanding before we generate your plan.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                  <div className="bg-black/20 p-5 rounded-2xl border border-white/5">
                    <dt className="font-mono text-xs text-primary mb-2 uppercase tracking-wider flex items-center gap-2">
                      <BookOpen className="w-3 h-3" /> Topic
                    </dt>
                    <dd className="font-sans text-lg font-medium">{parsedIntent.domain}</dd>
                  </div>
                  <div className="bg-black/20 p-5 rounded-2xl border border-white/5">
                    <dt className="font-mono text-xs text-primary mb-2 uppercase tracking-wider flex items-center gap-2">
                      <Target className="w-3 h-3" /> Target Outcome
                    </dt>
                    <dd className="font-sans text-lg font-medium">{parsedIntent.target_outcome}</dd>
                  </div>
                  <div className="bg-black/20 p-5 rounded-2xl border border-white/5">
                    <dt className="font-mono text-xs text-primary mb-2 uppercase tracking-wider flex items-center gap-2">
                      <TrendingUp className="w-3 h-3" /> Current Level
                    </dt>
                    <dd className="font-sans text-lg font-medium capitalize">{parsedIntent.current_skill_level}</dd>
                  </div>
                  <div className="bg-black/20 p-5 rounded-2xl border border-white/5">
                    <dt className="font-mono text-xs text-primary mb-2 uppercase tracking-wider flex items-center gap-2">
                      <Clock className="w-3 h-3" /> Commitment
                    </dt>
                    <dd className="font-sans text-lg font-medium">{parsedIntent.timeline_weeks} weeks @ {formData.hours_per_week} hrs/week</dd>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-end mt-8">
                  <button
                    onClick={() => {
                      setShowIntent(false);
                      setParsedIntent(null);
                      setGoal(null);
                      setStep(1);
                    }}
                    className="px-6 py-3 rounded-full border border-white/10 text-foreground font-medium hover:bg-white/5 transition-all text-center"
                  >
                    Edit Input
                  </button>
                  <button
                    onClick={handleGeneratePlan}
                    disabled={loading}
                    className="group relative flex items-center justify-center gap-2 px-8 py-3 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-all overflow-hidden shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                  >
                    <span className="relative z-10 flex items-center gap-2">
                      {loading ? (
                        <>
                          <Sparkles className="w-4 h-4 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          Generate Adaptive Plan
                          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </>
                      )}
                    </span>
                    {loading && (
                      <div className="absolute inset-0 bg-black/10 z-0 animate-pulse" />
                    )}
                  </button>
                </div>
              </motion.div>
            )}

            {goal && !showIntent && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-card p-8 rounded-3xl text-center"
              >
                <div className="w-16 h-16 mx-auto bg-primary/20 rounded-full flex items-center justify-center mb-6">
                  <Sparkles className="w-8 h-8 text-primary" />
                </div>
                <h2 className="text-2xl font-bold mb-4">Plan Ready!</h2>
                <p className="text-muted-foreground mb-8">Your personalized learning journey has been mapped out.</p>
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-all"
                >
                  Go to Dashboard <ArrowRight className="w-4 h-4" />
                </Link>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </motion.div>
    </div>
  );
}