from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

class ProductCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-id"
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "data": data,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        })
