import {
  _decorator,
  Component,
  Label,
  Node,
  Prefab,
  Sprite,
  instantiate,
  Layout,
} from "cc";
import { trimString } from "../../utils/StringUtils";
const { ccclass, property } = _decorator;

@ccclass("CurrentUserReferralRecord")
export class CurrentUserReferralRecord extends Component {
  @property({ type: Label }) indexLabel: Label | null = null;
  @property({ type: Label }) usernameLabel: Label | null = null;
  @property({ type: Label }) referralCountLabel: Label | null = null;
  @property({ type: Node }) referralCountContainer: Node | null = null;
  @property({ type: Prefab }) avatarPrefab1: Prefab | null = null;
  @property({ type: Prefab }) avatarPrefab2: Prefab | null = null;
  @property({ type: Prefab }) avatarPrefab3: Prefab | null = null;
  @property({ type: Prefab }) avatarPrefab4: Prefab | null = null;
  @property({ type: Prefab }) avatarPrefab5: Prefab | null = null;
  @property({ type: Node }) prefabParentNode: Node | null = null;

  public referralCount: number = 0;
  public shufflePrefab: Sprite | null = null;

  start() {
    // this.avatarSprite1.node.active = false;
    // this.avatarSprite2.node.active = false;
    // this.avatarSprite3.node.active = false;
  }

  shuffleNumber(): number {
    let i = Math.floor(Math.random() * 100);
    return i % 5;
  }

  stringToInt(str: string): number {
    const num = parseInt(str, 10);
    if (isNaN(num)) {
      throw new Error("Invalid string format for conversion to integer");
    }
    return num;
  }

  init(data: { rank: number; username: string; referral_count: number }) {
    let userReferralCount = `${data.referral_count}`;

    this.referralCount = this.stringToInt(userReferralCount);
    const prefab = [
      this.avatarPrefab1,
      this.avatarPrefab2,
      this.avatarPrefab3,
      this.avatarPrefab4,
      this.avatarPrefab5,
    ];
    console.log("prefab", prefab);
    if (this.referralCount > 3) {
      for (let i = 0; i < 3; i++) {
        const shuffle = this.shuffleNumber();
        const avatar = instantiate(prefab[shuffle]);
        this.prefabParentNode.addChild(avatar);
      }
    } else {
      for (let i = 0; i < this.referralCount; i++) {
        const shuffle = this.shuffleNumber();
        const avatar = instantiate(prefab[shuffle]);
        this.prefabParentNode.addChild(avatar);
      }
    }
    if (this.indexLabel) {
      this.indexLabel.string = data.rank.toString();
    }
    if (this.usernameLabel) {
      this.usernameLabel.string = trimString(data.username, 20);
    }
    if (this.referralCount === 0) {
      this.referralCountLabel.string = "0";
    } else if (this.referralCount && this.referralCountLabel) {
      if (this.referralCount === 1) {
        this.prefabParentNode.setPosition(139, 0);
      } else if (this.referralCount === 2) {
        this.prefabParentNode.setPosition(117, 0);
      }
      this.referralCountLabel.string = `${this.referralCount}`;
    }
  }
}
