import { useEffect, useMemo, useState } from 'react';
import apiClient from '../services/api';

const parseBlobErrorDetail = async (blob) => {
  if (!blob || typeof blob.text !== 'function') return '';
  try {
    const text = await blob.text();
    if (!text) return '';
    const parsed = JSON.parse(text);
    return parsed?.detail || parsed?.error || '';
  } catch {
    return '';
  }
};

const toFriendlyMessage = (detail, status) => {
  const normalized = String(detail || '').toLowerCase();
  if (normalized.includes('no camera frame available')) {
    return 'No camera frame yet. Start vision service and wait a few seconds for first annotated frame.';
  }
  if (normalized.includes('frame directory not found')) {
    return 'Frame directory not found. Ensure vision saves frames to ./vision/frames and backend VISION_FRAME_DIR is correct.';
  }
  if (status === 404) {
    return 'No frame endpoint data yet (404). Check vision service is running and producing frames.';
  }
  return detail || 'Camera feed unavailable right now.';
};

const CameraFeed = () => {
  const [imageUrl, setImageUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const feedPath = useMemo(
    () => import.meta.env.VITE_CAMERA_FEED_PATH || '/camera/latest-frame',
    []
  );
  const pollMs = Number(import.meta.env.VITE_CAMERA_POLL_MS || 1000);

  useEffect(() => {
    let timerId = null;
    let activeObjectUrl = '';

    const fetchFrame = async () => {
      try {
        const response = await apiClient.get(feedPath, {
          responseType: 'blob',
          params: { _ts: Date.now() },
        });
        const nextUrl = URL.createObjectURL(response.data);
        if (activeObjectUrl) {
          URL.revokeObjectURL(activeObjectUrl);
        }
        activeObjectUrl = nextUrl;
        setImageUrl(nextUrl);
        setError('');
      } catch (err) {
        const status = err?.response?.status;
        const blobDetail = await parseBlobErrorDetail(err?.response?.data);
        const detail = blobDetail || err?.userMessage || '';
        setError(toFriendlyMessage(detail, status));
      } finally {
        setLoading(false);
      }
    };

    fetchFrame();
    timerId = setInterval(fetchFrame, pollMs);

    return () => {
      if (timerId) clearInterval(timerId);
      if (activeObjectUrl) URL.revokeObjectURL(activeObjectUrl);
    };
  }, [feedPath, pollMs]);

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900">Live Camera Detection</h3>
        <span className="text-xs text-gray-500">Refresh {pollMs}ms</span>
      </div>

      <div className="aspect-video w-full overflow-hidden rounded-md bg-gray-100 border border-gray-200 flex items-center justify-center">
        {imageUrl ? (
          <img src={imageUrl} alt="Latest annotated camera frame" className="w-full h-full object-cover" />
        ) : (
          <p className="text-sm text-gray-500 px-4 text-center">
            {loading ? 'Loading camera feed...' : error || 'No frame available.'}
          </p>
        )}
      </div>

      {error && !loading && (
        <p className="mt-2 text-xs text-amber-700">
          {error}
        </p>
      )}
    </div>
  );
};

export default CameraFeed;
