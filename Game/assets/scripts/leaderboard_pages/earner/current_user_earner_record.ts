import { _decorator, Component, Label, Node, Sprite } from 'cc';
const { ccclass, property } = _decorator;
import { trimString } from "../../utils/StringUtils";
import { formatNumber } from '../../utils/NumberUtils';

@ccclass('CurrentUserEarnerRecord')
export class CurrentUserEarnerRecord extends Component {
  @property({ type: Label }) rankLabel: Label | null = null;
  @property({ type: Label }) nameLabel: Label | null = null;
  @property({ type: Label }) totalGoldLabel: Label | null = null;

  start() {}

  init(data: { rank: number; username: string; gold: number }) {
    console.log("rank: ", data.rank, " username: ", data.username, "gold: ", data.gold)
    if (this.rankLabel) {
      this.rankLabel.string = data.rank.toString();
    }
    if (this.nameLabel) {
      this.nameLabel.string = trimString(data.username, 20);
    }
    if (this.totalGoldLabel) {
      this.totalGoldLabel.string = formatNumber(data.gold);
    }
  }
}
