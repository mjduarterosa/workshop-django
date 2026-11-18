class SimpleLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Request: {request.method} {request.path}")   # before the view
        response = self.get_response(request)
        print(f"Response status: {response.status_code}")    # after the view
        return response
