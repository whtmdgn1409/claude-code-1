import './globals.css';
import { AuthProvider } from '@/context/AuthContext';

export const metadata = {
  title: '딜모아 게시판',
  description: '실시간 핫딜 게시판을 웹으로 탐색하세요.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>
        <AuthProvider>
          <div className="container">{children}</div>
        </AuthProvider>
      </body>
    </html>
  );
}
