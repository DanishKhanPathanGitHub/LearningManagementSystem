import time
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

class QueryLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        self.start_time = time.time()

    def process_response(self, request, response):
        print('-'*100, 'started')
        total_time = (time.time() - self.start_time) * 1000  # Convert to milliseconds
        print(f"\n{'-'*20} REQUEST LOG {'-'*30}")
        print(f"Path: {request.path}")
        print(f"Method: {request.method}")
        print(f"Total time: {total_time:.2f}ms")
        print('-'*100, 'completed')
        # Log each SQL query with formatting
        count = 1
        for query in connection.queries:
            print(f"\n{'-'*10} QUERY {count} {'-'*10}")
            print(f"SQL: {query['sql']}")
            print(f"Time: {query['time']}s")
            print('-' * 70)
            count+=1
        print(f"{'-'*55}\n")
        return response