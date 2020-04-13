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

  async getLotsArchive() {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + "lots/archive", {
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

  async approve(lot) {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + `lots/${lot.id}/approve`, {
        method: "PUT",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }

      return await response.json();
    } catch (error) {
    } finally {
      // await refreshList();
    }
  }

  async remove(lot) {
    try {
      const authToken = authService.getAuthToken();
      // const reason = document.getElementById("declineReason").value;
      const reason = { reason: "Лот не подходит под стандарты." };
      const response = await fetch(URL + `lots/unapproved/${lot.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(reason),
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }

      return await response.json();
    } catch (error) {
    } finally {
      // await refreshList();
    }
  }

  async guaranteeApprove(lot) {
    try {
      const authToken = authService.getAuthToken();
      let guarantee = lot.guarantee_percentage;
      if (guarantee < 0) {
        guarantee = 0;
      }
      if (guarantee > 100) {
        guarantee = 100;
      }
      const response = await fetch(URL + `lots/${lot.id}/guarantee`, {
        method: "PUT",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ value: guarantee }),
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }

      return await response.json();
    } catch (error) {
    } finally {
      // await refreshList();
    }
  }

  async guaranteeRemove(lot) {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + `lots/${lot.id}/guarantee`, {
        method: "DELETE",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }

      return await response.json();
    } catch (error) {
    } finally {
      // await refreshList();
    }
  }

  async getApprovedSubscriptions() {
    try {
      const authToken = authService.getAuthToken();
      const response = await fetch(URL + "lots/subscription/approved", {
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

  async getUnapprovedSubscriptions() {
    try {
      const authToken = authService.getAuthToken();
      const response = await fetch(URL + "lots/subscription/unapproved", {
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

  async securityCheckApprove(lot) {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + `lots/${lot.id}/security`, {
        method: "PUT",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }

      return await response.json();
    } catch (error) {
    } finally {
      // await refreshList();
    }
  }

  async securityCheckDecline(lot) {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + `lots/${lot.id}/security`, {
        method: "DELETE",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }

      return await response.json();
    } catch (error) {
    } finally {
      // await refreshList();
    }
  }
}

export default new LotsService();
