import {
  _decorator,
  Component,
  Label,
  Node,
  AnimationClip,
  Animation,
  Scene,
  Screen,
  director,
  Prefab,
  Button,
  EditBox,
  instantiate,
  Layout,
  Event,
  Canvas,
  Tween,
  tween,
  randomRange,
} from "cc";
const { ccclass, property } = _decorator;
import GlobalState from "../state/GlobalState";
import ApiService from "../api/ApiService";
import { WebSocketComponent } from "./websocket";
import { RecordItem } from "./record_item";
import { sendAnalyticsEvent } from "../utils/GoogleAnalytics";
import { ResolutionHelper } from "../utils/ResolutionHelper";
import ApiClient from "../api/ApiClient";
import { trimString } from "../utils/StringUtils";

enum RouletteState {
  L_CLOSE,
  W_CLOSE,
  SPIN,
  ERROR,
}

enum RouletteRecordType {
  WIN,
  LOSE,
}

@ccclass("RoulettePage")
export class RoulettePage extends Component {
  @property({ type: Node })
  canvasNode: Node | null = null;
  //result menu
  @property({ type: Node })
  public resultMenuWin: Node | null = null;
  @property({ type: Node })
  public resultMenuLose: Node | null = null;
  @property({ type: Node })
  public resultMenuBackground: Node | null = null;
  @property({ type: Node })
  public fadeInMenu: Node | null = null;
  @property({ type: Node })
  public fadeInMenuRed: Node | null = null;

  //player gold
  @property({ type: Label })
  public playerGoldLabel: Label | null = null;
  @property({ type: EditBox })
  public inputGold: EditBox | null = null;
  @property({ type: Label })
  public placeholderGold: Label | null = null;

  //spin animation
  @property({ type: Node })
  public rouletteWheel: Node | null = null;
  @property({ type: Animation })
  public spinAnimation: Animation | null = null;

  //buttons
  @property({ type: Button })
  public spinButton: Button | null = null;
  @property({ type: Button })
  public rouletteButton: Button | null = null;
  @property({ type: Button })
  public referralButton: Button | null = null;
  @property({ type: Button })
  public leaderboardButton: Button | null = null;
  @property({ type: Button })
  public howToPlayButton: Button | null = null;

  //how to play overlay
  @property({ type: Node })
  public howToPlayOverlay: Node | null = null;
  @property({ type: Animation })
  public howToPlayOverlayAnim: Animation | null = null;

  //error overlay
  @property({ type: Node })
  public errorOverlay: Node | null = null;
  @property({ type: Animation })
  public errorOverlayAnim: Animation | null = null;
  @property({ type: Label })
  public errorLabel: Label | null = null;

  //gold amount win or lose
  @property({ type: Label })
  public goldAmountLabelWin: Label | null = null;
  @property({ type: Label })
  public goldAmountLabelLose: Label | null = null;

  //bottom panel
  @property({ type: Prefab })
  WinResultItem: Prefab | null = null;
  @property({ type: Prefab })
  LoseResultItem: Prefab | null = null;
  @property({ type: Node })
  parentNode: Node | null = null;

  @property({ type: Node })
  emptyStateLabel: Node | null = null;

  public userId: string | null = null;
  public goldOutcome: number = 0;
  public userGold: number = 0;
  private renderList: BetRecord[] = [];
  private allowRenderItems: boolean;
  public goldAmount: number = 0;
  rouletteWheelTween: Tween<Node>;

  parseNumber(formattedString: string): number {
    const numberString = formattedString.replace(/\,|\.K|M/g, "");

    if (!numberString.trim() || isNaN(Number(numberString))) {
      return 0;
    }
    if (formattedString.endsWith("M")) {
      return parseFloat(numberString) * 1000000;
    }
    if (formattedString.endsWith("K")) {
      return parseFloat(numberString) * 1000;
    }
    return parseFloat(numberString);
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

  onLoad() {
    this.adjustResolution();
    sendAnalyticsEvent("page_view", "Scene Loaded", "Roulette", "Roulette");
    this.curSpinState = RouletteState.L_CLOSE;
    this.curSpinState = RouletteState.W_CLOSE;
    this.resultMenuBackground.active = false;
    this.fadeInMenu.active = false;
    this.fadeInMenuRed.active = false;
    this.errorOverlay.active = false;
    this.howToPlayOverlay.active = false;
    this.allowRenderItems = true;
    this.emptyStateLabel.active = true;
    WebSocketComponent.eventTarget.on("spin", this.handleSpin, this);
    WebSocketComponent.eventTarget.on("spinArray", this.handleSpinArray, this);
    this.getUserGold();
  }

  private adjustResolution() {
    if (this.canvasNode) {
      ResolutionHelper.adjustResolution(this.canvasNode);
    } else {
      console.error("No Canvas node found");
    }
  }

  protected start(): void {
    // this.spinAnimation.play("revolver_idle");
    tween(this.rouletteWheel)
      .repeatForever(tween().by(3, { angle: -360 }))
      .start();
    this.inputGold.string = "10";
    this.placeholderGold.string = "10";
  }

  rotateRouletteWheel(
    endAngle: number,
    duration: number,
    type: string,
    loop: boolean
  ): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const startAngle = this.rouletteWheel.angle;
      let endA = endAngle || startAngle - 360; // 10 full rotations
      const d = duration || 9; // Duration of the spin

      switch (type) {
        case "win":
          this.rouletteWheel.angle = this.normalizeAngle(startAngle);
          endA = (Math.floor(this.normalizeAngle(startAngle) + randomRange(60, 300) * -20));
          while ( this.normalizeAngle(endA) < 30 || this.normalizeAngle(endA) > 300 ) {
			console.log("hit");
            endA = Math.floor(this.normalizeAngle(startAngle) + randomRange(60, 300) * -20)
          }
          break;
        case "lose":
          this.rouletteWheel.angle = this.normalizeAngle(startAngle);
          endA = 360 * -10;
          break;
        default:
          endA = startAngle - 360;
          break;
      }

      this.rouletteWheelTween = tween(this.rouletteWheel);
      this.rouletteWheelTween
        .repeat(
          10,
          tween().to(
            d,
            { angle: endA },
            {
              easing: "quintOut",
              onComplete: () => {
                resolve(true);
              },
            }
          )
        )
        .start();
    });
  }

  normalizeAngle(angle: number) {
    return ((angle % 360) + 360) % 360;
  }

  async getUserGold(): Promise<void> {
    let userData = GlobalState.loadUserData();
    let userGold = this.formatNumber((await userData).gold);

    if (userData) {
      console.log(userData);
      this.updateRouletteGold(userGold);
    } else {
      console.error("Failed to load user data");
    }
  }

  private handleSpin(spin: BetRecord) {
    console.log("Spin received in SceneScript:", spin);

    if (this.allowRenderItems) {
      this.renderItem(
        this.isPositive(spin.outcome)
          ? RouletteRecordType.WIN
          : RouletteRecordType.LOSE,
        spin
      );
    } else {
      this.renderList.push(spin);
    }
  }

  private handleSpinArray(spinArray: BetRecord[]) {
    console.log("Spin array received in SceneScript:", spinArray);
    spinArray.reverse().forEach((spinItem) => {
      this.renderItem(
        this.isPositive(spinItem.outcome)
          ? RouletteRecordType.WIN
          : RouletteRecordType.LOSE,
        spinItem
      );
    });
  }

  private renderPendingItems() {
    this.renderList.forEach((spinItem) => {
      this.renderItem(
        this.isPositive(spinItem.outcome)
          ? RouletteRecordType.WIN
          : RouletteRecordType.LOSE,
        spinItem
      );
    });
    this.renderList = [];
  }

  private renderItem(type: RouletteRecordType, data: BetRecord) {
    if (!this.WinResultItem || !this.LoseResultItem || !this.parentNode) return;
    const newItem = instantiate(
      type === RouletteRecordType.WIN ? this.WinResultItem : this.LoseResultItem
    );

    const spinRecordComponent = newItem.getComponent(RecordItem);

    if (spinRecordComponent) {
      spinRecordComponent.init({
        type,
        username: trimString(data.user_details.username, 8),
        outcome: data.outcome,
        timestamp: data.created_at,
      });
    }

    this.emptyStateLabel.active = false;
    this.parentNode.insertChild(newItem, 0);

    const layout = this.parentNode.getComponent(Layout);
    if (layout) {
      layout.updateLayout();
    }
  }

  static async getRouletteOutcome(
    bet: number,
    telegram_id: string
  ): Promise<any> {
    try {
      const roulettePlay = {
        user: telegram_id,
        bet: bet,
      };
      const roulette = await ApiClient.roulette.playRoulette(roulettePlay);
      console.log(roulette);
      if (roulette) {
        console.log("Roulette outcome:", roulette.outcome);
        return roulette;
      } else {
        console.error("Failed to load roulette outcome");
        return null;
      }
    } catch (error) {
      console.error("Error loading roulette outcome:", error);
      return null;
    }
  }

  async roulettePlay(bet: number, telegram_id: string): Promise<void> {
    const roulette = await RoulettePage.getRouletteOutcome(bet, telegram_id);
    if (roulette) {
      this.goldOutcome = roulette.outcome;
      this.curSpinState = RouletteState.SPIN;
      this.userGold = roulette.user_details.gold;
    } else {
      this.curSpinState = RouletteState.ERROR;
    }
  }

  updateRouletteGold(gold: string) {
    this.playerGoldLabel.string = gold;
  }

  isNegative(number: number): boolean {
    return number < 0;
  }

  isPositive(number: number): boolean {
    return number > 0;
  }

  generateSpin() {
    console.log("gold outcome:", this.goldOutcome);
    this.resultMenuBackground.active = true;
    if (this.goldOutcome > 0) {
      this.fadeInMenu.active = true;
      this.fadeInMenu.getComponent(Animation).play("fade_in_result");
      this.winResult();
      console.log("win");
    } else {
      this.fadeInMenuRed.active = true;
      this.fadeInMenuRed.getComponent(Animation).play("fade_in_result_flash");
      this.loseResult();
      console.log("lose");
    }
  }

  loseResult() {
    this.resultMenuLose.active = true;
    this.goldAmountLabelLose.string = this.formatNumber(this.goldOutcome);
    console.log("gold outcome:", this.goldOutcome);
    this.updateRouletteGold(this.formatNumber(this.userGold));
  }

  winResult() {
    this.resultMenuWin.active = true;
    this.goldAmountLabelWin.string = this.formatNumber(this.goldOutcome * 2);
    console.log("gold outcome:", this.goldOutcome);
    this.updateRouletteGold(this.formatNumber(this.userGold));
  }

  intToStringAlt(num: number): string {
    return "" + num;
  }

  stringToInt(str: string): number {
    const num = parseInt(str, 10);
    if (isNaN(num)) {
      throw new Error("Invalid string format for conversion to integer");
    }
    return num;
  }

  async spin() {
    // this.spinAnimation.play("revolver_accelerate");
    // await new Promise((resolve) => setTimeout(resolve, 7000));
    // this.spinAnimation.stop();
    if (this.goldOutcome > 0) {
      this.rotateRouletteWheel(null, 9, "win", false).then(() => {
        console.log("win animation done");
        this.generateSpin();
      });
    } else {
      this.rotateRouletteWheel(null, 9, "lose", false).then(() => {
        console.log("lose animation done");
        this.generateSpin();
      });
    }
  }

  set curSpinState(value: RouletteState) {
    switch (value) {
      case RouletteState.SPIN:
        this.spin();
        break;
      case RouletteState.L_CLOSE:
        this.resultMenuLose.active = false;
        this.renderPendingItems();
        break;
      case RouletteState.W_CLOSE:
        this.resultMenuWin.active = false;
        this.renderPendingItems();
        break;
      case RouletteState.ERROR:
        this.errorOverlay.active = true;
        this.errorOverlayAnim.play("error_fade_in");
        this.errorFadeOut();
        break;
    }
  }

  async errorFadeOut() {
    this.spinButton.interactable = false;
    await new Promise((resolve) => setTimeout(resolve, 2500));
    this.errorOverlayAnim.play("error_fade_out");
    await new Promise((resolve) => setTimeout(resolve, 2000));
    this.errorOverlay.active = false;
    this.spinButton.interactable = true;
  }

  onSpinButtonClicked() {
    if (this.inputGold.string === "") {
      if (this.placeholderGold.string === "") {
        this.errorLabel.string = "MINIMUM 10 GODL TO SPIN!";
        this.curSpinState = RouletteState.ERROR;
        return;
      }
    }
    var goldAmount = 0;
    if (this.inputGold.string === "") {
      goldAmount = this.stringToInt(this.placeholderGold.string);
    } else {
      goldAmount = this.stringToInt(this.inputGold.string);
    }
    sendAnalyticsEvent(
      "mgrl_start",
      "Spin and Shoot Button",
      "mgrl_start",
      goldAmount
    );

    this.allowRenderItems = false;
    console.log("spin button clicked");
    if (goldAmount < 10) {
      this.errorLabel.string = "MINIMUM 10 GODL TO SPIN!";
      this.curSpinState = RouletteState.ERROR;
      return;
    }
    if (this.parseNumber(this.playerGoldLabel.string) < goldAmount) {
      this.errorLabel.string = "INSUFFICIENT GOLD!";
      this.curSpinState = RouletteState.ERROR;
      return;
    }
    if (this.parseNumber(this.playerGoldLabel.string) < 10) {
      this.errorLabel.string = "INSUFFICIENT GOLD!";
      this.curSpinState = RouletteState.ERROR;
    } else {
      this.goldDeduct();
      console.log("gold decuted:", this.goldAmount);
      console.log("gold amount:", goldAmount);
      this.referralButton.interactable = false;
      this.rouletteButton.interactable = false;
      this.leaderboardButton.interactable = false;
      this.spinButton.interactable = false;
      this.howToPlayButton.interactable = false;
      this.roulettePlay(goldAmount, GlobalState.getUserData().telegram_id);
    }
  }

  onClickButtonOkay(event: Event, customEventData: string) {
    if (customEventData === "win") {
      this.fadeInMenu.getComponent(Animation).play("fade_out_result");
      sendAnalyticsEvent(
        "mgrl_replay_win",
        "Play Again Button",
        "mgrl_replay_win"
      );
    } else if (customEventData === "lose") {
      this.fadeInMenuRed.getComponent(Animation).play("fade_out_result_red");
      sendAnalyticsEvent(
        "mgrl_replay_lose",
        "Play Again Button",
        "mgrl_replay_lose"
      );
    }

    this.curSpinState = RouletteState.L_CLOSE;
    this.curSpinState = RouletteState.W_CLOSE;
    setTimeout(() => {
      this.resultMenuBackground.active = false;
      this.fadeInMenu.active = false;
      this.fadeInMenuRed.active = false;
    }, 500);
    this.referralButton.interactable = true;
    this.rouletteButton.interactable = true;
    this.leaderboardButton.interactable = true;
    this.spinButton.interactable = true;
    this.howToPlayButton.interactable = true;
    // this.spinAnimation.play("revolver_idle");

    tween(this.rouletteWheel)
      .repeatForever(tween().by(3, { angle: -360 }))
      .start();
    this.allowRenderItems = true;
  }

  onClickHowToPlay() {
    this.howToPlayOverlay.active = true;
    this.howToPlayButton.interactable = false;
    this.howToPlayOverlayAnim.play("how_to_play_fade_in");
  }

  onClickCloseHowToPlay() {
    this.howToPlayButton.interactable = true;
    this.howToPlayOverlayAnim.play("how_to_play_fade_out");
    setTimeout(() => {
      this.howToPlayOverlay.active = false;
    }, 500);
  }

  checkGoldAmount() {
    const goldAmount = this.stringToInt(this.inputGold.string);
    if (goldAmount < 10) {
      this.spinButton.interactable = false;
    }
  }

  goldDeduct() {
    this.goldAmount =
      this.parseNumber(this.playerGoldLabel.string) -
      this.parseNumber(this.inputGold.string);
    this.updateRouletteGold(this.formatNumber(this.goldAmount));
  }
}
