from .models import Partner

def partners(request):
    return {
        "partner_logos_default": Partner.objects.all()
    }