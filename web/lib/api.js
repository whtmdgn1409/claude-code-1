import { cache } from 'react';
import { buildDealParams, buildDealPath } from '@/lib/deals';

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

const toNumber = (value, fallback = null) => {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
};

const requestJSON = async (path, options = {}, params = {}) => {
  const query = buildSearchParams(params);
  const url = `${API_BASE_URL}${path}${query ? `?${query}` : ''}`;
  const { revalidate, ...fetchOptions } = options || {};
  const next = {
    ...(fetchOptions.next || {}),
  };

  if (Number.isFinite(revalidate) && revalidate >= 0) {
    next.revalidate = revalidate;
  }

  const response = await fetch(url, {
    ...fetchOptions,
    ...(Object.keys(next).length ? { next } : {}),
    headers: {
      accept: 'application/json',
      ...(fetchOptions.headers || {}),
    },
  });

  if (!response.ok) {
    let detail = `API request failed: ${response.status}`;
    try {
      const body = await response.json();
      detail = body?.detail || JSON.stringify(body) || detail;
    } catch {
      // no-op
    }

    const error = new Error(detail);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
};

export const getDeals = async (query = {}) => {
  return requestJSON(buildDealPath(query), { revalidate: 60 }, buildDealParams(query));
};

export const getSources = cache(async () => requestJSON('/sources', { revalidate: 300 }, { is_active: true }));

export const getCategories = cache(async () => requestJSON('/categories', { revalidate: 300 }, { is_active: true }));

export const getDeal = async (id) => {
  const dealId = toNumber(id);
  if (!dealId) {
    const error = new Error('Invalid deal id');
    error.status = 400;
    throw error;
  }
  return requestJSON(`/deals/${dealId}`, {
    cache: 'no-store',
  });
};

export const getDealSummary = async (id) => {
  const dealId = toNumber(id);
  if (!dealId) return null;
  return requestJSON(`/deals/${dealId}/summary`, { cache: 'no-store' });
};
