import ApiClient from "../api/ApiClient";

export default class GlobalState {
  private static userData: User | null = null;

  static setUserData(data: User): void {
    this.userData = data;
  }

  static getUserData(): User | null {
    return this.userData;
  }

  static getUserIdFromHash() {
    const hash = window.location.hash;
    const hashParams = new URLSearchParams(hash.split("?")[1]);
    return hashParams.get("user_id") || "";
  }

  static async loadUserData(): Promise<User | null> {
    try {
	//   const telegramId = "123";
      const telegramId = this.getUserIdFromHash();

      const userData = await ApiClient.users.getUser(telegramId);
      console.log("user data:", userData);
      if (userData) {
        this.setUserData(userData);
        console.log(
          "User data loaded and stored globally:",
          this.getUserData()
        );
        return userData;
      } else {
        console.log("Failed to load user data.");
        return null;
      }
    } catch (error) {
      console.error("Error loading user data:", error);
      return null;
    }
  }
}
