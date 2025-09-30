export * from './types.js';

// Shared utilities
export const API_ENDPOINTS = {
  FEED: '/api/feed',
  CALCULATOR: '/api/calculator', 
  SURVEY: '/api/survey',
} as const;

export const GOALS = [
  'Improve study habits',
  'Strengthen parent–child relationship',
  'Explore extracurriculars', 
  'Plan university pathway',
] as const;

export const FEED_ITEMS = [
  { title: "Ask about today's highlight", text: "One genuine question at dinner builds trust." },
  { title: "Read 10 minutes together", text: "Shared reading beats solo scrolling." },
  { title: "Plan a study break", text: "A 5-minute stretch improves focus." },
  { title: "Celebrate small wins", text: "Notice effort, not just results." },
  { title: "Tomorrow's checklist", text: "Set two priorities before bed." },
  { title: "Screen-time agreement", text: "Co-create rules; kids follow what they help design." },
  { title: "Praise effort", text: "Name the strategy they used, not just the outcome." },
  { title: "1:1 time", text: "10 minutes of undistracted attention strengthens bonds." },
  { title: "Focus sprint", text: "Try two 25-5 Pomodoros this evening." },
  { title: "Ask why", text: "Explore interests behind a new hobby—it reveals motivations." },
  { title: "Plan tomorrow", text: "Pack the bag together; lower morning stress." },
  { title: "Family walk", text: "Light exercise improves sleep quality." },
] as const;