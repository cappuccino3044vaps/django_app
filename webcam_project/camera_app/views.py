import json
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .camera import Camera, CameraError

# グローバルなカメラインスタンス
camera = None

def get_camera():
    """グローバルカメラインスタンスの取得または初期化"""
    global camera
    if camera is None:
        camera = Camera()
        camera.start()
    return camera

def gen_frames():
    """ビデオストリーム用のフレーム生成ジェネレータ"""
    cam = get_camera()
    while True:
        frame = cam.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@require_GET
def index(request):
    """メインページを表示"""
    return render(request, 'camera_app/index.html')

@require_GET
def video_feed(request):
    """ビデオストリームのエンドポイント"""
    return StreamingHttpResponse(
        gen_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

@require_POST
@csrf_exempt
def camera_control(request):
    """カメラ制御APIエンドポイント"""
    global camera
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'start':
            get_camera().start()
            return JsonResponse({'status': 'success', 'message': 'カメラを開始しました'})
        
        elif action == 'stop':
            if camera:
                camera.stop()
            return JsonResponse({'status': 'success', 'message': 'カメラを停止しました'})
        
        elif action == 'switch':
            camera_id = int(data.get('camera_id', 0))
            if camera:
                camera.stop()
            camera = Camera(camera_id)
            camera.start()
            return JsonResponse({'status': 'success', 'message': f'カメラ #{camera_id} に切り替えました'})
        
        return JsonResponse({'status': 'error', 'message': '無効なアクション'}, status=400)
    
    except CameraError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_GET
def camera_status(request):
    """カメラの状態を返すエンドポイント"""
    global camera
    cam = get_camera()
    return JsonResponse({
        'running': cam.is_running,
        'error': cam.error,
        'camera_id': cam.camera_id
    })
