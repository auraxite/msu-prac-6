import http.server

http.server.test(
    HandlerClass=http.server.SimpleHTTPRequestHandler,
    port=8000,
    bind="10.4.42.253",
)

# 10.4.58.112 - Саня
# cp public/auraxite/hooks/post-update.sample public/auraxite/hooks/post-update
# cat public/auraxite/.git/hooks/post-update