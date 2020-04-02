import { URL } from "../constants";

export const getLots = async () => {
  try {
    const response = await fetch(URL + "lots/unapproved", {
      method: "GET"
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
