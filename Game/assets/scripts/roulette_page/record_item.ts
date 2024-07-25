import { _decorator, Component, Label } from "cc";
import { getRelativeTime } from "../utils/DateUtils";
import { RoulettePage } from "./roulette_page";
import { formatNumber } from "../utils/NumberUtils";
import { trimString } from "../utils/StringUtils";
const { ccclass, property } = _decorator;


enum RouletteRecordType {
  WIN,
  LOSE,
}

@ccclass("RecordItem")
export class RecordItem extends Component {
  @property({ type: Label }) recordLabel: Label | null = null;
  @property({ type: Label }) goldLabel: Label | null = null;
  @property({ type: Label }) dateLabel: Label | null = null;

  public goldAmount: number = 0;

  start() { }

  stringToInt(str: string): number {
    const num = parseInt(str, 10);
    if (isNaN(num)) {
      throw new Error("Invalid string format for conversion to integer");
    }
    return num;
  }

  init(data: {
    type: RouletteRecordType;
    username: string;
    outcome: number;
    timestamp: string;
  }) {
    if (this.recordLabel) {
      this.recordLabel.string =
        trimString(data.username, 8) +
        (data.type === RouletteRecordType.LOSE
          ? " got shot!"
          : " dodged the bullet!");
    }
    if (this.goldLabel) {
      this.goldLabel.string =
        data.type === RouletteRecordType.WIN
          ? "+" + (formatNumber(data.outcome * 2)).toString()
          : formatNumber(data.outcome).toString();
    }
    if (this.dateLabel) {
      this.dateLabel.string = getRelativeTime(data.timestamp);
    }
  }
}
