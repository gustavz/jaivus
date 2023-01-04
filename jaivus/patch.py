import logging
import queue

from streamlit_webrtc.receive import MediaReceiver

logger = logging.getLogger(__name__)

QUEUE_SIZE = 1024


async def _run_track_patch(self, track):
    while True:
        try:
            frame = await track.recv()
        except Exception:
            return
        if self._frames_queue.full():
            if self._frame_read:
                logger.warning("Queue overflow. Emptying queue.")
            self._frames_queue = queue.Queue(QUEUE_SIZE)
        self._frames_queue.put(frame)


# we patch the asyn _run_trac method to empty the queue if it overflows
MediaReceiver._run_track = _run_track_patch
