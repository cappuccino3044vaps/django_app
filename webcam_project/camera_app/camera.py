import cv2
import threading
import time
import numpy as np
from django.conf import settings


class CameraError(Exception):
    """カメラ操作に関するエラー"""
    pass


class Camera:
    """カメラ操作を管理するクラス"""
    
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.video = None
        self.frame = None
        self.is_running = False
        self.lock = threading.Lock()
        self.error = None
        self._connect()
    
    def _connect(self):
        """カメラに接続する"""
        try:
            self.video = cv2.VideoCapture(self.camera_id)
            if not self.video.isOpened():
                raise CameraError(f"カメラID {self.camera_id} に接続できませんでした。")
        except Exception as e:
            self.error = str(e)
            raise CameraError(f"カメラの初期化エラー: {str(e)}")
    
    def start(self):
        """カメラのキャプチャを開始する"""
        if self.is_running:
            return
        
        if self.video is None or not self.video.isOpened():
            self._connect()
            
        self.is_running = True
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
    
    def _update(self):
        """カメラからフレームを取得し続けるスレッド"""
        while self.is_running:
            try:
                if self.video is None or not self.video.isOpened():
                    self.error = "カメラ接続が切断されました。"
                    self.is_running = False
                    break
                    
                success, frame = self.video.read()
                if not success:
                    self.error = "フレームの取得に失敗しました。"
                    time.sleep(0.5)  # 少し待ってからリトライ
                    continue
                
                with self.lock:
                    self.frame = frame
                    self.error = None
                    
                time.sleep(1/30)  # フレームレートの制御（約30FPS）
            except Exception as e:
                self.error = f"フレーム取得エラー: {str(e)}"
                time.sleep(1)
    
    def get_frame(self):
        """現在のフレームをJPEG形式でエンコードして返す"""
        if self.error:
            # エラー状態を示す画像を生成
            error_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                error_img, 
                f"カメラエラー: {self.error}", 
                (50, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, 
                (255, 255, 255), 
                2
            )
            _, jpeg = cv2.imencode('.jpg', error_img)
            return jpeg.tobytes()
            
        with self.lock:
            if self.frame is None:
                # フレームが無い場合の代替画像
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(
                    blank, 
                    "カメラ起動中...", 
                    (220, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, 
                    (255, 255, 255), 
                    2
                )
                _, jpeg = cv2.imencode('.jpg', blank)
            else:
                # 実際のカメラフレーム
                _, jpeg = cv2.imencode('.jpg', self.frame)
                
        return jpeg.tobytes()
    
    def stop(self):
        """カメラのキャプチャを停止する"""
        self.is_running = False
        if self.video is not None:
            self.video.release()
            self.video = None
        self.frame = None
    
    def __del__(self):
        self.stop()
