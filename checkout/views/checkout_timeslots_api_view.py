from django.http import JsonResponse


def checkout_timeslots_api_view(request):
    if request.method != "GET":
        return JsonResponse(
            {
                "status": "error",
                "message": "Método no permitido",
            },
            status=405
        )

    return JsonResponse({
        "availableDates": [
            {
                "date": "2026-06-20",
                "slots": ["09:00", "10:00", "14:00", "17:25"]
            },
            {
                "date": "2026-06-21",
                "slots": ["11:00", "15:00"]
            },
            {
                "date": "2026-06-22",
                "slots": ["11:00", "15:00"]
            }
        ]
    })