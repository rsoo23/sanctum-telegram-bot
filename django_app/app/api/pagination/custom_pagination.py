from rest_framework.pagination import CursorPagination


class LeaderboardCursorGoldPagination(CursorPagination):
    page_size = 10
    ordering = ["-gold", "-created_at"]
    # ordering = ("-gold", "-referral_count")

    # def get_ordering(self, request, queryset, view):
    #     ordering = "-gold"
    #     if "type" in request.query_params:
    #         type = request.query_params.get("type")
    #         if type == "gold":
    #             ordering = "-gold"
    #         elif type == "referral":
    #             ordering = "-referral_count"
    #     else:
    #         ordering = ("-gold", "-referral_count")
    #     print(
    #         "----------------------------------------------------------------------------------"
    #     )
    #     print(f"Ordering: {ordering}")
    #     return tuple(ordering)
    #
    # def paginate_queryset(self, queryset, request, view=None):
    #     self.ordering = self.get_ordering(request, queryset, view)
    #     paginate_queryset = super().paginate_queryset(queryset, request, view)
    #     if self.ordering:
    #         paginate_queryset = paginate_queryset.order_by(*self.ordering)
    #     print(f"Final Query: {queryset.query}")
    #     return paginate_queryset
    #     # return super().paginate_queryset(queryset, request, view)
    #
    # def get_paginated_response(self, data):
    #     return super().get_paginated_response(data)


class LeaderboardCursorReferralPagination(CursorPagination):
    page_size = 10
    ordering = ["-referral_count", "-created_at"]
