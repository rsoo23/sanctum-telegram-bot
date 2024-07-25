import { _decorator, Component, Label, Node, Animation, director, Director, AnimationClip, ProgressBar } from 'cc';
const { ccclass, property } = _decorator;

import GlobalState from "../state/GlobalState";
import ApiClient from "../api/ApiClient";

import { formatNumber } from '../utils/NumberUtils';

@ccclass('ClaimGold')
export class ClaimGold extends Component {
    @property({ type: Label }) userGoldAmountLabel: Label | null = null;
    @property({ type: Label }) rewardOverlayGoldLabel: Label | null = null;

    @property({ type: Node }) claimButton: Node | null = null;
    @property({ type: Node }) claimableMode: Node | null = null;
    @property({ type: Label }) cooldownLabel: Label | null = null;
    @property({ type: ProgressBar }) cooldownProgressBar: ProgressBar | null = null;

    @property({ type: Node }) errorOverlay: Node | null = null;
    @property({ type: Animation }) errorOverlayAnim: Node | null = null;

    @property({ type: Node }) rewardOverlay: Node | null = null;
    @property({ type: Animation }) rewardOverlayAnim: Node | null = null;

    private userInfo: User = null;
    private goldClaimRechargeTime: number = 60; // in minutes (for testing purposes)
    private isSceneSwitching: Boolean = false;

    async onLoad() {
        this.isSceneSwitching = false;
        // this.errorOverlay.active = false;
        director.on(Director.EVENT_BEFORE_SCENE_LOADING, this.onSceneSwitching, this);
        // retrieve user info
        this.userInfo = GlobalState.getUserData();

        if (!this.userInfo) {
            this.userInfo = await GlobalState.loadUserData();
            if (this.userInfo) {
                GlobalState.setUserData(this.userInfo);
            }
        }

        // load other info
        if (this.userInfo) {
            this.updateUserGoldLabel(this.userInfo.gold);
            await this.initUser();
        } else {
            console.error("Failed to load user data");
        }
    }

    onSceneSwitching() {
        this.isSceneSwitching = true;
    }

    // this is to check if the user is a first timer
    async initUser() {
        const response = await ApiClient.tap_and_earn.lookup(this.userInfo.telegram_id)

        console.log("init user: ", response)
        if (response[0] === "Not Found") {
            this.showClaimableMode()
            console.log("Lookup failed")
        } else {
            this.hideClaimableMode()
            this.initTimer(response["time_last_claimed"])
            console.log("Lookup successful")
        }
    }

    showClaimableMode() {
        this.claimableMode.active = true
    }

    hideClaimableMode() {
        this.claimableMode.active = false
    }

    async updateGoldLabels(data: any): Promise<void> {
        let userGoldAmount: number = data["user_details"]["gold"]
        let rewardGoldAmount: number = data["claimed_amount"]

        this.updateUserGoldLabel(userGoldAmount);
        this.updateRewardOverlayGoldLabel(rewardGoldAmount)
    }

    async onClaimButtonPressed() {
        const response = await ApiClient.tap_and_earn.claimAmount({
            "user": this.userInfo.telegram_id
        });

        if (response.hasOwnProperty("Error")) {
            this.errorOverlayAnimation()
        } else {
            const data = await ApiClient.tap_and_earn.lookup(this.userInfo.telegram_id)

            if (data) {
                this.initTimer(data["time_last_claimed"])
                this.updateGoldLabels(data)
                this.rewardOverlayAnimation()
                this.hideClaimableMode()
            } else {
                console.log("Failed to load user info via lookup")
            }
        }
    }

    updateUserGoldLabel(gold: number) {
        this.userGoldAmountLabel.string = formatNumber(gold);
    }

    updateRewardOverlayGoldLabel(gold: number) {
        this.rewardOverlayGoldLabel.string = "+" + formatNumber(gold);
    }

    async errorOverlayAnimation() {
        if (this.isSceneSwitching) {
            return;
        }
        this.errorOverlay.active = true;
        this.claimButton.interactable = false;
        this.errorOverlayAnim.play("error_fade_in");
        await new Promise((resolve) => setTimeout(resolve, 1500));
        if (this.isSceneSwitching) {
            return;
        }
        this.errorOverlayAnim.play("error_fade_out");
        await new Promise((resolve) => setTimeout(resolve, 2000));
        if (this.isSceneSwitching) {
            return;
        }
        this.errorOverlay.active = false;
        this.claimButton.interactable = true;
    }

    async rewardOverlayAnimation() {
        if (this.isSceneSwitching) {
            return;
        }
        this.rewardOverlay.active = true;
        this.claimButton.interactable = false;
        this.rewardOverlayAnim.play("reward_overlay_fade_in");
        await new Promise((resolve) => setTimeout(resolve, 1500));
        if (this.isSceneSwitching) {
            return;
        }
        this.rewardOverlayAnim.play("reward_overlay_fade_out");
        await new Promise((resolve) => setTimeout(resolve, 1500));
        if (this.isSceneSwitching) {
            return;
        }
        this.rewardOverlay.active = false;
        this.claimButton.interactable = true;
    }

    initTimer(createdAtString: string) {
        const createdAtDate: Date = new Date(createdAtString)
        const claimableTime: Date = new Date(createdAtDate.getTime() + this.goldClaimRechargeTime * 60 * 1000)

        this.startCountdownTimer(claimableTime)
    }

    startCountdownTimer(claimableTime: Date): void {
        const now: Date = new Date();
        const targetTime: number = claimableTime.getTime();
        const difference: number = targetTime - now.getTime();

        if (difference <= 0) {
            this.showClaimableMode()
            console.log("Countdown timer has expired!");
            return;
        }

        const minutes: number = Math.floor(difference / (1000 * 60));
        const formattedMinutes: string = minutes.toString()

        console.log(`Countdown: ${formattedMinutes}`);

        this.updateCooldownLabel(formattedMinutes)
        this.updateCooldownProgressBar(minutes)

        // Call the function again after 1 minute to update the timer
        setTimeout(() => this.startCountdownTimer(claimableTime), 60000);
        //console.log("time difference: ", difference)
    }

    updateCooldownLabel(formattedMinutes: string) {
        if (this.cooldownLabel) {
            this.cooldownLabel.string = formattedMinutes + ' MIN'
        } else {
            console.log('Countdown Label Not Found')
        }
    }

    updateCooldownProgressBar(minutes: number) {
        if (this.cooldownProgressBar) {
            this.cooldownProgressBar.progress = 1- minutes/60;
        } else {
            console.log('Countdown Progress Bar Not Found')
        }
    }

    onDestroy() {
        director.off(Director.EVENT_BEFORE_SCENE_LOADING, this.onSceneSwitching, this);
    }
}
