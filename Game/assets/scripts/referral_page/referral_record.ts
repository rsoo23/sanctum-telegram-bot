import { _decorator, CCInteger, Component, Label, Node } from "cc";
import { formatDate } from "../utils/DateUtils";
import { trimString } from "../utils/StringUtils";
const { ccclass, property } = _decorator;

@ccclass("ReferralRecord")
export class ReferralRecord extends Component {
  @property({ type: Label }) indexLabel: Label | null = null;
  @property({ type: Label }) nameLabel: Label | null = null;
  @property({ type: Label }) rewardLabel: Label | null = null;
  @property({ type: Label }) dateLabel: Label | null = null;

  start() { }

  init(data: { index: number; referred: string; created_at: string, amount: number}) {
    if (this.indexLabel) {
      this.indexLabel.string = data.index.toString();
    }
    if (this.nameLabel) {
      this.nameLabel.string = trimString(data.referred, 20);
    }
    if (this.rewardLabel) {
	  
      this.rewardLabel.string = data.amount.toString();
    }
    if (this.dateLabel) {
      this.dateLabel.string = formatDate(data.created_at);
    }
  }
}
