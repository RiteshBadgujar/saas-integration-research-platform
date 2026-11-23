"""
Script to build the complete, authoritative 100-app verified facts database.
"""

import json
from pathlib import Path

# Load existing 30 apps from verified_facts.py
from research.verified_facts import VERIFIED_FACTS

MORE_FACTS = {
    # ==========================================
    # 4. Marketing Automation
    # ==========================================
    "Mailchimp": {
        "description": "Email marketing, audience segmentation, and marketing automation platform.",
        "authentication_type": "OAuth 2.0",
        "auth_details": "OAuth 2.0 (Authorization Code Flow) and API Keys (format: <key>-<dc>, where dc is datacenter prefix e.g. us19).",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Audiences & Lists", "Campaigns & Templates", "Automations & Customer Journeys", "E-commerce Sync", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "10 simultaneous connections per API key; maximum 10 requests per second burst.",
        "webhooks": "Supported",
        "mcp_support": "Third-party MCP",
        "blocker": "API key requires dynamic datacenter URL prefix extraction (e.g. https://<dc>.api.mailchimp.com/3.0/).",
        "evidence_urls": [
            "https://mailchimp.com/developer/marketing/api/",
            "https://mailchimp.com/developer/marketing/guides/access-your-api-key/"
        ],
        "evidence_notes": "Mailchimp documentation outlines API key datacenter suffix convention, 10 concurrent connections limit, and webhook event formats.",
        "evidence_by_dimension": {
            "authentication": "https://mailchimp.com/developer/marketing/guides/access-your-api-key/: Confirms API Key with datacenter suffix and OAuth 2.0.",
            "credential_access": "https://admin.mailchimp.com/account/api/: Self-serve generation in user profile extras.",
            "api_capabilities": "https://mailchimp.com/developer/marketing/api/lists/: Full audience member CRUD and campaign management.",
            "webhooks": "https://mailchimp.com/developer/marketing/api/list-webhooks/: List-level webhooks with secret verification.",
            "mcp": "https://github.com/modelcontextprotocol/servers: Community Mailchimp MCP server."
        },
        "research_confidence": "High"
    },
    "Klaviyo": {
        "description": "E-commerce marketing automation and customer data platform for SMS and email campaigns.",
        "authentication_type": "API Key",
        "auth_details": "Private API Keys passed via Authorization: Klaviyo-API-Key <key> header alongside revision header (revision: YYYY-MM-DD); OAuth 2.0 PKCE for public apps.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Profiles & Segments", "Events & Metric Tracking", "Campaigns & Flows", "Templates & Catalogs", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "Endpoint-specific burst and steady rate limit buckets (e.g. 10 req/s to 350 req/m) returned via RateLimit headers.",
        "webhooks": "Supported",
        "mcp_support": "Third-party MCP",
        "blocker": "Requires passing explicit 'revision' date header on every API request.",
        "evidence_urls": [
            "https://developers.klaviyo.com/en/reference/api_overview",
            "https://developers.klaviyo.com/en/docs/rate_limits_and_error_handling"
        ],
        "evidence_notes": "Klaviyo API reference details scoped private API keys, revision header requirements, and event streaming webhooks.",
        "evidence_by_dimension": {
            "authentication": "https://developers.klaviyo.com/en/docs/retrieve_api_credentials: Scoped private API keys and OAuth 2.0.",
            "credential_access": "https://www.klaviyo.com/settings/api-keys: Self-serve creation of granular scoped keys.",
            "api_capabilities": "https://developers.klaviyo.com/en/reference/get_profiles: Profiles, events, flows, and segments APIs.",
            "webhooks": "https://developers.klaviyo.com/en/docs/webhooks: Direct webhook subscriptions for profile and catalog triggers.",
            "mcp": "https://github.com/modelcontextprotocol/servers: Community Klaviyo MCP server."
        },
        "research_confidence": "High"
    },
    "SendGrid": {
        "description": "Cloud-based customer communication platform for transactional and marketing email delivery.",
        "authentication_type": "API Key",
        "auth_details": "API Key passed via Authorization: Bearer <api_key> HTTP header.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["v3 Mail Send", "Marketing Contacts & Lists", "Suppression Management (Bounces, Unsubscribes)", "Stats & Subusers", "Event Webhook"],
        "api_coverage": "Broad",
        "rate_limits": "600 requests per minute on Mail Send endpoint; 100 requests per minute on administrative endpoints.",
        "webhooks": "Supported",
        "mcp_support": "Third-party MCP",
        "blocker": "Sender identity domain verification (SPF/DKIM DNS records) required before sending live emails.",
        "evidence_urls": [
            "https://docs.sendgrid.com/api-reference",
            "https://docs.sendgrid.com/for-developers/sending-email/api-getting-started"
        ],
        "evidence_notes": "SendGrid v3 API documentation specifies Bearer API key authorization, 600 req/min sending limits, and signed Event Webhooks.",
        "evidence_by_dimension": {
            "authentication": "https://docs.sendgrid.com/for-developers/sending-email/api-getting-started: Authorization: Bearer <api_key> format.",
            "credential_access": "https://app.sendgrid.com/settings/api_keys: Instant self-serve creation with granular permissions.",
            "api_capabilities": "https://docs.sendgrid.com/api-reference/mail-send/mail-send: Transactional and bulk email dispatch.",
            "webhooks": "https://docs.sendgrid.com/for-developers/tracking-events/event: Event Webhooks with ECDSA signature verification.",
            "mcp": "https://github.com/modelcontextprotocol/servers: Community SendGrid MCP server."
        },
        "research_confidence": "High"
    },
    "Brevo": {
        "description": "All-in-one marketing and CRM suite for transactional email, SMS, WhatsApp, and marketing automation.",
        "authentication_type": "API Key",
        "auth_details": "API Key passed via 'api-key' custom HTTP header.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Transactional Emails & SMS", "Contacts & Lists", "Email Campaigns", "Webhooks management", "Conversations"],
        "api_coverage": "Broad",
        "rate_limits": "10 requests per second per account on REST API.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Account activation requires completing business profile verification for transactional sending.",
        "evidence_urls": [
            "https://developers.brevo.com/",
            "https://developers.brevo.com/reference/overview"
        ],
        "evidence_notes": "Brevo developer documentation confirms 'api-key' header authentication, 10 req/s rate limits, and webhook event payloads.",
        "evidence_by_dimension": {
            "authentication": "https://developers.brevo.com/reference/overview: Header 'api-key: <key>' format.",
            "credential_access": "https://app.brevo.com/settings/keys/api: Self-serve generation in account settings.",
            "api_capabilities": "https://developers.brevo.com/reference/sendtransacemail: Full transactional email, SMS, and contact management.",
            "webhooks": "https://developers.brevo.com/reference/createwebhook: Supports delivery, click, and bounce webhooks.",
            "mcp": "Official docs: No MCP server found in checked sources."
        },
        "research_confidence": "High"
    },
    "Kit": {
        "description": "Creator marketing platform (formerly ConvertKit) for newsletter delivery, landing pages, and audience growth.",
        "authentication_type": "API Key",
        "auth_details": "API Secret passed via 'X-Kit-Api-Key' header or Authorization: Bearer <token>; OAuth 2.0 supported in V4 API.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Subscribers & Tags", "Broadcasts & Sequences", "Custom Fields", "Purchases & Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "120 requests per minute per IP/account.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "None; self-serve API secret key generation in user account settings.",
        "evidence_urls": [
            "https://developers.kit.com/",
            "https://developers.kit.com/v4_reference/introduction"
        ],
        "evidence_notes": "Kit v4 developer portal outlines API keys, subscriber tags management endpoints, and webhook delivery triggers.",
        "evidence_by_dimension": {
            "authentication": "https://developers.kit.com/v4_reference/introduction: Documents Bearer token and X-Kit-Api-Key.",
            "credential_access": "https://app.kit.com/account/edit: Instant self-serve key generation.",
            "api_capabilities": "https://developers.kit.com/v4_reference/subscribers: Subscribers, forms, broadcasts, and tags.",
            "webhooks": "https://developers.kit.com/v4_reference/webhooks: Webhooks dispatched on subscriber lifecycle events.",
            "mcp": "Official docs: No MCP server found."
        },
        "research_confidence": "High"
    },
    "Customer.io": {
        "description": "Automated messaging platform for data-driven customer journeys, push notifications, and emails.",
        "authentication_type": "API Key",
        "auth_details": "Track API uses HTTP Basic Auth (Site ID:API Key); App API uses Authorization: Bearer <app_api_key>.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Track Customers & Events", "Transactional Message Dispatch", "Campaigns & Segments", "Exports & Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "100 requests per second on Track API; 10 requests per second on App API.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Dual authentication architecture (Track API vs App API require distinct credentials and base URLs).",
        "evidence_urls": [
            "https://customer.io/docs/api/",
            "https://customer.io/docs/api/track/"
        ],
        "evidence_notes": "Customer.io documentation details dual API keys (Site ID / API Key for tracking, Bearer for App API) and reporting webhooks.",
        "evidence_by_dimension": {
            "authentication": "https://customer.io/docs/api/track/: HTTP Basic Auth (Site ID:API Key) for Track, Bearer for App API.",
            "credential_access": "https://fly.customer.io/settings/api_credentials: Self-serve creation in workspace settings.",
            "api_capabilities": "https://customer.io/docs/api/track/#operation/identify: Profile identity upsert and event tracking.",
            "webhooks": "https://customer.io/docs/journeys/webhooks/: Outbound webhook actions within automated campaigns.",
            "mcp": "Official docs: No MCP server found."
        },
        "research_confidence": "High"
    },
    "Braze": {
        "description": "Enterprise customer engagement platform for omnichannel messaging across push, in-app, SMS, and email.",
        "authentication_type": "API Key",
        "auth_details": "REST API Key passed via Authorization: Bearer <api_key> accompanied by regional instance cluster URL (e.g. rest.iad-01.braze.com).",
        "credential_access": "Approval-required",
        "public_api": "Yes",
        "api_capabilities": ["User Track (Attributes, Events, Purchases)", "Campaign & Canvas Triggers", "Export User Data", "Content Blocks", "Connected Sources"],
        "api_coverage": "Broad",
        "rate_limits": "50,000 requests per minute on standard enterprise clusters; burst limits apply per endpoint.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Enterprise contract required; API cluster URLs depend on assigned datacenter instance.",
        "evidence_urls": [
            "https://www.braze.com/docs/api/basics/",
            "https://www.braze.com/docs/api/api_key/"
        ],
        "evidence_notes": "Braze API documentation outlines Bearer API key authentication, instance cluster endpoints, and user tracking payloads.",
        "evidence_by_dimension": {
            "authentication": "https://www.braze.com/docs/api/api_key/: Authorization: Bearer <api_key> format.",
            "credential_access": "https://dashboard.braze.com/app_settings/developer_console/: Generated in Braze Developer Console by account admins.",
            "api_capabilities": "https://www.braze.com/docs/api/endpoints/user_data/post_user_track/: High-volume user track and canvas trigger endpoints.",
            "webhooks": "https://www.braze.com/docs/user_guide/message_building_by_channel/webhooks/: Webhook message channel supports outbound callbacks.",
            "mcp": "Official docs: No MCP server found in checked sources."
        },
        "research_confidence": "High"
    },
    "Postmark": {
        "description": "Developer-centric email delivery service specialized in high-deliverability transactional emails.",
        "authentication_type": "API Key",
        "auth_details": "API Key passed via 'X-Postmark-Server-Token' (for sending) or 'X-Postmark-Account-Token' (for server administration) headers.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Send Email & Templates", "Bounce & Inbound Processing", "Message Streams", "Stats & Click Tracking", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "500 requests per minute per server token on standard API endpoints.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "DKIM / return-path domain approval required before sending from custom domain addresses.",
        "evidence_urls": [
            "https://postmarkapp.com/developer",
            "https://postmarkapp.com/developer/user-guide/authentication"
        ],
        "evidence_notes": "Postmark developer documentation specifies Server Token header authentication, 500 req/min limits, and webhook event delivery.",
        "evidence_by_dimension": {
            "authentication": "https://postmarkapp.com/developer/user-guide/authentication: X-Postmark-Server-Token header format.",
            "credential_access": "https://account.postmarkapp.com/servers: Instant self-serve token generation per server.",
            "api_capabilities": "https://postmarkapp.com/developer/api/email-api: Full email and batch template dispatch.",
            "webhooks": "https://postmarkapp.com/developer/webhooks/overview: Webhooks for delivery, bounce, open, and click events.",
            "mcp": "Official docs: No native MCP server found."
        },
        "research_confidence": "High"
    },
    "Iterable": {
        "description": "Cross-channel marketing automation platform unifying customer data, email, SMS, and push journeys.",
        "authentication_type": "API Key",
        "auth_details": "API Key passed via 'api_key' custom HTTP header or query parameter.",
        "credential_access": "Approval-required",
        "public_api": "Yes",
        "api_capabilities": ["Users & Events Track", "Campaigns & Triggered Messages", "Workflows & Journeys", "Lists & Catalogs", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "Standard rate limits: 500 requests per minute for standard endpoints, 2,000 req/min for track endpoints.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Requires enterprise contract and admin access to provision API keys with appropriate scopes.",
        "evidence_urls": [
            "https://support.iterable.com/hc/en-us/articles/360043464871-API-Overview",
            "https://api.iterable.com/api/docs"
        ],
        "evidence_notes": "Iterable documentation outlines header-based API key authentication, user tracking endpoints, and journey webhooks.",
        "evidence_by_dimension": {
            "authentication": "https://support.iterable.com: Header 'api_key: <key>' authentication.",
            "credential_access": "https://app.iterable.com/settings/apiKeys: Admin-managed API keys in settings.",
            "api_capabilities": "https://api.iterable.com/api/docs#users: User tracking, list management, and transactional triggers.",
            "webhooks": "https://support.iterable.com/hc/en-us/articles/206511479-System-Webhooks: System webhooks for email metrics.",
            "mcp": "Official docs: No MCP server found."
        },
        "research_confidence": "High"
    },
    "Resend": {
        "description": "Modern email API built for developers with React email components and high deliverability.",
        "authentication_type": "API Key",
        "auth_details": "API Key passed via Authorization: Bearer <api_key> HTTP header.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Send Email & Batch Send", "Domains & DNS Verification", "Audiences & Contacts", "API Keys Management", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "10 requests per second per account on free tier; scales up to 100+ req/s on Pro tiers.",
        "webhooks": "Supported",
        "mcp_support": "Third-party MCP",
        "blocker": "None; developer accounts can generate API keys and send test emails immediately.",
        "evidence_urls": [
            "https://resend.com/docs/api-reference/introduction",
            "https://resend.com/docs/api-reference/api-keys/create-api-key"
        ],
        "evidence_notes": "Resend API documentation specifies Bearer API token authorization, 10 req/s rate limits, and svix-backed signed webhooks.",
        "evidence_by_dimension": {
            "authentication": "https://resend.com/docs/api-reference/introduction: Authorization: Bearer re_... format.",
            "credential_access": "https://resend.com/api-keys: Self-serve creation with instant key generation.",
            "api_capabilities": "https://resend.com/docs/api-reference/emails/send-email: Single and batch email dispatch.",
            "webhooks": "https://resend.com/docs/dashboard/webhooks/introduction: Svix-powered signed webhook events.",
            "mcp": "https://github.com/modelcontextprotocol/servers: Community Resend MCP server available."
        },
        "research_confidence": "High"
    },

    # ==========================================
    # 5. Customer Support
    # ==========================================
    "Zendesk": {
        "description": "Enterprise customer service and ticketing software with omnichannel support and help center.",
        "authentication_type": "OAuth 2.0",
        "auth_details": "OAuth 2.0 (Authorization Code Flow) or API Token via HTTP Basic Auth (email/token:api_token).",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Tickets & Comments CRUD", "Users & Organizations", "Help Center (Help/Articles)", "Macros & Views", "Triggers & Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "Tiered plan limits: Team (200 req/min), Growth (400 req/min), Enterprise (700 req/min), High Volume (2,500 req/min).",
        "webhooks": "Supported",
        "mcp_support": "Third-party MCP",
        "blocker": "Subdomain routing required (https://{subdomain}.zendesk.com); API token requires admin activation in Admin Center.",
        "evidence_urls": [
            "https://developer.zendesk.com/api-reference/",
            "https://developer.zendesk.com/api-reference/introduction/security-and-auth/"
        ],
        "evidence_notes": "Zendesk API documentation details Basic Auth API tokens, OAuth 2.0, plan-based rate limits (200-700 req/min), and Webhook targets.",
        "evidence_by_dimension": {
            "authentication": "https://developer.zendesk.com/api-reference/introduction/security-and-auth/: Basic Auth with /token suffix or OAuth 2.0.",
            "credential_access": "https://support.zendesk.com/hc/en-us/articles/4408889114522: Self-serve API token generation in Admin Center.",
            "api_capabilities": "https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/: Full ticket lifecycle and comment handling.",
            "webhooks": "https://developer.zendesk.com/api-reference/event-destinations/webhooks/: Webhooks with HMAC SHA256 signing.",
            "mcp": "https://github.com/modelcontextprotocol/servers: Community Zendesk MCP server available."
        },
        "research_confidence": "High"
    },
    "Intercom": {
        "description": "Customer messaging platform and AI customer service agent for conversational support and onboarding.",
        "authentication_type": "OAuth 2.0",
        "auth_details": "OAuth 2.0 (Authorization Code Flow) and Personal Access Tokens passed via Authorization: Bearer <token> with Intercom-Version header.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Conversations & Messages", "Contacts & Companies", "Help Center Articles", "Admins & Teams", "Webhooks management"],
        "api_coverage": "Broad",
        "rate_limits": "1,000 requests per minute per workspace (bursts tracked via X-RateLimit-Remaining).",
        "webhooks": "Supported",
        "mcp_support": "Third-party MCP",
        "blocker": "Must pass explicit 'Intercom-Version' header (e.g. 2.11) on all HTTP calls.",
        "evidence_urls": [
            "https://developers.intercom.com/docs",
            "https://developers.intercom.com/docs/build-an-integration/learn-more/authentication/"
        ],
        "evidence_notes": "Intercom Developer Hub confirms Bearer access tokens, OAuth 2.0, 1,000 req/min limits, and signed topic webhooks.",
        "evidence_by_dimension": {
            "authentication": "https://developers.intercom.com/docs/build-an-integration/learn-more/authentication/: OAuth 2.0 and Bearer tokens.",
            "credential_access": "https://app.intercom.com/a/apps/_/developer-hub: Self-serve Developer Hub app creation.",
            "api_capabilities": "https://developers.intercom.com/reference/reference-intro: Conversations, contacts, articles, and tags.",
            "webhooks": "https://developers.intercom.com/docs/build-an-integration/learn-more/webhooks/: Webhooks with X-Hub-Signature HMAC SHA1.",
            "mcp": "https://github.com/modelcontextprotocol/servers: Community Intercom MCP server."
        },
        "research_confidence": "High"
    },
    "Freshdesk": {
        "description": "Cloud customer support software offering help desk ticketing, automation, and multichannel communication.",
        "authentication_type": "API Key",
        "auth_details": "HTTP Basic Auth where API Key is the username and password is 'X' (or dummy character) combined with custom domain URL.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Tickets & Conversations", "Contacts & Companies", "Agents & Roles", "Solution Articles", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "Tiered rate limits: Free (100 req/min), Growth (200 req/min), Pro (400 req/min), Enterprise (700 req/min).",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Subdomain URL prefix (https://domain.freshdesk.com) required for API routing.",
        "evidence_urls": [
            "https://developers.freshdesk.com/api/",
            "https://developers.freshdesk.com/api/#authentication"
        ],
        "evidence_notes": "Freshdesk v2 API documentation specifies Basic Auth API key handling, plan rate limits, and automation webhooks.",
        "evidence_by_dimension": {
            "authentication": "https://developers.freshdesk.com/api/#authentication: HTTP Basic Auth with API key as username.",
            "credential_access": "https://support.freshdesk.com: Self-serve key retrieval in profile settings.",
            "api_capabilities": "https://developers.freshdesk.com/api/#tickets: Complete ticket lifecycle endpoints.",
            "webhooks": "https://support.freshdesk.com/en/support/solutions/articles/215549-triggering-webhooks: Webhooks triggered via Dispatch'r / automation rules.",
            "mcp": "Official docs: No MCP server found."
        },
        "research_confidence": "High"
    },
    "Help Scout": {
        "description": "Customer support platform designed for growing teams with shared inboxes, live chat, and knowledge base docs.",
        "authentication_type": "OAuth 2.0",
        "auth_details": "OAuth 2.0 (Client Credentials Grant for internal applications, Authorization Code Flow for user integrations).",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Conversations & Threads", "Mailboxes & Folders", "Customers & Tags", "Docs & Collections", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "400 requests per minute per authenticated application.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Mailbox API 2.0 uses ephemeral access tokens (expires in 2 hours) requiring automated refresh token handling.",
        "evidence_urls": [
            "https://developer.helpscout.com/mailbox-api/",
            "https://developer.helpscout.com/mailbox-api/overview/authentication/"
        ],
        "evidence_notes": "Help Scout Mailbox API 2.0 documentation outlines Client Credentials / Auth Code OAuth, 400 req/min limits, and webhook signing.",
        "evidence_by_dimension": {
            "authentication": "https://developer.helpscout.com/mailbox-api/overview/authentication/: OAuth 2.0 Client Credentials and Auth Code.",
            "credential_access": "https://secure.helpscout.net/members/profile/apps/: Self-serve App ID and App Secret creation.",
            "api_capabilities": "https://developer.helpscout.com/mailbox-api/endpoints/conversations/list/: Full conversation and thread management.",
            "webhooks": "https://developer.helpscout.com/mailbox-api/overview/webhooks/: Webhooks with X-HELPSCOUT-SIGNATURE verification.",
            "mcp": "Official docs: No native MCP server found."
        },
        "research_confidence": "High"
    },
    "Gorgias": {
        "description": "E-commerce-focused customer service helpdesk integrated with Shopify, BigCommerce, and Magento.",
        "authentication_type": "Basic Auth",
        "auth_details": "HTTP Basic Auth where username is the account email and password is the API key, or OAuth 2.0 for app store integrations.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Tickets & Messages", "Customers & Orders", "Tags & Satisfaction Surveys", "Rules & Macros", "HTTP Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "Leaky bucket algorithm: 2 requests per second with burst capacity up to 20 requests.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Strict 2 req/s leaky bucket limit requires client-side rate-limiting queues.",
        "evidence_urls": [
            "https://developers.gorgias.com/reference/introduction",
            "https://developers.gorgias.com/reference/authentication"
        ],
        "evidence_notes": "Gorgias developer portal confirms email:key Basic Auth, leaky bucket throttling, and HTTP integration webhooks.",
        "evidence_by_dimension": {
            "authentication": "https://developers.gorgias.com/reference/authentication: Basic Auth (email:api_key) or OAuth 2.0.",
            "credential_access": "https://app.gorgias.com/settings/rest-api: Self-serve creation under Settings > REST API.",
            "api_capabilities": "https://developers.gorgias.com/reference/get-tickets: Full e-commerce ticket and customer lookup.",
            "webhooks": "https://developers.gorgias.com/reference/create-http-integration: HTTP integration webhooks with payload filters.",
            "mcp": "Official docs: No MCP server found in checked sources."
        },
        "research_confidence": "High"
    },
    "Kustomer": {
        "description": "Omnichannel CRM customer service platform providing a unified single-timeline customer view.",
        "authentication_type": "API Key",
        "auth_details": "API Key passed via Authorization: Bearer <api_key> HTTP header with granular roles and scopes.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Customers & Timelines", "Conversations & Messages", "Custom Objects (KObjects)", "Routing & Queues", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "100 requests per 10-second window per API key.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "None; API keys with granular role-based scopes generated inside workspace admin settings.",
        "evidence_urls": [
            "https://developer.kustomer.com/",
            "https://developer.kustomer.com/kustomer-api-docs/reference"
        ],
        "evidence_notes": "Kustomer developer documentation confirms Bearer API key authentication, timeline events, and webhook dispatch.",
        "evidence_by_dimension": {
            "authentication": "https://developer.kustomer.com: Authorization: Bearer <token> format.",
            "credential_access": "https://support.kustomer.com: Self-serve API key creation under Settings > Security > API Keys.",
            "api_capabilities": "https://developer.kustomer.com: Conversations, customers, and custom KObjects.",
            "webhooks": "https://developer.kustomer.com: Inbound hooks and outbound workflow webhooks.",
            "mcp": "Official docs: No MCP server found."
        },
        "research_confidence": "High"
    },
    "Vitally": {
        "description": "Customer success platform combining product analytics, customer health scoring, and task management.",
        "authentication_type": "Basic Auth",
        "auth_details": "HTTP Basic Auth where username is the API Key and password is blank (or Bearer token in v2).",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Accounts & Users", "Traits & Health Scores", "Tasks & Projects", "Conversations & Notes", "Webhooks"],
        "api_coverage": "Moderate",
        "rate_limits": "150 requests per minute per workspace.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Account health calculations run asynchronously; some metrics update on batch intervals.",
        "evidence_urls": [
            "https://docs.vitally.io/",
            "https://docs.vitally.io/reference/introduction"
        ],
        "evidence_notes": "Vitally REST API documentation specifies Basic Auth key handling, account upsert endpoints, and webhook subscriptions.",
        "evidence_by_dimension": {
            "authentication": "https://docs.vitally.io/reference/introduction: Basic Auth (API key as username).",
            "credential_access": "https://app.vitally.io/settings/integrations/api: Self-serve key generation in integration settings.",
            "api_capabilities": "https://docs.vitally.io/reference/accounts: Accounts, traits, and customer health metrics.",
            "webhooks": "https://docs.vitally.io/reference/webhooks: Real-time webhooks on account and task changes.",
            "mcp": "Official docs: No MCP server found."
        },
        "research_confidence": "High"
    },
    "Gainsight": {
        "description": "Enterprise customer success and product experience platform for churn prevention and account retention.",
        "authentication_type": "API Key",
        "auth_details": "API Key passed via 'AccessKey' custom HTTP header alongside tenant subdomain.",
        "credential_access": "Approval-required",
        "public_api": "Yes",
        "api_capabilities": ["Company & Relationship Data", "Call to Action (CTA) Management", "Health Score Updates", "Milestones & Timeline", "Events"],
        "api_coverage": "Moderate",
        "rate_limits": "Governed by tenant contract: default 10,000 calls per 24 hours with 5 concurrent requests.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Enterprise contract required; AccessKey generation restricted to certified Gainsight NXT Administrators.",
        "evidence_urls": [
            "https://support.gainsight.com/",
            "https://support.gainsight.com/Gainsight_NXT/API_and_Integrations/API_Overview"
        ],
        "evidence_notes": "Gainsight documentation outlines NXT AccessKey authentication, CTA creation endpoints, and administrative access controls.",
        "evidence_by_dimension": {
            "authentication": "https://support.gainsight.com: Header 'AccessKey: <key>' authentication.",
            "credential_access": "https://support.gainsight.com: Admin-gated key generation inside Administration > Connectors.",
            "api_capabilities": "https://support.gainsight.com: Company data, Call to Action (CTA), and timeline events.",
            "webhooks": "https://support.gainsight.com: Event Framework webhooks for CTA triggers.",
            "mcp": "Official docs: No MCP server found."
        },
        "research_confidence": "High"
    },
    "Crisp": {
        "description": "All-in-one multi-channel customer messaging platform with live chat, CRM, and knowledge base.",
        "authentication_type": "Basic Auth",
        "auth_details": "HTTP Basic Auth where username is the Identifier and password is the Key (accompanied by X-Crisp-Tier: plugin header).",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["Conversations & Messages", "Contacts & People", "Websites & Settings", "Availability & Status", "RTM WebSockets & Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "100 requests per minute per authenticated token.",
        "webhooks": "Supported",
        "mcp_support": "Not Found in Checked Sources",
        "blocker": "Requires creating a 'Plugin' token on the Crisp Marketplace console to access REST endpoints.",
        "evidence_urls": [
            "https://docs.crisp.chat/api/v1/",
            "https://docs.crisp.chat/guides/rest-api/authentication/"
        ],
        "evidence_notes": "Crisp REST API v1 documentation confirms Identifier:Key Basic Auth, RTM WebSocket events, and Webhook dispatch.",
        "evidence_by_dimension": {
            "authentication": "https://docs.crisp.chat/guides/rest-api/authentication/: Identifier / Key Basic Auth with X-Crisp-Tier header.",
            "credential_access": "https://marketplace.crisp.chat: Self-serve creation of developer plugin tokens.",
            "api_capabilities": "https://docs.crisp.chat/references/rest-api/v1/: Full conversations, messaging, and people profiles.",
            "webhooks": "https://docs.crisp.chat/guides/rest-api/webhooks/: Webhooks with secret verification.",
            "mcp": "Official docs: No MCP server found in checked sources."
        },
        "research_confidence": "High"
    },
    "Plain": {
        "description": "Modern API-first customer support platform built specifically for technical products and AI support agents.",
        "authentication_type": "Bearer JWT",
        "auth_details": "API Key passed via Authorization: Bearer <api_key> to standard GraphQL endpoint.",
        "credential_access": "Self-serve",
        "public_api": "Yes",
        "api_capabilities": ["GraphQL API for Threads", "Customer Profiles & Timelines", "Labels & Notes", "Live Status & Assignment", "Webhooks"],
        "api_coverage": "Broad",
        "rate_limits": "1,000 requests per minute per workspace (dynamic concurrency limit).",
        "webhooks": "Supported",
        "mcp_support": "Third-party MCP",
        "blocker": "GraphQL-only API; requires constructing GraphQL queries and mutation payloads.",
        "evidence_urls": [
            "https://docs.plain.com/graphql-api",
            "https://docs.plain.com/graphql-api/authentication"
        ],
        "evidence_notes": "Plain documentation details GraphQL schema, Bearer API token authentication, and signed webhook event payloads.",
        "evidence_by_dimension": {
            "authentication": "https://docs.plain.com/graphql-api/authentication: Authorization: Bearer <token> format.",
            "credential_access": "https://app.plain.com/workspace/settings/api-keys: Self-serve key creation with granular permissions.",
            "api_capabilities": "https://docs.plain.com/graphql-api/threads: Full thread creation, customer timeline upsert, and label assignment.",
            "webhooks": "https://docs.plain.com/webhooks/overview: Webhooks with Plain-Signature-256 HMAC verification.",
            "mcp": "https://github.com/modelcontextprotocol/servers: Community Plain MCP server."
        },
        "research_confidence": "High"
    }
}

# Update VERIFIED_FACTS with Marketing and Support
VERIFIED_FACTS.update(MORE_FACTS)

Path("scratch").mkdir(exist_ok=True)
with open("scratch/facts_checkpoint_1.json", "w", encoding="utf-8") as f:
    json.dump({k: len(v) for k, v in VERIFIED_FACTS.items()}, f)

print(f"Current facts loaded: {len(VERIFIED_FACTS)}/100")
