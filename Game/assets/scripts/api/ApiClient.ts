import ApiService from "./ApiService";

export default {
  users: {
    getUser: (userId: string) => {
      return ApiService.get(`/user/${userId}/`);
    },
  },
  roulette: {
    playRoulette: (params: { user: string; bet: number }) => {
      return ApiService.post(`/roulette/play/`, params);
    },
  },
  referrals: {
    getReferralList: (userId: string) => {
      return ApiService.get(`/referral_history/user/${userId}/`);
    },
  },
  leaderboards: {
    getLeaderboard: (userId: string, type: "gold" | "referral") => {
      return ApiService.get(`/user/${userId}/leaderboard/?type=${type}`);
    },
    getPage: (userId: string, type: "gold" | "referral") => {
      return ApiService.get(`/user/${userId}/leaderboard_page/?type=${type}`);
    },
    getOtherPage: (userId: string, cursor: string) => {
      return ApiService.get(`/user/${userId}/leaderboard_page/?${cursor}`);
    }
  },
  tap_and_earn: {
    lookup: (userId: string) => {
      return ApiService.get(`/tap_and_earn/lookup/?user_id=${userId}`);
    },
    claimAmount: (params: {user: string}) => {
      return ApiService.post(`/tap_and_earn/claim/`, params);
    },
  },
  dailyreward: {
	getDailyReward: (telegram_id: string) => {
	  return ApiService.get(`/daily-reward/check/${telegram_id}`);
	},
	claimDailyReward: (params: { telegram_id: string }) => {
	  return ApiService.post(`/daily-reward/claim/`, params);
	},
  },
};
