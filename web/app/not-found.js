import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="board-error">
      <h1>요청한 페이지를 찾을 수 없습니다</h1>
      <p className="error-state">딜 ID 또는 경로를 다시 확인해 주세요.</p>
      <Link href="/" className="btn btn-primary">
        게시판 홈으로
      </Link>
    </main>
  );
}
