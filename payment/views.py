import datetime

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render


from payment.models import Payment


def sum_payments(request):
    if not request.user.is_authenticated and not request.user.is_superuser:
        return render(request, "forbidden.html", status=403)

    from_str = request.GET.get('from')
    to_str = request.GET.get('to')

    if from_str:
        from_datetime = datetime.datetime.strptime(from_str, '%Y-%m-%d')
    else:
        from_datetime = datetime.datetime.now().replace(month=datetime.datetime.now().month-1)

    if to_str:
        to_datetime = datetime.datetime.strptime(to_str, '%Y-%m-%d') + datetime.timedelta(days=1)
    else:
        to_datetime = datetime.datetime.now()

    d = Payment.objects.filter(done=True,
                               updated__gte=from_datetime,
                               updated__lte=to_datetime).aggregate(Sum('amount'))

    data = {'amount': d}

    return JsonResponse(data=data)
