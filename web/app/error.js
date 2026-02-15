'use client';

import Link from 'next/link';

const errorMessages = {
  title: '페이지를 불러올 수 없습니다',
  description: '요청 처리 중 일시적인 오류가 발생했습니다.',
  retry: '다시 시도',
  home: '게시판으로 돌아가기',
};

export default function Error({ error, reset }) {
  const message = error?.message || '요청 처리 중 일시적인 오류가 발생했습니다.';

  return (
    <main className="board-error">
      <h1>{errorMessages.title}</h1>
      <p className="error-state">{errorMessages.description}</p>
      <p className="error-state detail" role="alert">
        {message}
      </p>
      {error?.digest ? <p className="error-state">{`코드: ${error.digest}`}</p> : null}
      <div className="actions">
        <button type="button" className="btn btn-primary" onClick={() => reset()}>
          {errorMessages.retry}
        </button>
        <Link href="/" className="btn">
          {errorMessages.home}
        </Link>
      </div>
    </main>
  );
}
