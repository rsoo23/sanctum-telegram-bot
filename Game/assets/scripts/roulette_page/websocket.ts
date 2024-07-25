import { _decorator, Component, EventTarget } from "cc";
import EnvLoader from "../utils/EnvLoader";
const { ccclass, property } = _decorator;

interface Spin {
  user: string;
  result: string;
  timestamp: number;
}

@ccclass("WebSocketComponent")
export class WebSocketComponent extends Component {
  private socket: WebSocket | null = null;
  private baseUrl: string;

  public static eventTarget = new EventTarget();

  async onLoad() {
    await EnvLoader.loadConfig();
    this.baseUrl = EnvLoader.get("WEBSOCKET_URL");

    this.socket = new WebSocket(`${this.baseUrl}/ws/roulette/`);

    this.socket.addEventListener("open", (event) => {
      console.log("Connected to the WebSocket server");

      this.socket?.send("receive");
    });

    this.socket.addEventListener("message", (event) => {
      const data = event.data;
      console.log("Message from server:", data);

      this.processMessage(data);
    });

    this.socket.addEventListener("error", (event) => {
      console.error("WebSocket error:", event);
    });

    this.socket.addEventListener("close", (event) => {
      console.log("WebSocket connection closed:", event);
    });
  }

  private processMessage(message: string) {
    try {
      const data = JSON.parse(message);
      if (Array.isArray(data.games)) {
        this.processSpinArray(data.games);
      } else {
        this.processSingleSpin(data);
      }
    } catch (e) {
      console.error("Error parsing message:", e);
    }
  }

  private processSingleSpin(spin: Spin) {
    WebSocketComponent.eventTarget.emit("spin", spin);
  }

  private processSpinArray(spinArray: Spin[]) {
    WebSocketComponent.eventTarget.emit("spinArray", spinArray);
  }

  onDestroy() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
