// Shared types between frontend and backend

export interface FeedItem {
  title: string;
  text: string;
}

export interface FeedResponse {
  items: FeedItem[];
  streak: number;
}

export interface CalculatorRequest {
  a: number;
  b: number;
}

export interface CalculatorResponse {
  result: number;
}

export interface SurveyRequest {
  goal: string;
  note?: string;
}

export interface SurveyResponse {
  goal: string;
  note: string;
  recommendation: string;
  tiny_actions: string[];
}

export type AppView = 'home' | 'feed' | 'calculator' | 'survey' | 'report';

export interface ReportData {
  goal: string;
  note: string;
}