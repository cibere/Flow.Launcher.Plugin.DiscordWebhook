import logging
import re
from collections.abc import AsyncIterator
from typing import Any

from flogin import ErrorResponse, Query, QueryResponse

from .plugin import DiscordPlugin, InvalidSettings
from .results import AddPresetResult, DisplayWebhookResult, Result, SendMessageResult

log = logging.getLogger(__name__)

URL_PATTERN = re.compile(
    r"https://(?P<subdomain>[a-zA-Z]+\.)?discord\.com/api/webhooks/(?P<channel_id>[0-9]+)/(?P<slug>[a-zA-Z0-9_\-]+)/?"
)

plugin = DiscordPlugin()


@plugin.search(lambda query: query.text.split(" ")[0] in plugin.webhooks)
async def send_preset(query: Query) -> Result:
    parts = query.text.split(" ")
    url = plugin.webhooks.get(parts.pop(0))
    if not url:
        return Result(title="Preset Not Found")

    return SendMessageResult(url, " ".join(parts).strip())


@plugin.search(pattern=URL_PATTERN)
async def send_from_url(query: Query[re.Match[str]]) -> AsyncIterator[Result]:
    assert query.condition_data

    url = f"https://discord.com/api/webhooks/{query.condition_data['channel_id']}/{query.condition_data['slug']}"
    parts = query.text.split(" ")
    msg = " ".join(parts[1:]).strip()

    yield SendMessageResult(url, msg)

    if " " not in msg:
        yield AddPresetResult(url, msg)


@plugin.search(text="")
async def index_handler(query: Query) -> list[Result]:
    return [
        Result(
            title="To send a message, type the url then content or a webhook's name then content.",
            score=1000,
        ),
        *(
            DisplayWebhookResult(
                query.keyword,
                key,
                title=f"Send a message to the {key} webhook",
                sub=value,
            )
            for key, value in plugin.webhooks.items()
        ),
    ]


@plugin.search()
async def invalid(query: Query) -> Result:
    part = query.text.split(" ")[0]
    return Result(title=f"Invalid url or unknown webhook name: {part}")


@plugin.event
async def on_error(
    event_method: str, error: Exception, *args: Any, **kwargs: Any
) -> QueryResponse | ErrorResponse:
    log.exception("Ignoring exception in event %r", event_method, exc_info=error)
    if isinstance(error, InvalidSettings):
        return QueryResponse([Result(title="Invalid Settings Given")])
    return ErrorResponse.internal_error(error)
