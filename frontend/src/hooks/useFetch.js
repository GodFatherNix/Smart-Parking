import { useState, useEffect } from 'react';

export const useFetch = (fetchFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await fetchFunction();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch data');
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error };
};

export const usePolling = (fetchFunction, interval = 5000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const poll = async () => {
      try {
        setLoading(true);
        const result = await fetchFunction();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    poll();
    const timer = setInterval(poll, interval);

    return () => clearInterval(timer);
  }, [fetchFunction, interval]);

  return { data, loading, error };
};
