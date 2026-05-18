const ACCESS_TOKEN_KEY = "pep_tracker_access_token";
const REFRESH_TOKEN_KEY = "pep_tracker_refresh_token";
const USER_KEY = "pep_tracker_user";

export function saveAuth({ access, refresh, user }) {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  if (refresh) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  }
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getUser() {
  const value = localStorage.getItem(USER_KEY);
  return value ? JSON.parse(value) : null;
}

export function logout() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
