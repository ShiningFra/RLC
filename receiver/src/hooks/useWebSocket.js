import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

export function useWebSocket(onMessage) {
  const socketRef = useRef();

  useEffect(() => {
    socketRef.current = io('http://localhost:3000/rlc');
    socketRef.current.on('packet', onMessage);
    socketRef.current.on('ack', () => console.log('ACK broadcast received'));
    return () => socketRef.current.disconnect();
  }, [onMessage]);

  const send = (event, payload) => socketRef.current.emit(event, payload);
  return { send };
}
