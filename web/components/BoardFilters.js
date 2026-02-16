'use client';

import { useMemo } from 'react';

const SORT_OPTIONS = [
  { value: 'hot_score', label: '인기 순' },
  { value: 'published_at', label: '최신 순' },
  { value: 'price', label: '가격 순' },
  { value: 'bookmark_count', label: '스크랩 순' },
];

const BoardFilters = ({ query, sources, categories }) => {
  const sourceOptions = useMemo(
    () => [
      { value: '', label: '전체 커뮤니티' },
      ...sources.map((item) => ({ value: String(item.id), label: item.display_name || item.name })),
    ],
    [sources],
  );

  const categoryOptions = useMemo(
    () => [
      { value: '', label: '전체 카테고리' },
      ...categories.map((item) => ({ value: String(item.id), label: item.name })),
    ],
    [categories],
  );

  return (
    <form method="get" className="filter-wrap">
      {query.theme ? <input type="hidden" name="theme" value={query.theme} /> : null}
      <input
        name="q"
        placeholder="딜 제목/상품명 검색 (2자 이상)"
        aria-label="딜 검색"
        defaultValue={query.q || ''}
        minLength={2}
        maxLength={80}
        inputMode="search"
      />
      <select name="sort_by" defaultValue={query.sort_by || 'hot_score'} aria-label="정렬 기준">
        {SORT_OPTIONS.map((option) => (
          <option value={option.value} key={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <select name="order" defaultValue={query.order || 'desc'} aria-label="정렬 방향">
        <option value="desc">내림차순</option>
        <option value="asc">오름차순</option>
      </select>
      <select name="source_id" defaultValue={query.source_id || ''} aria-label="커뮤니티 필터">
        {sourceOptions.map((option) => (
          <option value={option.value} key={`source-${option.value}`}>
            {option.label}
          </option>
        ))}
      </select>
      <select name="category_id" defaultValue={query.category_id || ''} aria-label="카테고리 필터">
        {categoryOptions.map((option) => (
          <option value={option.value} key={`category-${option.value}`}>
            {option.label}
          </option>
        ))}
      </select>
      <button type="submit" aria-label="게시판 조회">
        조회
      </button>
    </form>
  );
};

export default BoardFilters;
