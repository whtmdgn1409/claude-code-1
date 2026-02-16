'use client';

import Link from 'next/link';
import Image from 'next/image';
import { memo, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import {
  currencyKRW,
  formatDiscount,
  formatSignal,
  relativeTimeFromNow,
} from '@/lib/format';

const DealCard = ({ deal, detailQueryString = '' }) => {
  const { isBookmarked, toggleBookmark, isAuthenticated } = useAuth();
  const [isToggling, setIsToggling] = useState(false);
  const [message, setMessage] = useState('');

  if (!deal?.id) return null;

  const sourceName = deal.source?.display_name || deal.source?.name || '알 수 없음';
  const sourceBadgeStyle = {
    backgroundColor: deal.source?.color_code || '#f2f2f7',
    color: '#111827',
  };

  const isMarked = Boolean(isBookmarked?.(deal.id));
  const detailHref = detailQueryString ? `/deals/${deal.id}?${detailQueryString}` : `/deals/${deal.id}`;

  const onToggleBookmark = async (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (isToggling) return;
    if (!isAuthenticated) {
      setMessage('로그인 후 북마크할 수 있습니다.');
      return;
    }

    try {
      setIsToggling(true);
      setMessage('');
      await toggleBookmark(deal.id);
    } catch (error) {
      setMessage(error?.message || '북마크 처리 중 오류가 발생했습니다.');
    } finally {
      setIsToggling(false);
    }
  };

  return (
    <article className="deal-card" style={{ contentVisibility: 'auto' }}>
      <Link href={detailHref} className="deal-card-main">
        <div className="deal-card-top">
          {deal.thumbnail_url ? (
            <Image
              src={deal.thumbnail_url}
              alt={deal.title}
              loading="lazy"
              className="deal-thumbnail"
              width={900}
              height={500}
            />
          ) : (
            <div className="deal-thumbnail placeholder">이미지 없음</div>
          )}
          <div className="source-badges">
            <span className="source-badge" style={sourceBadgeStyle}>
              {sourceName}
            </span>
            {deal.category?.name ? (
              <span className="source-badge muted">{deal.category.name}</span>
            ) : null}
          </div>
        </div>

        <div className="deal-card-body">
          <h2 className="deal-title">{deal.title}</h2>
          <p className="deal-meta">
            {deal.mall_name ? <span>{deal.mall_name}</span> : null}
            {deal.published_at ? <span>{relativeTimeFromNow(deal.published_at)}</span> : null}
          </p>
          <div className="deal-price-row">
            {deal.price ? <strong>{currencyKRW(deal.price)}원</strong> : null}
            {deal.original_price ? (
              <span className="strike">{currencyKRW(deal.original_price)}원</span>
            ) : null}
            {formatDiscount(deal.discount_rate) ? (
              <span className="discount">{formatDiscount(deal.discount_rate)}</span>
            ) : null}
          </div>
          <p className="signal">{formatSignal(deal.price_signal)}</p>
          <dl className="stats">
            <div>
              <dt>추천</dt>
              <dd>👍 {deal.upvotes || 0}</dd>
            </div>
            <div>
              <dt>댓글</dt>
              <dd>💬 {deal.comment_count || 0}</dd>
            </div>
            <div>
              <dt>조회</dt>
              <dd>👁 {deal.view_count || 0}</dd>
            </div>
            <div>
              <dt>스크랩</dt>
              <dd>⭐ {deal.bookmark_count || 0}</dd>
            </div>
          </dl>
        </div>
      </Link>

      <button
        type="button"
        className={`bookmark-btn ${isMarked ? 'on' : ''}`}
        aria-label={isMarked ? '북마크 해제' : '북마크 추가'}
        title={isMarked ? '북마크 해제' : '북마크 추가'}
        onClick={onToggleBookmark}
        disabled={isToggling}
      >
        {isMarked ? '★' : '☆'}
      </button>

      {message ? (
        <p className="bookmark-error" role="alert" aria-live="polite">
          {message}
        </p>
      ) : null}
    </article>
  );
};

export default memo(DealCard);
