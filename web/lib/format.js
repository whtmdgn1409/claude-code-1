const KOR_DATE_UNITS = [
  { value: 60, unit: '초 전' },
  { value: 60, unit: '분 전' },
  { value: 24, unit: '시간 전' },
  { value: 7, unit: '일 전' },
];

const toNumber = (value) => {
  const next = Number(value);
  return Number.isFinite(next) ? next : 0;
};

export const currencyKRW = (value) =>
  toNumber(value).toLocaleString('ko-KR', {
    maximumFractionDigits: 0,
  });

export const formatDiscount = (value) => {
  const rate = toNumber(value);
  if (!rate) return null;
  return `${rate.toFixed(1)}%`;
};

export const formatSignal = (signal) => {
  switch (signal) {
    case 'lowest':
      return '🟢 역대가';
    case 'average':
      return '🟡 평균가';
    case 'high':
      return '🔴 비쌈';
    default:
      return '⚪ 정보 없음';
  }
};

export const relativeTimeFromNow = (isoDate) => {
  const target = new Date(isoDate);
  if (Number.isNaN(target.getTime())) return '';

  const now = Date.now();
  let diff = Math.max(0, Math.floor((now - target.getTime()) / 1000));

  for (let i = 0; i < KOR_DATE_UNITS.length; i += 1) {
    const { value, unit } = KOR_DATE_UNITS[i];
    if (diff < value) return `${diff}${unit}`;
    diff = Math.floor(diff / value);
  }

  return `${diff}주 전`;
};
