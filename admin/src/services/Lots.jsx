import authService from "./Auth";

class LotsService {
  async getLots(...args /** TODO: USE ARGS LIKE `query` etc. */) {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + "lots/unapproved", {
        method: "GET",
        headers: { Authorization: `Basic ${authToken}` },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  }
}

export default new LotsService();
