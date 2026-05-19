import Cookies from 'js-cookie';

const TOKEN_KEY = 'docuguard_auth_token';
const USER_ROLE_KEY = 'docuguard_user_role';

export const setAuthToken = (token: string, role: string) => {
  Cookies.set(TOKEN_KEY, token, { expires: 1 }); // 1 day
  Cookies.set(USER_ROLE_KEY, role, { expires: 1 });
};

export const getAuthToken = () => {
  return Cookies.get(TOKEN_KEY);
};

export const getUserRole = () => {
  return Cookies.get(USER_ROLE_KEY);
};

export const removeAuthToken = () => {
  Cookies.remove(TOKEN_KEY);
  Cookies.remove(USER_ROLE_KEY);
};

export const isAuthenticated = () => {
  return !!getAuthToken();
};

export const isAdmin = () => {
  return getUserRole() === 'admin';
};
