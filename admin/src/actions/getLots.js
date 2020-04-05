import { URL, encData } from "../constants";

export const getLots = async () => {
    const response = await fetch(URL + "lots/unapproved", {
      method: "GET",
      headers: { Authorization: `Basic ${encData}` },
    });

    if (!response.ok) {
      return new Error("Unsuccessfull response");
    } else {
      return await response.json();
    }
  } catch (error) {
    console.error(error);
  }
};
