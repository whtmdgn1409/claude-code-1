import Link from 'next/link';
import AuthPanel from '@/components/AuthPanel';
import BoardFeed from '@/components/BoardFeed';
import BoardFilters from '@/components/BoardFilters';
import { getCategories, getDeals, getSources } from '@/lib/api';
import { normalizeQuery } from '@/lib/deals';

export const revalidate = 120;

export default async function HomePage({ searchParams }) {
  const toFriendlyError = (error) => {
    if (!error) return '게시판 데이터를 불러오지 못했습니다.';

    const message = String(error.message || '');
    if (message.includes('API request failed: 404')) {
      return '요청한 API 경로를 찾지 못했습니다. NEXT_PUBLIC_API_BASE_URL을 확인해 주세요.';
    }

    if (message.includes('fetch failed') || message.includes('ECONNREFUSED')) {
      return '백엔드 API에 연결할 수 없습니다. 서버가 실행 중인지/도메인이 맞는지 확인해 주세요.';
    }

    return message || '게시판 데이터를 불러오는 중 알 수 없는 오류가 발생했습니다.';
  };

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

  let safeDeals = [];
  let safeTotalPages = 1;
  let sources = [];
  let categories = [];
  let boardError = '';

  try {
    const [dealsData, sourceData, categoryData] = await Promise.all([
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

    safeDeals = dealsData?.deals || [];
    safeTotalPages = Math.max(1, dealsData?.total_pages || 1);
    sources = sourceData || [];
    categories = categoryData || [];
  } catch (error) {
    boardError = toFriendlyError(error);
  }

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
      {boardError ? <p className="error-state">{boardError}</p> : null}
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
