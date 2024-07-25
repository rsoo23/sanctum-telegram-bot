import { _decorator, Component, Node, Material, Vec2, view, Sprite } from "cc";
const { ccclass, property } = _decorator;

@ccclass("BlurController")
export default class BlurController extends Component {
  @property(Material)
  blurMaterial: Material = null;

  @property(Node)
  targetNode: Node = null;

  start() {
    if (this.blurMaterial && this.targetNode) {
      const resolution = view.getVisibleSize();
      const radius = 2.0; // Adjust the radius as needed
      const strength = 0.5; // Adjust the strength as needed

      // Create a new material instance
      const materialInstance = new Material();
      materialInstance.copy(this.blurMaterial);

      materialInstance.setProperty(
        "resolution",
        new Vec2(resolution.width, resolution.height)
      );
      materialInstance.setProperty("radius", radius);
      materialInstance.setProperty("strength", strength);

      const sprite = this.targetNode.getComponent(Sprite);
      if (sprite) {
        sprite.sharedMaterials[0] = materialInstance;
      }
    }
  }
}
