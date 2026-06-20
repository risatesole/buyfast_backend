from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def checkout_timeslots_api_view(request):
    return Response({
        "availableDates": [
            {
            "date": "2026-06-20",
            "slots": ["09:00", "10:00", "14:00","17:25"]
            },
            {
            "date": "2026-06-21",
            "slots": ["11:00", "15:00"]
            },
            
            {
            "date": "2026-06-22",
            "slots": ["11:00", "15:00"]
            }
        ]}
    )
