import { URL } from "../constants";

class AuthService {
  isAuthenticated() {
    return !!localStorage.getItem("email");
  }

  getAuthToken() {
    const email = localStorage.getItem("email");
    const password = window.atob(localStorage.getItem("password"));
    const userData = `${email}:${password}`;
    const authToken = this.createAuthToken(userData);

    return authToken;
  }

  createAuthToken(userData) {
    return window.btoa(userData);
  }

  async login({ email, password }) {
    const userData = `${email}:${password}`;
    const authToken = this.createAuthToken(userData);

    try {
      const response = await fetch(URL + "user", {
        method: "GET",
        headers: { Authorization: `Basic ${authToken}` },
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.msg);
      }
      if (result.type === "user" || result.type === "moderator") {
        localStorage.setItem("role", result.type);
        localStorage.setItem("email", result.email);
        localStorage.setItem("password", window.btoa(password));
      } else {
        //error msg for users
      }
    } catch (error) {
      throw error;
    }
  }

  async logout() {}
}

export default new AuthService();
