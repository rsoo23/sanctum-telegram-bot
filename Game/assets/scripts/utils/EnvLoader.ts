import { _decorator, JsonAsset, resources, error } from "cc";

enum Environment {
  Local = "local",
  Staging = "staging",
  Production = "production",
}

class EnvLoader {
  private static environment: Environment =
    ((window as any).ENV as Environment) || Environment.Local; // Read from global variable set in index.html
  private static config: any;

  public static setEnvironment(env: string) {
    if (env in Environment) {
      this.environment = env as Environment;
    } else {
      throw new Error(`Invalid environment: ${env}`);
    }
  }

  public static async loadConfig() {
    return new Promise((resolve, reject) => {
      const configPath = `config/env.${this.environment}`;
      resources.load(configPath, JsonAsset, (err, jsonAsset) => {
        if (err) {
          error("Failed to load JSON file:", err);
          reject(err);
          return;
        }
        this.config = jsonAsset.json;
        resolve(this.config);
      });
    });
  }

  public static get(key: string): any {
    return this.config ? this.config[key] : null;
  }
}

export default EnvLoader;
