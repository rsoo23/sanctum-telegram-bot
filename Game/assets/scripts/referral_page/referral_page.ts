import {
  _decorator,
  Component,
  Prefab,
  Label,
  Button,
  instantiate,
  Node,
  Layout,
  Animation,
  Canvas,
  Director,
  director
} from "cc";
const { ccclass, property } = _decorator;
import GlobalState from "../state/GlobalState";
import { ReferralRecord } from "./referral_record";
import { sendAnalyticsEvent } from "../utils/GoogleAnalytics";
import EnvLoader from "../utils/EnvLoader";
import { ResolutionHelper } from "../utils/ResolutionHelper";
import ApiClient from "../api/ApiClient";

@ccclass("ReferralPage")
export class ReferralPage extends Component {
  private referralCode: string | null = null;
  private botname: string | null = null;
  private telegramMessage: string | null = null;

  @property({ type: Node })
  canvasNode: Node | null = null;

  @property({ type: Label })
  referralCodeLabel: Label | null = null;

  @property({ type: Node })
  copyToClipboardNode: Node | null = null;

  @property({ type: Button })
  inviteFriendsButton: Button | null = null;

  @property({ type: Prefab })
  referralHistoryItem: Prefab | null = null;

  @property({ type: Node })
  parentNode: Node | null = null;

  @property({ type: Node })
  emptyStateLabel: Node | null = null;

  //message overlay
  @property({ type: Node })
  public messageOverlay: Node | null = null;
  @property({ type: Animation })
  public messageOverlayAnim: Animation | null = null;

  private isSceneSwitching: Boolean = false;

  async onLoad() {
    await EnvLoader.loadConfig();
    this.botname = EnvLoader.get("TELEGRAM_BOTNAME");

    this.isSceneSwitching = false; 
    director.on(Director.EVENT_BEFORE_SCENE_LOADING, this.onSceneSwitching, this);

    this.adjustResolution();
    sendAnalyticsEvent("page_view", "Scene Loaded", "Referral", "Referral");
    await this.loadUser();
    await this.loadReferralHistory();
    this.inviteFriendsButton.node.on("click", this.shareInviteLink, this);
    this.copyToClipboardNode.on(
      Node.EventType.TOUCH_END,
      this.onNodeClicked,
      this
    );
    this.telegramMessage = `🎁 I'm giving you 100 GODL.\n@sanctumai_bot is the 1st Web3 AI open world on telegram. Play and earn mega airdrop rewards now!
    \n👉 Redeem GODL with my code: https://t.me/${this.botname}?start=${this.referralCode}`;
  }

  onSceneSwitching() {
    this.isSceneSwitching = true;
  }

  private adjustResolution() {
    if (this.canvasNode) {
      ResolutionHelper.adjustResolution(this.canvasNode);
    } else {
      console.error("No Canvas node found");
    }
  }

  async loadUser(): Promise<void> {
    let userInfo = GlobalState.getUserData();
    if (!userInfo) {
      console.log("load user info.");

      userInfo = await GlobalState.loadUserData();
    }
    if (userInfo) {
      this.updateReferralCodeLabel(userInfo.referral_id);
      this.referralCode = userInfo.referral_id;
    } else {
      console.log("Failed to load user info.");
    }
  }

  async loadReferralHistory(): Promise<void> {
    let userInfo = GlobalState.getUserData();

    if (userInfo) {
      const referralHistoryData = await ApiClient.referrals.getReferralList(
        userInfo.telegram_id
      );
      this.renderItems(referralHistoryData);
    } else {
      console.log("Failed to load user referral history.");
    }
  }

  renderItems(data: ReferralRecordItem[]) {
    if (!this.referralHistoryItem || !this.parentNode) return;
    this.parentNode.removeAllChildren();
    if (data.length > 0) {
      this.emptyStateLabel.active = false;

      data.forEach((itemData, i) => {
        const newItem = instantiate(this.referralHistoryItem);
        const referralRecordComponent = newItem.getComponent(ReferralRecord);
        if (referralRecordComponent) {
          referralRecordComponent.init({ index: i + 1, ...itemData });
        }
        this.parentNode.addChild(newItem);
      });
    } else {
      this.emptyStateLabel.active = true;
    }

    const layout = this.parentNode.getComponent(Layout);
    if (layout) {
      layout.updateLayout();
    }
  }

  updateReferralCodeLabel(code: string): void {
    this.referralCodeLabel.string = code;
  }

  async copyToClipboard(text: string) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(text);
        console.log("Text copied to clipboard: " + text);
      } catch (err) {
        console.error("Failed to copy text using Clipboard API: ", err);
        this.fallbackCopyToClipboard(text);
      }
    } else {
      console.warn(
        "Clipboard API not supported or unavailable. Using fallback method."
      );
      this.fallbackCopyToClipboard(text);
    }
  }

  fallbackCopyToClipboard(text: string) {
    const el = document.createElement("textarea");
    el.value = text;
    document.body.appendChild(el);
    el.select();
    const successful = document.execCommand("copy");
    document.body.removeChild(el);

    if (successful) {
      console.log("Text copied to clipboard using fallback method: " + text);
    } else {
      console.error("Failed to copy text using fallback method.");
      alert("Failed to copy text to clipboard.");
    }
  }

  async onNodeClicked() {
    if (this.isSceneSwitching) {
      return;
    }
    this.copyToClipboard(this.telegramMessage);
    this.messageOverlay.active = true;
    this.messageOverlayAnim.play("error_fade_in");
    await new Promise((resolve) => setTimeout(resolve, 2500));
    if (this.isSceneSwitching) {
      return;
    }
    this.messageOverlayAnim.play("error_fade_out");
    await new Promise((resolve) => setTimeout(resolve, 2000));
    if (this.isSceneSwitching) {
      return;
    }
    this.messageOverlay.active = false;
    sendAnalyticsEvent("invite", "Invite Friends", "invite");
  }

  shareInviteLink() {
    sendAnalyticsEvent("invite", "Invite Friends", "invite");

    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.showPopup({
        title: "Share Invite Link",
        message: this.telegramMessage,
        buttons: [
          {
            id: "share",
            type: "text",
            text: "Share",
            onClick: function () {
              window.Telegram.WebApp.sendData(this.telegramMessage);
            },
          },
          {
            id: "cancel",
            type: "text",
            text: "Cancel",
            onClick: function () {
              window.Telegram.WebApp.close();
            },
          },
        ],
      });
    } else {
      console.error("Telegram WebApp is not available.");

      const telegramUrl = `https://t.me/share/url?url=${encodeURIComponent(
        this.telegramMessage
      )}`;

      window.open(telegramUrl, "_blank");
    }
  }

  start() { }

  onDestroy() {
    director.off(Director.EVENT_BEFORE_SCENE_LOADING, this.onSceneSwitching, this);
  }
}
