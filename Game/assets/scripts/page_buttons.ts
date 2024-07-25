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

// import { GlobalInfo } from './global_info'

@ccclass("PageButtons")
export class PageButtons extends Component {
  @property({ type: Node })
  rouletteButton: Node | null = null;
  @property({ type: Node })
  referButton: Node | null = null;
  @property({ type: Node })
  leaderboardButton: Node | null = null;

  private roulettePagePath: string = "assets/scenes/roulette_page";
  private referralPagePath: string = "assets/scenes/referral_page";
  private leaderboardPagePath: string = "assets/scenes/leaderboard_earner_page";

  onRouletteButtonPressed() {
    director.loadScene(this.roulettePagePath);
    Router.navigateTo("/roulette");
  }

  onReferButtonPressed() {
    director.loadScene(this.referralPagePath);
    Router.navigateTo("/referral");
  }

  onLeaderboardButtonPressed() {
    director.loadScene(this.leaderboardPagePath);
    Router.navigateTo("/leaderboard");
  }
}
