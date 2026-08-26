import sys
sys.path.insert(0, '.')
from camera.camera_manager import camera_manager
import threading

print('=== PIPELINES ===')
for name, pipeline in camera_manager.pipelines.items():
    stream = getattr(pipeline, 'stream', None)
    worker = getattr(pipeline, 'worker', None)
    running = getattr(pipeline, 'is_running', False)
    print(f'{name}: running={running}, stream={stream is not None}, worker={worker is not None}')

print('\n=== ALL THREADS ===')
for t in threading.enumerate():
    print(f'  {t.name} (daemon={t.daemon})')
