from django.shortcuts import render

def vendor_add_view(request):
    return render(request, 'vendors/vendor_add.html')

def vendor_view(request):
    context = {'vendors': mock_db.VENDORS}
    return render(request, 'vendors/vendor_view.html', context)
