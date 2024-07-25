import { _decorator, Component, Label, Node } from 'cc';
const { ccclass, property } = _decorator;
import { trimString } from "../utils/StringUtils";

@ccclass('TrophySection')
export class TrophySection extends Component {
  @property({ type: Label }) firstPlaceLabel: Label | null = null;
  @property({ type: Label }) secondPlaceLabel: Label | null = null;
  @property({ type: Label }) thirdPlaceLabel: Label | null = null;

  init(topThreeUsernames) {
    if (this.firstPlaceLabel) {
      this.firstPlaceLabel.string = trimString(topThreeUsernames[0], 9);
    }
    if (this.secondPlaceLabel) {
      this.secondPlaceLabel.string = trimString(topThreeUsernames[1], 9);
    }
    if (this.thirdPlaceLabel) {
      this.thirdPlaceLabel.string = trimString(topThreeUsernames[2], 9);
    }
  }
}
