import logging
import re
from typing import Any

from aiohttp import ClientSession
from flogin import ErrorResponse, Plugin, Query, QueryResponse, Settings

from .results import Result, SendMessageResult, UpdateQueryResult

log = logging.getLogger(__name__)

# https://ptb.discord.com/api/webhooks/1336483229112340541/NPu4OFtrbsF0OXFcUA0mnyJFItqLkmRn933mGDf_l_1pM-Mgkse6liRoH3B4AjU3AK-e
url_pattern = re.compile(
    r"https://(?P<subdomain>[a-zA-Z]+\.)?discord\.com/api/webhooks/(?P<channel_id>[0-9]+)/(?P<slug>[a-zA-Z0-9_\-]+)/?"
)


class InvalidSettings(Exception): ...


class PluginSettings(Settings):
    webhooks: str | None


class DiscordPlugin(Plugin[PluginSettings]):
    session: ClientSession

    async def start(self):
        async with ClientSession() as cs:
            self.session = cs
            await super().start()

    @property
    def webhooks(self) -> dict[str, str]:
        try:
            raw = self.settings.webhooks or ""
            return {
                parts[0].strip(): parts[1].strip()
                for line in raw.splitlines()
                if (parts := line.split("!"))
            }
        except Exception as e:
            raise InvalidSettings("Could not convert settings") from e


plugin = DiscordPlugin()


@plugin.search(lambda query: query.text.split(" ")[0] in plugin.webhooks)
async def send_preset(query: Query):
    parts = query.text.split(" ")
    url = plugin.webhooks.get(parts.pop(0))
    if not url:
        return Result(title="Preset Not Found")

    return SendMessageResult(url, " ".join(parts).strip())


@plugin.search(pattern=url_pattern)
async def send_from_url(query: Query[re.Match]):
    assert query.condition_data

    url = f"https://discord.com/api/webhooks/{query.condition_data['channel_id']}/{query.condition_data['slug']}"
    parts = query.text.split(" ")
    return SendMessageResult(url, " ".join(parts[1:]).strip())


@plugin.search(text="")
async def index_handler(query: Query):
    return [
        Result(
            title="To send a message, type the url then content or a webhook's name then content.",
            score=1000,
        ),
        *(
            UpdateQueryResult(
                f"{query.keyword} {key} ",
                title=f"Send a message to the {key} webhook",
                sub=value,
            )
            for key, value in plugin.webhooks.items()
        ),
    ]


@plugin.search()
async def invalid(query: Query):
    part = query.text.split(" ")[0]
    return Result(title=f"Invalid url or unknown webhook name: {part}")


@plugin.event
async def on_error(
    event_method: str, error: Exception, *args: Any, **kwargs: Any
) -> QueryResponse | ErrorResponse:
    """gets called when an error occurs in an event"""
    log.exception("Ignoring exception in event %r", event_method, exc_info=error)
    if isinstance(error, InvalidSettings):
        return QueryResponse([Result(title="Invalid Settings Given")])
    return ErrorResponse.internal_error(error)
