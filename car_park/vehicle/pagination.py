from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  # Позволяет задавать размер страницы через параметр запроса
    max_page_size = 50  # Максимальный размер страницы
