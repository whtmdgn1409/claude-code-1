const DEFAULT_API_BASE = 'http://localhost:8000/api/v1';
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE).replace(/\/$/, '');

const buildSearchParams = (params) => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined || value === '') return;
    searchParams.set(key, String(value));
  });
  return searchParams.toString();
};

const resolveToken = (token) => {
  if (token) return token;
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('dealmoa_access_token');
};

const buildUrl = (path, params = {}) => {
  const query = buildSearchParams(params);
  return `${API_BASE_URL}${path}${query ? `?${query}` : ''}`;
};

const parseError = async (response) => {
  let detail = `API request failed: ${response.status}`;
  try {
    const body = await response.json();
    detail = body?.detail || JSON.stringify(body) || detail;
  } catch {
    // no-op
  }
  const error = new Error(detail);
  error.status = response.status;
  return error;
};

const request = async (path, options = {}) => {
  const {
    token,
    params,
    body,
    method = 'GET',
    headers = {},
    ...rest
  } = options;

  const authToken = resolveToken(token);
  const response = await fetch(buildUrl(path, params), {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(headers || {}),
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
    ...rest,
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  if (response.status === 204) return null;
  return response.json();
};

export const getDealPage = async (query = {}) => {
  const params = {
    page: query.page || 1,
    page_size: query.page_size || query.pageSize || 20,
    source_id: query.source_id,
    category_id: query.category_id,
    sort_by: query.sort_by,
    order: query.order,
    ...(query.keyword || query.q ? { keyword: query.keyword || query.q } : {}),
  };

  const path = query.keyword || query.q ? '/deals/search' : '/deals';
  return request(path, { params, token: query.token });
};

export const loginUser = async (email, password) =>
  request('/users/login', {
    method: 'POST',
    body: { email, password },
    token: null,
  });

export const registerUser = async ({ email, password, username, displayName = null }) =>
  request('/users/register', {
    method: 'POST',
    body: {
      email,
      password,
      username: username || email?.split('@')[0],
      display_name: displayName,
    },
    token: null,
  });

export const getMe = async (token) =>
  request('/users/me', {
    token,
  });

export const listBookmarks = async ({ page = 1, page_size = 100, token }) =>
  request('/bookmarks', {
    params: {
      page,
      page_size,
    },
    token,
  });

export const createBookmark = async (dealId, token) =>
  request('/bookmarks', {
    method: 'POST',
    token,
    body: {
      deal_id: Number(dealId),
    },
  });

export const deleteBookmark = async (bookmarkId, token) =>
  request(`/bookmarks/${bookmarkId}`, {
    method: 'DELETE',
    token,
  });
