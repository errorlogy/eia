"""Telegram Bot API contact adapter with shadow mode."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from eia.audit import CausalTrace, TraceNodeKind


@dataclass
class TelegramSendResult:
    """Outcome of a contact attempt."""

    sent: bool
    shadow: bool
    message: str
    http_status: int | None = None
    error: str | None = None
    telegram_message_id: int | None = None


class TelegramAdapter:
    """Send proactive messages via Telegram Bot API."""

    API_URL = "https://api.telegram.org/bot{token}/sendMessage"

    def __init__(
        self,
        *,
        bot_token: str | None = None,
        chat_id: str | None = None,
        shadow_mode: bool = True,
    ) -> None:
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        self.shadow_mode = shadow_mode

    def _log_shadow(self, text: str, trace: CausalTrace | None) -> TelegramSendResult:
        payload = {
            "channel": "telegram",
            "shadow": True,
            "chat_id": self.chat_id or "(unset)",
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        line = f"[EIA shadow contact] {json.dumps(payload, ensure_ascii=False)}"
        print(line, file=sys.stdout)
        if trace is not None:
            trace.add_node(
                TraceNodeKind.CONTACT_GOVERNOR,
                {
                    "live_contact": True,
                    "adapter": "telegram",
                    "shadow": True,
                    **payload,
                },
                parent_kind=TraceNodeKind.CONTACT_GOVERNOR,
            )
        return TelegramSendResult(sent=False, shadow=True, message=text)

    def send_message(
        self,
        text: str,
        *,
        trace: CausalTrace | None = None,
    ) -> TelegramSendResult:
        """Deliver message via Telegram or log in shadow mode."""
        if self.shadow_mode:
            return self._log_shadow(text, trace)

        if not self.bot_token or not self.chat_id:
            return TelegramSendResult(
                sent=False,
                shadow=False,
                message=text,
                error="TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID required for live mode",
            )

        url = self.API_URL.format(token=self.bot_token)
        body = urllib.parse.urlencode(
            {"chat_id": self.chat_id, "text": text, "disable_web_page_preview": "true"}
        ).encode()
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = resp.status
                raw = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode() if exc.fp else str(exc)
            return TelegramSendResult(
                sent=False,
                shadow=False,
                message=text,
                http_status=exc.code,
                error=err_body,
            )
        except urllib.error.URLError as exc:
            return TelegramSendResult(
                sent=False,
                shadow=False,
                message=text,
                error=str(exc.reason),
            )

        msg_id = raw.get("result", {}).get("message_id")
        result = TelegramSendResult(
            sent=True,
            shadow=False,
            message=text,
            http_status=status,
            telegram_message_id=msg_id,
        )
        if trace is not None:
            trace.add_node(
                TraceNodeKind.CONTACT_GOVERNOR,
                {
                    "live_contact": True,
                    "adapter": "telegram",
                    "shadow": False,
                    "chat_id": self.chat_id,
                    "text": text,
                    "http_status": status,
                    "telegram_message_id": msg_id,
                },
                parent_kind=TraceNodeKind.CONTACT_GOVERNOR,
            )
        return result

    @staticmethod
    def format_message(
        *,
        drive: str,
        question_text: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Template-based message (no LLM) for v1 live stack."""
        ctx = context or {}
        if question_text:
            return question_text

        templates = {
            "epistemic": (
                "EIA noticed uncertainty about {subject}. "
                "Could you clarify: {claim}?"
            ),
            "coherence": (
                "EIA found conflicting information about {topic}. "
                "Which version is correct?"
            ),
            "commitment": (
                "Following up on {subject} — {claim}. Any update?"
            ),
        }
        tpl = templates.get(drive, "EIA has a proactive question: {subject}")
        return tpl.format(
            subject=ctx.get("subject", "your project"),
            claim=ctx.get("claim", "an open item"),
            topic=ctx.get("topic", "a topic"),
        )
