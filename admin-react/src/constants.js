export const URL = "/api/v1/";

export const BASE_HREF = "/admin";

export function encData() {
  return (
    window.btoa(localStorage.getItem("email") + ":") +
    localStorage.getItem("password")
  );
}