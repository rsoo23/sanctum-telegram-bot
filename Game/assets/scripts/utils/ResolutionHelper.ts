import {
  _decorator,
  Component,
  Canvas,
  view,
  Node,
  Vec3,
  ResolutionPolicy,
} from "cc";
const { ccclass, property } = _decorator;

@ccclass("ResolutionHelper")
export class ResolutionHelper extends Component {
  public static adjustResolution(canvasNode: Node) {
    const canvas = canvasNode.getComponent(Canvas);
    if (!canvas) {
      console.error("No Canvas component found on the node");
      return;
    }

    const frameSize = view.getVisibleSize();
    const designResolution = view.getDesignResolutionSize();

    const screenRatio = frameSize.width / frameSize.height;
    const designRatio = designResolution.width / designResolution.height;

    canvas.node.setScale(new Vec3(1, 1, 1));

    if (screenRatio > designRatio) {
      view.setResolutionPolicy(ResolutionPolicy.FIXED_HEIGHT);
    } else {
      view.setResolutionPolicy(ResolutionPolicy.FIXED_WIDTH);
    }
  }
}
