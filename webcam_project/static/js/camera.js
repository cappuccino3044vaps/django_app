$(document).ready(function() {
    // 要素の参照
    const cameraFeed = $('#cameraFeed');
    const loadingOverlay = $('#loadingOverlay');
    const connectionStatus = $('#connectionStatus');
    const cameraRunning = $('#cameraRunning');
    const cameraId = $('#cameraId');
    const errorAlert = $('#errorAlert');
    const errorMessage = $('#errorMessage');
    
    // ボタン要素の参照
    const startButton = $('#startCamera');
    const stopButton = $('#stopCamera');
    const switchButton = $('#switchCamera');
    const cameraSelect = $('#cameraSelect');
    
    // 初期状態の設定
    let isVideoLoaded = false;
    
    // カメラフィードのロード状態監視
    cameraFeed.on('load', function() {
        loadingOverlay.hide();
        isVideoLoaded = true;
        updateStatus(true);
    });
    
    cameraFeed.on('error', function() {
        showError("カメラ映像の読み込みに失敗しました");
        loadingOverlay.show();
        isVideoLoaded = false;
        updateStatus(false);
    });
    
    // 状態更新関数
    function updateStatus(isConnected) {
        if (isConnected) {
            connectionStatus.removeClass('bg-danger').addClass('bg-success').text('接続中');
            cameraRunning.removeClass('bg-danger').addClass('bg-success').text('実行中');
        } else {
            connectionStatus.removeClass('bg-success').addClass('bg-danger').text('切断');
            cameraRunning.removeClass('bg-success').addClass('bg-danger').text('停止中');
        }
    }
    
    // エラー表示関数
    function showError(message) {
        errorMessage.text(message);
        errorAlert.removeClass('d-none');
        setTimeout(() => {
            errorAlert.addClass('d-none');
        }, 5000);
    }
    
    // カメラ状態の定期的な取得
    function refreshCameraStatus() {
        $.get('/api/camera_status/', function(data) {
            updateStatus(data.running);
            cameraId.text(data.camera_id);
            
            if (data.error) {
                showError(data.error);
            }
        }).fail(function(jqXHR) {
            showError("サーバー接続エラー: " + jqXHR.status);
            updateStatus(false);
        });
    }
    
    // 定期的なステータス更新（3秒ごと）
    setInterval(refreshCameraStatus, 3000);
    refreshCameraStatus(); // 初期状態の取得
    
    // ボタンのイベントハンドラ
    startButton.on('click', function() {
        $.ajax({
            url: '/api/camera_control/',
            method: 'POST',
            data: JSON.stringify({ action: 'start' }),
            contentType: 'application/json',
            beforeSend: function() {
                loadingOverlay.show();
            },
            success: function(response) {
                // リロードしてカメラ接続を更新
                cameraFeed.attr('src', cameraFeed.attr('src'));
                refreshCameraStatus();
            },
            error: function(jqXHR) {
                showError("カメラ開始エラー: " + (jqXHR.responseJSON?.message || jqXHR.status));
                loadingOverlay.hide();
            }
        });
    });
    
    stopButton.on('click', function() {
        $.ajax({
            url: '/api/camera_control/',
            method: 'POST',
            data: JSON.stringify({ action: 'stop' }),
            contentType: 'application/json',
            success: function(response) {
                updateStatus(false);
                loadingOverlay.show();
                refreshCameraStatus();
            },
            error: function(jqXHR) {
                showError("カメラ停止エラー: " + (jqXHR.responseJSON?.message || jqXHR.status));
            }
        });
    });
    
    switchButton.on('click', function() {
        const selectedCamera = cameraSelect.val();
        
        $.ajax({
            url: '/api/camera_control/',
            method: 'POST',
            data: JSON.stringify({ 
                action: 'switch',
                camera_id: selectedCamera
            }),
            contentType: 'application/json',
            beforeSend: function() {
                loadingOverlay.show();
            },
            success: function(response) {
                // リロードしてカメラ接続を更新
                cameraFeed.attr('src', cameraFeed.attr('src'));
                cameraId.text(selectedCamera);
                refreshCameraStatus();
            },
            error: function(jqXHR) {
                showError("カメラ切替エラー: " + (jqXHR.responseJSON?.message || jqXHR.status));
                loadingOverlay.hide();
            }
        });
    });
    
    // ページが閉じられる前にカメラを停止する
    $(window).on('beforeunload', function() {
        $.ajax({
            url: '/api/camera_control/',
            method: 'POST',
            data: JSON.stringify({ action: 'stop' }),
            contentType: 'application/json',
            async: false
        });
    });
});
