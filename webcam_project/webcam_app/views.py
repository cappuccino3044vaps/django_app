import cv2
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render

def index(request):
    cameras = get_available_cameras()
    return render(request, 'webcam_app/index.html', {'cameras': cameras})

def get_available_cameras():
    cameras = []
    for i in range(10):  # 最大10台まで検索
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append(i)
            cap.release()
    return cameras

def camera_list(request):
    cameras = get_available_cameras()
    return JsonResponse({'cameras': cameras})

def gen_frames(camera_id):
    camera = cv2.VideoCapture(camera_id)
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        camera.release()

def camera_stream(request, camera_id):
    return StreamingHttpResponse(
        gen_frames(camera_id),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )