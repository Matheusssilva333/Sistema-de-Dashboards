export interface Summary {
  spend: number;
  roas: number;
  conversions: number;
  cpa: number;
  ctr: number;
  clicks: number;
}

export interface DailyMetric {
  date: string;
  spend: number;
  conversions: number;
  roas: number;
}

export interface Campaign {
  id: number;
  name: string;
  status: "active" | "paused" | "archived";
  spend: number;
  roas: number;
  conversions: number;
}

export interface DashboardData {
  summary: Summary;
  daily: DailyMetric[];
  campaigns: Campaign[];
  isDemo?: boolean;
  isRealData?: boolean;
  isConnected?: boolean;
  subscription?: {
    plan: string;
    status: string;
    expiresAt: string | null;
  };
}
