import Link from 'next/link';
import AuthPanel from '@/components/AuthPanel';
import BoardFeed from '@/components/BoardFeed';
import BoardFilters from '@/components/BoardFilters';
import { getCategories, getDeals, getSources } from '@/lib/api';
import { normalizeQuery } from '@/lib/deals';

export const revalidate = 120;

export default async function HomePage({ searchParams }) {
  const normalized = normalizeQuery({
    page: searchParams?.page,
    pageSize: 20,
    keyword: searchParams?.q,
    sort_by: searchParams?.sort_by,
    sortBy: searchParams?.sort_by,
    order: searchParams?.order,
    source_id: searchParams?.source_id,
    category_id: searchParams?.category_id,
  });

  const query = {
    ...normalized,
    q: normalized.keyword,
    sort_by: normalized.sort_by,
    order: normalized.order,
    source_id: normalized.source_id,
    category_id: normalized.category_id,
    page: normalized.page,
  };

  const [dealsData, sources, categories] = await Promise.all([
    getDeals({
      page: query.page,
      pageSize: query.page_size,
      keyword: query.q,
      sourceId: query.source_id || undefined,
      categoryId: query.category_id || undefined,
      sortBy: query.sort_by,
      order: query.order,
    }),
    getSources(),
    getCategories(),
  ]);

  const safeDeals = dealsData?.deals ?? [];
  const safeTotalPages = Math.max(1, dealsData?.total_pages || 1);
  const searchHint = query.q && query.q.length > 0 && query.q.length < 2
    ? '검색어는 2자 이상으로 입력하세요. 현재는 전체 목록으로 전환됩니다.'
    : '';

  const buildPageUrl = (page) => {
    const nextSearchParams = new URLSearchParams();

    nextSearchParams.set('q', query.q || '');
    nextSearchParams.set('sort_by', query.sort_by || '');
    nextSearchParams.set('order', query.order || 'desc');
    nextSearchParams.set('source_id', query.source_id || '');
    nextSearchParams.set('category_id', query.category_id || '');
    nextSearchParams.set('page', String(page));

    return `/?${nextSearchParams.toString()}`;
  };

  return (
    <main>
      <header className="board-header">
        <h1 className="board-title">딜모아 게시판</h1>
        <p className="board-subtitle">기존 API를 기반으로 구축한 실시간 핫딜 보드</p>
        <BoardFilters query={query} sources={sources} categories={categories} />
        <AuthPanel />
      </header>
      <noscript>
        <nav className="board-pagination">
          {query.page > 1 ? (
            <Link href={buildPageUrl(query.page - 1)}>이전 페이지</Link>
          ) : (
            <span className="disabled">이전 페이지</span>
          )}
          <span>
            {query.page} / {safeTotalPages}
          </span>
          {query.page < safeTotalPages ? (
            <Link href={buildPageUrl(query.page + 1)}>다음 페이지</Link>
          ) : (
            <span className="disabled">다음 페이지</span>
          )}
        </nav>
      </noscript>
      {searchHint ? <p className="error-state">{searchHint}</p> : null}
      <BoardFeed
        initialDeals={safeDeals}
        totalPages={safeTotalPages}
        query={{ ...query, q: query.q, page_size: query.page_size }}
        initialPage={query.page}
      />
    </main>
  );
}
