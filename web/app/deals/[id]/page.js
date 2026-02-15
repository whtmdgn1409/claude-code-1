import Link from 'next/link';
import Image from 'next/image';
import { currencyKRW, relativeTimeFromNow } from '@/lib/format';
import { getDeal, getDealSummary } from '@/lib/api';
import PriceHistoryChart from '@/components/PriceHistoryChart';

const normalizeQueryValue = (value) => {
  if (Array.isArray(value)) return value[0];
  return value;
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

  const [deal, summary] = await Promise.all([
    getDeal(id),
    getDealSummary(id).catch(() => null),
  ]);
  const sourceName = deal.source?.display_name || deal.source?.name || '알 수 없음';
  const categoryName = deal.category?.name || '미분류';

  const sourceLabelColor = deal.source?.color_code || '#f2f2f7';
  const summaryText = summary?.summary;
  const summaryStatus = summary?.status || 'not_configured';

  return (
    <main className="detail-main">
      <p>
        <Link href={backUrl}>← 목록으로</Link>
      </p>
      <h1 className="detail-title">{deal.title}</h1>
      <p className="detail-meta">
        <span>{sourceName}</span>
        <span style={{ color: sourceLabelColor }}>{categoryName}</span>
        <span>{deal.mall_name}</span>
        <span>{relativeTimeFromNow(deal.published_at)}</span>
      </p>

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
          <strong>가격</strong>
          <p>
            {deal.price ? `${currencyKRW(deal.price)}원` : '가격 미공개'}
            {deal.original_price ? ` (정가 ${currencyKRW(deal.original_price)}원)` : ''}
          </p>
          <p>할인율: {deal.discount_rate ? `${deal.discount_rate}%` : '없음'}</p>
        </section>
        <section className="section">
          <strong>게시 정보</strong>
          <p>조회: {deal.view_count || 0}</p>
          <p>댓글: {deal.comment_count || 0}</p>
          <p>스크랩: {deal.bookmark_count || 0}</p>
          <p>추천: {deal.upvotes || 0}</p>
        </section>
      </div>

      <section className="section">
        <strong>본문</strong>
        <p className="summary">{deal.content || '본문 데이터가 없습니다.'}</p>
      </section>

      <section className="section">
        <strong>AI 요약</strong>
        <p>
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
