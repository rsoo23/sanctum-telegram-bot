import {
    _decorator,
    Component,
    director,
    Label,
    Sprite,
    resources,
    SpriteFrame,
    Node,
    Button,
    Color,
} from "cc";
import ApiClient from "../api/ApiClient";
import ApiService from "../api/ApiService";
import GlobalState from "../state/GlobalState";
const { ccclass, property } = _decorator;

// import { GlobalInfo } from './global_info'

@ccclass("DailyReward")
export class DailyReward extends Component {
    @property({ type: Button })
    showDailyRewardButton: Button | null = null;
    @property({ type: Node })
    dailyRewardModal: Node | null = null;
    @property({ type: Node })
    dailyRewardBackground: Node | null = null;
    @property({ type: Node })
    days: Node[] = [];
    @property({ type: Button })
    claimDailyRewardButton: Button | null = null;
	@property({ type: Button })
	alreadyClaimedButton: Button | null = null;

    // sprite
    @property({ type: SpriteFrame })
    claimableBackground: SpriteFrame | null = null;
    @property({ type: SpriteFrame })
    normalBackground: SpriteFrame | null = null;
	@property({ type: Label })
	playerGoldLabel: Label | null = null;

    public currentClaimableDay: number = 0;
	public daystreaks: number = 0;
	public claimed: boolean = false;
	public userGold: number = 0;
    public rewards: Array<any> = [
        {
            day: 1,
            claimable: true,
            claimed: false,
        },
        {
            day: 2,
            claimable: false,
            claimed: false,
        },
        {
            day: 3,
            claimable: false,
            claimed: false,
        },
        {
            day: 4,
            claimable: false,
            claimed: false,
        },
        {
            day: 5,
            claimable: false,
            claimed: false,
        },
        {
            day: 6,
            claimable: false,
            claimed: false,
        },
        {
            day: 7,
            claimable: false,
            claimed: false,
        },
        {
            day: 8,
            claimable: false,
            claimed: false,
        },
    ];

    async onLoad() { 
		this.dailyRewardModal.active = false;
		this.getUserGold();
    }

	async getUserGold(): Promise<void> {
		let userData = GlobalState.loadUserData();
		let userGold = this.formatNumber((await userData).gold);

		if (userData) {
			this.updateRouletteGold(userGold);
			console.log("User data loaded and stored globally:", userData)
		} else {
			console.error("Failed to load user data.");
		}
	}

	updateRouletteGold(gold: string) {
		this.playerGoldLabel.string = gold;
	}

	formatNumber(number: number): string {
		const sign = number < 0 ? "-" : "";
		const absNumber = Math.abs(number);
	
		if (absNumber >= 1000000) {
		  const formattedNumber = (absNumber / 1000000)
			.toFixed(3)
			.replace(".", ".");
		  return sign + formattedNumber + "M";
		} else if (absNumber >= 1000) {
		  return sign + absNumber.toLocaleString("en-US");
		} else {
		  return sign + absNumber.toString();
		}
	  }

	static async getDailyReward(
		telegram_id: string
	): Promise<any> {
		try {
			const response = await ApiClient.dailyreward.getDailyReward(telegram_id);
			if (response) {
				return response;
			} else {
				console.error("Failed to get daily reward.");
				return null;
			}
		} catch (error) {
		console.error("Error getting daily reward:", error);
		return null;
		}
	}

	static async claimDailyRewards(
		telegram_id: string
	): Promise<DailyRewards> {
		try {
			const response = await ApiClient.dailyreward.claimDailyReward({ telegram_id });
			console.log("Claim daily reward response:", response);
			if (response) {
				console.log("Claimed daily reward.");
				return response;
			} else {
				console.error("Failed to claim daily reward.");
			}
		} catch (error) {
			console.error("Error claiming daily reward:", error);
		}
	}

	async checkDailyReward(telegram_id: string): Promise<void> {
		const daily_reward = await DailyReward.getDailyReward(telegram_id);
		this.daystreaks = daily_reward.day_streak;
		this.claimed = daily_reward.claimed;
		if (daily_reward) {
			if (daily_reward.claimed === false) {
				this.claimDailyRewardButton.node.active = true;
				this.alreadyClaimedButton.node.active = false;
			} else if (daily_reward.claimed === true){
				this.claimDailyRewardButton.node.active = false;
				this.alreadyClaimedButton.node.active = true;
			}
			console.log("1. Daystreaks:", this.daystreaks, "Claimed:", this.claimed);
			this.updateClaimed(this.daystreaks, this.claimed);
		} else {
			console.error("Failed to get daily reward.");
		}
	}

	async claimDailyReward(userId: string): Promise<void> {
		const daily_reward = await DailyReward.claimDailyRewards(userId);

		this.daystreaks = daily_reward.day_streak;
		this.claimed = daily_reward.claimed;
		console.log("Claimed daily reward:", this.claimed, "Daystreaks:", this.daystreaks)
		if (daily_reward) {
			this.getUserGold();
			this.updateClaimed(this.daystreaks, this.claimed);
			this.claimDailyRewardButton.node.active = false;
			this.alreadyClaimedButton.node.active = true;
		} else {
			console.error("Failed to claim daily reward.");
		}
	}
	
	onCloseDailyRewardModal() {
		this.dailyRewardModal.active = false;
	}

    onShowDailyRewardBtnPress() {
		let telegramId = GlobalState.getUserData().telegram_id
		this.checkDailyReward(telegramId);
        this.dailyRewardModal.active = true;
    }

    onClaimDailyRewardBtnPress() {
		this.claimDailyReward(GlobalState.getUserData().telegram_id);
    }

    updateClaimed(claim_day: number, claimed: boolean) {
		console.log("2. Daystreaks:", claim_day, "Claimed:", claimed);
		for (let i = 0; i < this.rewards.length; i++) {
			console.log("i:", i, "Claimed:", this.rewards[i].claimed, "Claimable:", this.rewards[i].claimable)
			if (i < claim_day) {
				console.log("hi 1");
				this.rewards[i].claimable = false;
				this.rewards[i].claimed = true;
			} else if (i === claim_day && claimed === false) {
				console.log("hi 2");
				this.rewards[i].claimable = true;
				this.rewards[i].claimed = false;
			} else if (i === claim_day && claimed === true) {
				console.log("hi 3");
				this.rewards[i].claimable = false;
				this.rewards[i].claimed = true;
			}
        }

        for (let i = 0; i < this.rewards.length; i++) {
            if (this.rewards[i].claimed) {
                this.days[i].getChildByPath('Layout/Gold').active = false;
                this.days[i].getChildByPath('Layout/Claimed').active = true;
                this.days[i].getChildByPath('Layout/Title').getComponent(Label).color = new Color(0, 0, 0, 255);
                this.days[i].getChildByPath('Layout/Amount').getComponent(Label).color = new Color(0, 0, 0, 255);
                this.days[i].getComponent(Sprite).spriteFrame = this.normalBackground;
            }
            if (this.rewards[i].claimable) {
                this.days[i].getChildByPath('Layout/Gold').active = true;
                this.days[i].getChildByPath('Layout/Claimed').active = false;
                this.days[i].getChildByPath('Layout/Title').getComponent(Label).color = new Color(255, 255, 255, 255);
                this.days[i].getChildByPath('Layout/Amount').getComponent(Label).color = new Color(255, 255, 255, 255);
                this.days[i].getComponent(Sprite).spriteFrame = this.claimableBackground;
            }
        }
    }

    setcurrentClaimableDay(days: number) {
        this.currentClaimableDay = days;
    }
}