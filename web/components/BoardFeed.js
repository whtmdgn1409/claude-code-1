'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getDealPage } from '@/lib/client-api';
import DealCard from '@/components/DealCard';
import { buildDealParams } from '@/lib/deals';

const toErrorMessage = (error) => error?.message || '요청을 처리할 수 없습니다.';

export default function BoardFeed({ initialDeals, totalPages, query, initialPage }) {
  const [deals, setDeals] = useState(() => initialDeals || []);
  const [currentPage, setCurrentPage] = useState(initialPage || 1);
  const [hasMore, setHasMore] = useState(Boolean((initialPage || 1) < (totalPages || 1)));
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState('');
  const sentinelRef = useRef(null);

  const requestParams = useMemo(() => {
    const params = buildDealParams({
      ...query,
      page: 1,
      page_size: Number(query?.page_size) || 20,
    });

    return params;
  }, [query]);

  const totalPageByServer = useMemo(() => {
    return Math.max(1, Number(totalPages || 1));
  }, [totalPages]);

  const detailQueryString = useMemo(() => {
    const params = new URLSearchParams();
    const append = (key, value) => {
      if (value === undefined || value === null || value === '') return;
      params.set(key, String(value));
    };

    append('q', query?.q || '');
    append('sort_by', query?.sort_by || '');
    append('order', query?.order || '');
    append('source_id', query?.source_id || '');
    append('category_id', query?.category_id || '');
    append('theme', query?.theme || '');
    append('page', currentPage);
    return params.toString();
  }, [currentPage, query]);

  const appendDeals = useCallback((items = []) => {
    if (!items.length) return;
    setDeals((prev) => {
      const existingIds = new Set(prev.map((item) => item.id));
      const merged = [...prev];

      items.forEach((item) => {
        if (!existingIds.has(item.id)) {
          merged.push(item);
        }
      });

      return merged;
    });
  }, []);

  const loadNextPage = useCallback(async () => {
    if (!hasMore || isLoading) return;

    setIsLoading(true);
    setLoadError('');
    try {
      const nextPage = currentPage + 1;
      const data = await getDealPage({
        ...requestParams,
        page: nextPage,
      });

      appendDeals(data?.deals || []);
      const newPage = data?.page || nextPage;
      setCurrentPage(newPage);
      setHasMore(newPage < (data?.total_pages || newPage));
    } catch (error) {
      setLoadError(toErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [appendDeals, currentPage, hasMore, isLoading, requestParams]);

  useEffect(() => {
    setCurrentPage(initialPage || 1);
    setDeals(initialDeals || []);
    setHasMore(Boolean((initialPage || 1) < totalPageByServer));
    setLoadError('');
  }, [initialDeals, initialPage, totalPageByServer]);

  useEffect(() => {
    if (!hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const target = entries[0];
        if (!target) return;
        if (target.isIntersecting) {
          loadNextPage();
        }
      },
      {
        rootMargin: '0px 0px 320px 0px',
        threshold: 0,
      },
    );

    if (sentinelRef.current) observer.observe(sentinelRef.current);

    return () => observer.disconnect();
  }, [hasMore, loadNextPage]);

  if (!deals.length) {
    return <p className="empty">표시할 딜이 없습니다.</p>;
  }

  return (
    <>
      <section className="board-grid">
        {deals.map((deal) => (
          <DealCard key={deal.id} deal={deal} detailQueryString={detailQueryString} />
        ))}
      </section>

      {loadError ? <p className="error-state">{loadError}</p> : null}
      <div
        ref={sentinelRef}
        className={`board-sentinel ${isLoading ? 'loading' : ''}`}
        aria-live="polite"
      >
        {isLoading
          ? '다음 페이지를 불러오는 중...'
          : hasMore
            ? '아래로 스크롤하면 더 불러옵니다'
            : '모든 딜을 확인했습니다.'}
      </div>
    </>
  );
}
