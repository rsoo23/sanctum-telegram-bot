import { _decorator, Component, game, director } from "cc";
import GlobalState from "./state/GlobalState";
const { ccclass, property } = _decorator;

@ccclass("Router")
export class Router extends Component {
  onLoad() {}

  static navigateTo(hash: string) {
    window.location.hash = hash + `?user_id=${GlobalState.getUserIdFromHash()}`;
  }
}
