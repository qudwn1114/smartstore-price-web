from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
import datetime

def summernote_image_upload_view(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        uploaded_files = request.FILES.getlist('files')
        file_urls = []

        for file in uploaded_files:
            # 파일 저장 (예: 미디어 디렉터리로 저장)
            file_path = default_storage.save(f"summernote/{datetime.datetime.now().date()}/{file.name}", file)
            file_url = default_storage.url(file_path)
            absolute_url = f"{settings.SITE_URL}{file_url}"
            file_urls.append(absolute_url)

        return JsonResponse({'urls': file_urls})  # 여러 파일 URL 반환

    return JsonResponse({'error': '파일이 없습니다.'}, status=400)