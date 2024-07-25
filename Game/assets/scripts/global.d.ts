interface User {
  telegram_id: string;
  referral_id: string;
  username: string;
  gold: number;
  roulettes: any[];
  referred_by: string | null;
  agents: any[];
  email: string | null;
  created_at: string;
}

interface ReferralRecordItem {
  telegram_id: string;
  referred: string;
  created_at: string;
  referred_by: string;
  amount: number;
}

interface TopEarnerRecord {
  rank: number;
  username: string;
  gold: number;
}

interface DailyRewards {
	day_streak: number;
	claimed: boolean;
}

interface TopReferralRecordItem {
  telegram_id: string;
  referral_id: string;
  username: string;
  gold: number;
  roulettes: any[];
  referred_by: string;
  referral_count: number;
  agents: any[];
  email: string;
  create_at: string;
  rank: number;
}

interface UserDetails {
  username: string;
  gold: number;
}

interface BetRecord {
  id: number;
  user: number;
  user_details: UserDetails;
  bet: number;
  outcome: number;
  created_at: string;
}

interface RoulettePlay {
  user: string;
  bet: number;
}

interface Roulette {
  id: number;
  user: string;
  // user_details: ;
  bet: number;
  outcome: number;
  created_at: string;
}

interface TelegramWebApp {
  showPopup(params: {
    title: string;
    message: string;
    buttons: {
      id: string;
      type: string;
      text: string;
      onClick: () => void;
    }[];
  }): void;
  sendData(data: string): void;
  close(): void;
}

interface Window {
  Telegram?: {
    WebApp?: TelegramWebApp;
  };
}
