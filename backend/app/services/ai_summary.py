"""
AI-powered text summarization service with multi-provider support.

Supports:
- OpenAI (GPT-3.5-turbo, GPT-4)
- Anthropic Claude (Claude 3 Haiku)
- Dry-run mode (placeholder when API key not configured)
"""
from typing import Dict, Any, List, Optional
from app.config import settings


class AISummaryService:
    """AI-powered text summarization service with multi-provider support."""

    @staticmethod
    def is_configured() -> bool:
        """
        Check if AI service is configured with API key.

        Returns:
            bool: True if API key is set, False otherwise
        """
        return bool(settings.AI_API_KEY)

    @staticmethod
    def generate_summary(
        deal_title: str,
        deal_content: str,
        comments: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate 3-line Korean summary of deal and comments.

        Args:
            deal_title: Title of the deal
            deal_content: Content/description of the deal
            comments: List of comment dictionaries with 'author', 'content', 'upvotes'

        Returns:
            Dict containing:
                - summary (str): The 3-line summary text
                - provider (str): Provider used ("openai", "claude", "dry-run")
                - tokens_used (int): Number of tokens consumed
                - cost_estimate (float): Estimated cost in USD
        """
        if not AISummaryService.is_configured():
            return AISummaryService._dry_run()

        # Build prompt
        prompt = AISummaryService._build_prompt(
            deal_title, deal_content, comments
        )

        # Call AI provider based on configuration
        try:
            if settings.AI_SERVICE_PROVIDER == "openai":
                return AISummaryService._call_openai(prompt)
            elif settings.AI_SERVICE_PROVIDER == "claude":
                return AISummaryService._call_claude(prompt)
            else:
                return AISummaryService._dry_run()
        except Exception as e:
            # Log error and fallback to dry-run
            print(f"AI service error: {e}")
            return AISummaryService._dry_run()

    @staticmethod
    def _build_prompt(title: str, content: str, comments: List[Dict]) -> str:
        """
        Build Korean summarization prompt.

        Args:
            title: Deal title
            content: Deal content
            comments: List of comments

        Returns:
            str: Formatted prompt for AI model
        """
        # Limit to top 10 comments by upvotes
        top_comments = sorted(
            comments,
            key=lambda x: x.get('upvotes', 0),
            reverse=True
        )[:10]

        comment_text = "\n".join([
            f"- {c.get('author', '익명')}: {c.get('content', '')[:100]}"
            for c in top_comments
        ]) if top_comments else "댓글 없음"

        return f"""다음 핫딜 게시글과 댓글을 분석하여 한국어로 정확히 3줄 요약을 작성하세요.

[게시글 제목]
{title}

[게시글 내용]
{content[:500] if content else "내용 없음"}

[주요 댓글]
{comment_text}

요구사항:
- 정확히 3줄로 작성 (각 줄은 한 문장)
- 가격, 배송비, 쿠폰 정보 등 핵심 정보 포함
- 댓글에서 언급된 주의사항이나 팁 포함
- 존댓말 사용, 간결하고 명확하게

요약:
"""

    @staticmethod
    def _call_openai(prompt: str) -> Dict[str, Any]:
        """
        Call OpenAI API (GPT-3.5-turbo or GPT-4).

        Args:
            prompt: The prompt to send to OpenAI

        Returns:
            Dict with summary, provider, tokens_used, cost_estimate
        """
        import openai

        client = openai.OpenAI(api_key=settings.AI_API_KEY)

        try:
            response = client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 한국어 딜 정보를 간결하게 요약하는 어시스턴트입니다."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=settings.AI_TEMPERATURE
            )

            summary = response.choices[0].message.content.strip()
            tokens = response.usage.total_tokens

            # Cost estimation (GPT-3.5-turbo pricing: $0.0005/1k input, $0.0015/1k output)
            cost = (
                response.usage.prompt_tokens * 0.0005 / 1000 +
                response.usage.completion_tokens * 0.0015 / 1000
            )

            return {
                "summary": summary,
                "provider": "openai",
                "tokens_used": tokens,
                "cost_estimate": cost
            }

        except Exception as e:
            # Log error and fallback to dry-run
            print(f"OpenAI API error: {e}")
            raise

    @staticmethod
    def _call_claude(prompt: str) -> Dict[str, Any]:
        """
        Call Claude API (Claude 3 Haiku for cost efficiency).

        Args:
            prompt: The prompt to send to Claude

        Returns:
            Dict with summary, provider, tokens_used, cost_estimate
        """
        import anthropic

        client = anthropic.Anthropic(api_key=settings.AI_API_KEY)

        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=settings.AI_MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            summary = response.content[0].text.strip()
            tokens = response.usage.input_tokens + response.usage.output_tokens

            # Cost estimation (Claude Haiku pricing: $0.00025/1k input, $0.00125/1k output)
            cost = (
                response.usage.input_tokens * 0.00025 / 1000 +
                response.usage.output_tokens * 0.00125 / 1000
            )

            return {
                "summary": summary,
                "provider": "claude",
                "tokens_used": tokens,
                "cost_estimate": cost
            }

        except Exception as e:
            print(f"Claude API error: {e}")
            raise

    @staticmethod
    def _dry_run() -> Dict[str, Any]:
        """
        Return placeholder summary when API not configured.

        Returns:
            Dict with placeholder summary and zero cost
        """
        return {
            "summary": (
                "1. AI 요약 기능이 활성화되지 않았습니다.\n"
                "2. API 키를 설정하면 자동으로 요약이 생성됩니다.\n"
                "3. OpenAI 또는 Claude API 키를 .env 파일에 추가해주세요."
            ),
            "provider": "dry-run",
            "tokens_used": 0,
            "cost_estimate": 0.0
        }
