import { useState, useCallback, useEffect } from 'react';
import { ServerToClientEvent } from '../types';
import axios from 'axios';

const WebSocket_URL = 'ws://127.0.0.1:8000/api/v1/ws/chat';

export const useWebSocket = (accessToken: string | null) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [chatOverviewList, setChatOverviewList] = useState<any[]>([]);

  const connectSocket = (token: string) => {
    const ws = new WebSocket(`${WebSocket_URL}?access_token=${token}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.event as ServerToClientEvent) {
        case 'message_sent':
          setMessages((prevMessages) => [...prevMessages, data.data]);
          break;
        case 'chat_overview_list_sent':
          setChatOverviewList(data.data);
          break;
        default:
          break;
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    setSocket(ws);
  };

  const reconnectSocket = useCallback((token: string) => {
    if (socket) {
      socket.close(); // Close the old socket if it exists
    }
    connectSocket(token);
  }, [socket]);

  const sendMessage = (chatId: string, message: string) => {
    if (socket) {
      socket.send(JSON.stringify({
        event: 'new_message',
        data: { chatId, text: message },
      }));
    }
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        const response = await axios.post('http://127.0.0.1:8000/api/v1/auth/refresh', { refresh_token: refreshToken });
        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);
        reconnectSocket(access_token); // Reconnect WebSocket with new token
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
    }
  };

  useEffect(() => {
    if (accessToken) {
      connectSocket(accessToken);
    }
  }, [accessToken]);

  return { socket, sendMessage, messages, chatOverviewList, reconnectSocket, refreshToken };
};
