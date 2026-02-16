'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_PASSWORD_LENGTH = 6;

export default function AuthPanel() {
  const { isAuthenticated, user, isLoading, authError, login, register, logout } = useAuth();
  const [mode, setMode] = useState('login');
  const [isOpen, setIsOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [message, setMessage] = useState('');

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setUsername('');
    setDisplayName('');
    setMessage('');
  };

  const submit = async (event) => {
    event.preventDefault();

    if (!EMAIL_PATTERN.test(email)) {
      setMessage('이메일 형식을 확인해 주세요.');
      return;
    }

    if (password.length < MIN_PASSWORD_LENGTH) {
      setMessage(`비밀번호는 ${MIN_PASSWORD_LENGTH}자 이상이어야 합니다.`);
      return;
    }

    try {
      setMessage('');
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password, username, displayName);
      }
      resetForm();
      setIsOpen(false);
    } catch (error) {
      setMessage(error.message || '요청 처리에 실패했습니다.');
    }
  };

  if (isLoading) {
    return <p className="auth-loading">인증 상태 확인 중...</p>;
  }

  if (isAuthenticated && user) {
    return (
      <div className="auth-status">
        <p>
          {user.display_name || user.username || user.email || '사용자'}님 안녕하세요
        </p>
        <button type="button" className="btn" onClick={logout}>
          로그아웃
        </button>
      </div>
    );
  }

  return (
    <section className="auth-wrap">
      <button type="button" className="btn" onClick={() => setIsOpen((prev) => !prev)}>
        로그인
      </button>

      {!isOpen ? null : (
        <form className="auth-form" onSubmit={submit}>
          <p className="auth-title">{mode === 'login' ? '로그인' : '회원가입'}</p>

          <label>
            <span>이메일</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              placeholder="you@example.com"
            />
          </label>

          <label>
            <span>비밀번호</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={MIN_PASSWORD_LENGTH}
              placeholder={`${MIN_PASSWORD_LENGTH}자 이상`}
            />
          </label>

          {mode === 'register' ? (
            <>
              <label>
                <span>사용자명(선택)</span>
                <input
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="username"
                />
              </label>
              <label>
                <span>표시 이름(선택)</span>
                <input
                  type="text"
                  value={displayName}
                  onChange={(event) => setDisplayName(event.target.value)}
                  placeholder="표시할 이름"
                />
              </label>
            </>
          ) : null}

          <div className="auth-actions">
            <button type="submit" className="btn btn-primary">
              {mode === 'login' ? '로그인' : '회원가입'}
            </button>
            <button
              type="button"
              className="btn"
              onClick={() => {
                setMode(mode === 'login' ? 'register' : 'login');
                setMessage('');
              }}
            >
              {mode === 'login' ? '회원가입으로 전환' : '로그인으로 전환'}
            </button>
          </div>

          {(message || authError) ? <p className="error-state">{message || authError}</p> : null}
        </form>
      )}
    </section>
  );
}
