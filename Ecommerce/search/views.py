from django.shortcuts import render
from django.views import View
from shop.models import Products
from django.db.models import Q

class SearchView(View):
    def get(self, request):
        query = request.GET.get('q')
        print(query)
        if query:
            p = Products.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(price__icontains=query)
            )
        else:
            p = Products.objects.none()  # Empty queryset if no query

        context = {'products':p}
        return render(request, "search.html", context)