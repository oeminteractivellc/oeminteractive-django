import logging

from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class ProgressView(views.APIView):
  def get(self, request, *args, **kwargs):
    progress_id = self.kwargs.get("progress_id")
    progress = get_object_or_404(request.user.uploads.all(), id=progress_id)
    return Response({
        "status": progress.status,
        "rows_processed": progress.rows_processed,
        "objects_added": progress.objects_added,
        "objects_updated": progress.objects_updated,
        "errors": progress.errors,
    })
