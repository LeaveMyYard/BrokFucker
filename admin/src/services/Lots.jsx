import authService from "./Auth";
import { URL } from "../constants";

class LotsService {
  async getLots() {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + "lots/unapproved", {
        method: "GET",
        headers: { Authorization: `Basic ${authToken}` },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }
      console.log(response);
      const result = await response.json();
      return result;
    } catch (error) {
      throw error;
    }
  }

  async guaranteeLots() {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + "lots/requested/guarantee", {
        method: "GET",
        headers: { Authorization: `Basic ${authToken}` },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }
      console.log(response);
      const result = await response.json();
      return result;
    } catch (error) {
      throw error;
    }
  }

  async verificationLots() {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(
        URL + "lots/requested/security_verification",
        {
          method: "GET",
          headers: { Authorization: `Basic ${authToken}` },
        }
      );

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }
      console.log(response);
      const result = await response.json();
      return result;
    } catch (error) {
      throw error;
    }
  }
}

export default new LotsService();
