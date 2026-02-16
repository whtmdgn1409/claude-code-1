import Link from 'next/link';
import Image from 'next/image';
import { currencyKRW, relativeTimeFromNow } from '@/lib/format';
import { getDeal, getDealSummary } from '@/lib/api';
import PriceHistoryChart from '@/components/PriceHistoryChart';

const THEME_OPTIONS = [
  { value: 'calm', label: 'calm' },
  { value: 'bold', label: 'bold' },
  { value: 'neutral', label: 'neutral' },
];
const DEFAULT_THEME = 'calm';

const normalizeQueryValue = (value) => {
  if (Array.isArray(value)) return value[0];
  return value;
};

const normalizeThemeValue = (value) => {
  const normalized = normalizeQueryValue(value);
  if (normalized === 'coast') return 'calm';
  if (normalized === 'sunset') return 'bold';
  if (normalized === 'graphite') return 'neutral';
  if (THEME_OPTIONS.some((option) => option.value === normalized)) {
    return normalized;
  }
  return DEFAULT_THEME;
};

const buildBackUrl = ({ searchParams }) => {
  if (!searchParams) return '/';
  const nextParams = new URLSearchParams();

  Object.entries(searchParams).forEach(([key, value]) => {
    const normalized = normalizeQueryValue(value);
    if (normalized === undefined || normalized === null || normalized === '') return;
    nextParams.set(key, String(normalized));
  });

  const query = nextParams.toString();
  return query ? `/?${query}` : '/';
};

const buildThemeHref = ({ id, searchParams, theme }) => {
  const nextParams = new URLSearchParams();

  Object.entries(searchParams || {}).forEach(([key, value]) => {
    const normalized = normalizeQueryValue(value);
    if (normalized === undefined || normalized === null || normalized === '') return;
    nextParams.set(key, String(normalized));
  });
  nextParams.set('theme', theme);
  return `/deals/${id}?${nextParams.toString()}`;
};

export async function generateMetadata({ params }) {
  const id = Number(params.id);
  const title = Number.isInteger(id) ? `딜 ${id} 상세` : '딜 상세';
  return {
    title,
    description: 'DealMoa 핫딜 게시글 상세 보기',
  };
}

export default async function DealDetailPage({ params, searchParams }) {
  const id = Number(params.id);
  const backUrl = buildBackUrl({ searchParams: searchParams || {} });
  const theme = normalizeThemeValue(searchParams?.theme);
  let deal = null;
  let summary = null;
  let loadError = '';

  try {
    const [dealData, summaryData] = await Promise.all([
      getDeal(id),
      getDealSummary(id).catch(() => null),
    ]);
    deal = dealData;
    summary = summaryData;
  } catch (error) {
    loadError = error?.message || '딜 상세 조회 중 오류가 발생했습니다.';
  }

  if (loadError) {
    return (
      <main className="detail-main detail-shell theme-calm">
        <h1>딜 상세를 표시할 수 없습니다</h1>
        <p className="error-state" role="alert">
          {loadError}
        </p>
        <div className="actions">
          <Link href="/" className="btn btn-primary">
            목록으로
          </Link>
        </div>
      </main>
    );
  }

  if (!deal) {
    return (
      <main className="detail-main detail-shell theme-calm">
        <h1>딜 상세를 표시할 수 없습니다</h1>
        <p className="error-state">딜 데이터가 존재하지 않습니다.</p>
      </main>
    );
  }

  const sourceName = deal.source?.display_name || deal.source?.name || '알 수 없음';
  const categoryName = deal.category?.name || '미분류';

  const sourceLabelColor = deal.source?.color_code || '#f2f2f7';
  const summaryText = summary?.summary;
  const summaryStatus = summary?.status || 'not_configured';
  const detailStats = [
    {
      label: '현재가',
      value: deal.price ? `${currencyKRW(deal.price)}원` : '가격 미공개',
    },
    {
      label: '할인',
      value: deal.discount_rate ? `${deal.discount_rate}%` : '정보 없음',
    },
    {
      label: '업데이트',
      value: deal.published_at ? relativeTimeFromNow(deal.published_at) : '시간 미상',
    },
  ];

  return (
    <main className={`detail-main detail-shell theme-${theme}`}>
      <div className="detail-topbar">
        <Link href={backUrl} className="detail-back-link">
          목록으로
        </Link>
        <nav className="theme-switcher detail-theme-switcher" aria-label="상세 페이지 컬러 테마">
          {THEME_OPTIONS.map((option) => (
            <Link
              key={option.value}
              href={buildThemeHref({ id: deal.id, searchParams: searchParams || {}, theme: option.value })}
              className={`theme-pill ${theme === option.value ? 'active' : ''}`}
            >
              {option.label}
            </Link>
          ))}
        </nav>
      </div>

      <section className="detail-hero">
        <div className="detail-heading">
          <p className="detail-kicker" style={{ color: sourceLabelColor }}>
            {sourceName} · {categoryName}
          </p>
          <h1 className="detail-title">{deal.title}</h1>
          <p className="detail-meta">
            <span>{deal.mall_name || '몰 정보 없음'}</span>
            <span>{deal.published_at ? relativeTimeFromNow(deal.published_at) : '시간 정보 없음'}</span>
          </p>
        </div>
        <dl className="detail-stat-grid" aria-label="핵심 요약">
          {detailStats.map((item) => (
            <div key={item.label}>
              <dt>{item.label}</dt>
              <dd>{item.value}</dd>
            </div>
          ))}
        </dl>
      </section>

      {deal.thumbnail_url ? (
        <Image
          src={deal.thumbnail_url}
          alt={deal.title}
          loading="lazy"
          className="detail-thumb"
          width={900}
          height={500}
        />
      ) : null}

      <div className="detail-grid">
        <section className="section">
          <strong className="section-title">가격</strong>
          <p>
            {deal.price ? `${currencyKRW(deal.price)}원` : '가격 미공개'}
            {deal.original_price ? ` (정가 ${currencyKRW(deal.original_price)}원)` : ''}
          </p>
          <p>할인율: {deal.discount_rate ? `${deal.discount_rate}%` : '없음'}</p>
        </section>
        <section className="section">
          <strong className="section-title">게시 정보</strong>
          <p>조회: {deal.view_count || 0}</p>
          <p>댓글: {deal.comment_count || 0}</p>
          <p>스크랩: {deal.bookmark_count || 0}</p>
          <p>추천: {deal.upvotes || 0}</p>
        </section>
      </div>

      <section className="section">
        <strong className="section-title">본문</strong>
        <p className="summary">{deal.content || '본문 데이터가 없습니다.'}</p>
      </section>

      <section className="section">
        <strong className="section-title">AI 요약</strong>
        <p className="summary summary-ai">
          {summaryText
            ? summaryText
            : summaryStatus === 'generating'
              ? '요약 생성 중입니다.'
              : '요약 미지원 또는 아직 준비되지 않았습니다.'}
        </p>
      </section>

      <PriceHistoryChart rows={deal.price_history || []} />

      <div className="actions">
        <Link href="/" className="btn btn-primary">
          목록으로
        </Link>
        {deal.mall_product_url ? (
          <a className="btn" href={deal.mall_product_url} target="_blank" rel="noreferrer">
            상품 페이지 열기
          </a>
        ) : null}
        <a className="btn" href={deal.url} target="_blank" rel="noreferrer">
          원문 보기
        </a>
      </div>
    </main>
  );
}
