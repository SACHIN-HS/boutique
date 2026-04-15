from django.shortcuts import render


def tailoring_view(request):
    context = {
        'tailors': [],
        'jobs': mock_db.TAILORING_JOBS
    }
    return render(request, 'tailoring/tailoring.html', context)
