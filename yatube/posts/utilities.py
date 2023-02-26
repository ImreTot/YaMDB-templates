from django.core.paginator import Paginator

POST_AMOUNT = 10


def post_paginator(objects_list, request):
    paginator = Paginator(objects_list, POST_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
