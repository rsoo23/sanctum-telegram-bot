import EnvLoader from "../utils/EnvLoader";

export default class ApiService {
  private static endpoint: string;

  static async init() {
    await EnvLoader.loadConfig();
    this.endpoint = EnvLoader.get("API_URL");
  }

  static async request(
    method: string,
    path: string,
    body: any = null,
    headers: Record<string, string> = {}
  ): Promise<any> {
    try {
      const options: RequestInit = {
        method: method,
        headers: {
          "Content-Type": "application/json",
          ...headers,
        },
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      if (!this.endpoint) {
        await this.init();
      }
      console.log(`Endpoint: ${this.endpoint}${path}`);

      const response = await fetch(`${this.endpoint}${path}`, options);
      console.log(`Response status: ${response.status}`);

      if (!response) {
        throw new Error(`Network response was not ok: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(
        `There has been a problem with your ${method} request:`,
        error
      );
    }
  }

  static get(path: string, headers: Record<string, string> = {}): Promise<any> {
    return this.request("GET", path, null, headers);
  }

  static post(
    path: string,
    body: any,
    headers: Record<string, string> = {}
  ): Promise<any> {
    return this.request("POST", path, body, headers);
  }

  static put(
    path: string,
    body: any,
    headers: Record<string, string> = {}
  ): Promise<any> {
    return this.request("PUT", path, body, headers);
  }

  static delete(
    path: string,
    headers: Record<string, string> = {}
  ): Promise<any> {
    return this.request("DELETE", path, null, headers);
  }
}
