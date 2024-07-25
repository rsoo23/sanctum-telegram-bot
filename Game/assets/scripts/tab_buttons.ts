import {
  _decorator,
  Component,
  director,
  Label,
  Sprite,
  resources,
  SpriteFrame,
  Node,
} from "cc";
import { Router } from "./router";
const { ccclass, property } = _decorator;

@ccclass("TabButtons")
export class TabButtons extends Component {
  @property({ type: Node })
  godlEarnerButton: Node | null = null;
  @property({ type: Node })
  referButton: Node | null = null;
  @property({ type: Node })
  alliancesButton: Node | null = null;

  private leaderboardEarnerPagePath: string =
    "assets/scenes/leaderboard_earner_page";
  private leaderboardReferralPagePath: string =
    "assets/scenes/leaderboard_referral_page";
  private leaderboardAlliancePagePath: string =
    "assets/scenes/leaderboard_alliances_page";

  onGodlEarnerButtonPressed() {
    director.loadScene(this.leaderboardEarnerPagePath);
    Router.navigateTo("/leaderboard");
  }

  onReferButtonPressed() {
    director.loadScene(this.leaderboardReferralPagePath);
    Router.navigateTo("/leaderboard");
  }

  onAllianceButtonPressed() {
    director.loadScene(this.leaderboardAlliancePagePath);
    Router.navigateTo("/leaderboard");
  }
}
