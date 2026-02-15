'use client';

import Link from 'next/link';

export default function Error({ error, reset }) {
  return (
    <main className="detail-main">
      <h1>딜 상세를 불러오지 못했습니다</h1>
      <p className="error-state">{error.message || '딜 상세 조회에 실패했습니다.'}</p>
      <div className="actions">
        <button type="button" className="btn btn-primary" onClick={() => reset()}>
          다시 시도
        </button>
        <Link href="/" className="btn">
          목록으로
        </Link>
      </div>
    </main>
  );
}
