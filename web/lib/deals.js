export const PAGE_SIZE = 20;

export const SORT_BY = ['hot_score', 'published_at', 'price', 'bookmark_count'];
export const ORDER = ['asc', 'desc'];

export const normalizeText = (value) => {
  if (Array.isArray(value)) return value[0] ?? '';
  return value || '';
};

export const toPositiveInt = (value, fallback = 1) => {
  const n = Number(value);
  if (!Number.isInteger(n) || n < 1) return fallback;
  return n;
};

export const normalizeQuery = (query = {}) => {
  const page = toPositiveInt(query.page, 1);
  const pageSize = Math.min(toPositiveInt(query.pageSize || query.page_size, PAGE_SIZE), 100);
  const keyword = normalizeText(query.keyword).trim();

  const sortBy = SORT_BY.includes(normalizeText(query.sort_by || query.sortBy))
    ? normalizeText(query.sort_by || query.sortBy)
    : SORT_BY[0];

  const order = ORDER.includes(normalizeText(query.order)) ? normalizeText(query.order) : ORDER[1];

  return {
    page,
    page_size: pageSize,
    source_id: normalizeText(query.sourceId || query.source_id),
    category_id: normalizeText(query.categoryId || query.category_id),
    sort_by: sortBy,
    order,
    keyword: keyword.length >= 2 ? keyword : '',
  };
};

export const buildDealParams = (query = {}) => {
  const normalized = normalizeQuery(query);
  return {
    page: normalized.page,
    page_size: normalized.page_size,
    source_id: normalized.source_id || undefined,
    category_id: normalized.category_id || undefined,
    sort_by: normalized.sort_by,
    order: normalized.order,
    ...(normalized.keyword ? { keyword: normalized.keyword } : {}),
  };
};

export const buildDealPath = (query = {}) => {
  const { keyword } = normalizeQuery(query);
  return keyword ? '/deals/search' : '/deals';
};
