from __future__ import annotations

from environs import Env

env = Env()

MULTITENANT_MODE = env.str("MULTITENANT_MODE", default="schema")  # off|schema|database
ENABLE_STRIPE = env.bool("ENABLE_STRIPE", default=True)

# CMS is always enabled (MDX-based, no Wagtail)
ENABLE_CMS = True
ENABLE_LMS = env.bool("ENABLE_LMS", default=False)
ENABLE_COMMUNITY = env.bool("ENABLE_COMMUNITY", default=False)
ENABLE_MCP = env.bool("ENABLE_MCP", default=False)


def optional_apps() -> list[str]:
    apps: list[str] = []
    if ENABLE_CMS:
        apps.append("cms")
    if ENABLE_LMS:
        apps.append("lms")
    if ENABLE_COMMUNITY:
        apps.append("community")
    if ENABLE_MCP:
        apps.append("mcp")
    return apps


def optional_api_urls() -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    if ENABLE_CMS:
        urls.append(("cms/", "cms.urls"))
    if ENABLE_LMS:
        urls.append(("lms/", "lms.urls"))
    if ENABLE_COMMUNITY:
        urls.append(("community/", "community.urls"))
    if ENABLE_MCP:
        urls.append(("mcp/", "mcp.urls"))
    return urls
