"""Fail-closed handling for reverse-proxy metadata.

Only the immediate socket peer can establish proxy trust. Forwarded headers are
removed before the request reaches routing code.
"""
import ipaddress


_FORWARDING_HEADERS = {
    b"forwarded",
    b"x-forwarded-for",
    b"x-forwarded-host",
    b"x-forwarded-proto",
    b"x-forwarded-port",
    b"x-real-ip",
}


class TrustedProxyMiddleware:
    def __init__(self, app, *, trusted_proxy_networks=(), canonical_hosts=()):
        self.app = app
        self.trusted_proxy_networks = tuple(trusted_proxy_networks)
        self.canonical_hosts = frozenset(host.lower() for host in canonical_hosts)

    def _is_trusted_peer(self, scope) -> bool:
        client = scope.get("client")
        if not client:
            return False
        try:
            address = ipaddress.ip_address(client[0])
        except ValueError:
            return False
        return any(address in network for network in self.trusted_proxy_networks)

    @staticmethod
    def _values(headers, name):
        return [value.decode("latin-1").strip() for key, value in headers if key.lower() == name]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = list(scope.get("headers", []))
        trusted = self._is_trusted_peer(scope)
        forwarded_proto = self._values(headers, b"x-forwarded-proto")
        forwarded_host = self._values(headers, b"x-forwarded-host")
        forwarded_for = self._values(headers, b"x-forwarded-for")
        host_values = self._values(headers, b"host")

        def reject():
            body = b"Invalid request authority or proxy metadata."
            return {
                "type": "http.response.start",
                "status": 400,
                "headers": [(b"content-type", b"text/plain; charset=utf-8"),
                            (b"content-length", str(len(body)).encode("ascii"))],
            }, {"type": "http.response.body", "body": body}

        # A trusted proxy is the sole authority for the external scheme. Missing,
        # duplicated, list-valued, blank, or downgraded metadata is ambiguous and
        # must never result in an HTTP request reaching cookie-issuing routes.
        client_address = None
        if trusted:
            if len(forwarded_proto) != 1 or forwarded_proto[0].lower() != "https":
                start, body = reject()
                await send(start)
                await send(body)
                return
            # The ingress must overwrite X-Forwarded-For with exactly one client
            # address. Never trust a client-supplied chain or an arbitrary hop.
            if len(forwarded_for) != 1 or "," in forwarded_for[0] or not forwarded_for[0]:
                start, body = reject()
                await send(start)
                await send(body)
                return
            try:
                client_address = str(ipaddress.ip_address(forwarded_for[0]))
            except ValueError:
                start, body = reject()
                await send(start)
                await send(body)
                return

        normalized_host = None
        if trusted and forwarded_host:
            if len(forwarded_host) != 1 or "," in forwarded_host[0]:
                start, body = reject()
                await send(start)
                await send(body)
                return
            normalized_host = forwarded_host[0].lower()
            if not self.canonical_hosts or normalized_host not in self.canonical_hosts:
                start, body = reject()
                await send(start)
                await send(body)
                return

        if self.canonical_hosts:
            if len(host_values) != 1 or "," in host_values[0]:
                start, body = reject()
                await send(start)
                await send(body)
                return
            request_host = (normalized_host or host_values[0]).lower()
            if request_host not in self.canonical_hosts:
                start, body = reject()
                await send(start)
                await send(body)
                return

        clean_headers = [(key, value) for key, value in headers if key.lower() not in _FORWARDING_HEADERS]
        if normalized_host is not None:
            clean_headers = [
                (key, value) for key, value in clean_headers if key.lower() != b"host"
            ]
            clean_headers.append((b"host", normalized_host.encode("latin-1")))

        child_scope = dict(scope)
        child_scope["headers"] = clean_headers
        if trusted:
            # Retain the immediate proxy peer for diagnostics while exposing only
            # the edge-validated client address to application rate-limit logic.
            child_scope["maalenex.proxy_peer"] = scope.get("client")
            child_scope["client"] = (client_address, scope["client"][1])
            child_scope["scheme"] = "https"

        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                response_headers = list(message.get("headers", []))
                present = {key.lower() for key, _ in response_headers}
                required = (
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"x-frame-options", b"DENY"),
                    (b"permissions-policy", b"geolocation=(), camera=(), microphone=()"),
                )
                for key, value in required:
                    if key not in present:
                        response_headers.append((key, value))
                message = dict(message)
                message["headers"] = response_headers
            await send(message)

        await self.app(child_scope, receive, send_with_security_headers)
