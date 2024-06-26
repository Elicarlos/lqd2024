class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        frame_ancestors = "'self' https://lqd2024-ff3963465f8b.herokuapp.com https://teste-teste-lqd2024-fdb4a1ec713e.herokuapp.com"
        response['Content-Security-Policy'] = f"frame-ancestors {frame_ancestors}"
        return response