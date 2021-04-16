from rest_framework import pagination
from rest_framework.response import Response


class CustomPageNumberPagination(pagination.PageNumberPagitation):
    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "page": self.page.number,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "per_page": self.page_size,
                "results": data,
            }
        )
