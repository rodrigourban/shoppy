from django.shortcuts import redirect
from django.utils import timezone
from django.views import View


from .models import Coupon


class CouponApplyView(View):
    def post(self, request):
        now = timezone.now()
        code = request.POST.get("code", "")
        try:
            coupon = Coupon.objects.get(
                code__iexact=code, valid_from__lte=now, valid_to__gte=now
            )
            self.request.session["coupon_id"] = coupon.id
        except Coupon.DoesNotExist:
            self.request.session["coupon_id"] = None

        return redirect("cart:list")
