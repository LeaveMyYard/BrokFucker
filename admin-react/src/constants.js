export const URL = "http://localhost:5000/api/v1/";

export const BASE_HREF = "/admin";

export function encData() {
  return window.btoa(
    localStorage.getItem("email") +
      ":" +
      window.atob(localStorage.getItem("password"))
  );
}
