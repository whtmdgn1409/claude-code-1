# DealMoa Web Board

기존 DealMoa API(`/api/v1`)를 재사용해 만든 React 기반 웹 게시판(Next.js) 앱입니다.

## 1) 필수 준비

- Backend API가 실행 중이어야 합니다.
- 기본 API 주소: `http://localhost:8000`

## 2) 실행 (Local)

```bash
cd web
npm install
cp .env.example .env.local  # 필요 시 생성
npm run dev
```

- 접속: `http://localhost:3000`

## 3) 환경 변수

`web/.env.local` 예시

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## 4) 검증

```bash
cd web
npm run lint
npm run build
```

## 5) Vercel 배포 체크리스트

- Vercel Project Import: Root Directory = `web`
- Framework: `Next.js`
- Install Command: `npm install`
- Build Command: `npm run build`
- Output Directory: `/.next`
- Preview 배포 환경 변수:
  - `NEXT_PUBLIC_API_BASE_URL` = 배포할 API 주소
    - 예: `https://your-api.example.com/api/v1`

필요하면 Vercel CLI로도 배포 가능합니다.

```bash
cd web
npx vercel          # Preview 배포
npx vercel --prod   # Production 배포
```
