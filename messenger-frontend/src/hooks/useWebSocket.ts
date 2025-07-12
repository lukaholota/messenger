import { useState, useEffect } from 'react';
import axios from 'axios';
import type { Message, ChatOverview, IncomingMessage, ServerToClientEvent } from '../types';

const WS_URL = 'ws://127.0.0.1:8000/api/v1/ws/chat';

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch (e) {
    return true;
  }
}

async function refreshToken(): Promise<string | null> {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      const res = await axios.post('http://127.0.0.1:8000/api/v1/auth/refresh', { refresh_token: refreshToken });
      const { access_token } = res.data;
      localStorage.setItem('access_token', access_token);
      return access_token;
    }
  } catch (err) {
    console.error('Token refresh failed', err);
  }
  return null;
}

export const useWebSocket = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatOverviewList, setChatOverviewList] = useState<ChatOverview[]>([]);

  const connectSocket = async () => {
    let token = localStorage.getItem('access_token');

    if (!token || isTokenExpired(token)) {
      token = await refreshToken();
    }

    if (!token) {
      console.error('No valid access token, cannot connect WebSocket');
      return;
    }

    const ws = new WebSocket(`${WS_URL}?access_token=${token}`);

    ws.onopen = () => console.log('WebSocket connected');
    ws.onmessage = (event) => {
      const message: IncomingMessage = JSON.parse(event.data);
      switch (message.event as ServerToClientEvent) {
        case 'message_sent':
          setMessages((prev) => [...prev, message.data as Message]);
          break;
        case 'chat_overview_list_sent':
          setChatOverviewList(message.data as ChatOverview[]);
          break;
        case 'undelivered_messages_sent':
          console.log('Undelivered messages:', message.data);
          setMessages((prev) => [...prev, ...(message.data as Message[])]);
          break;
        default:
          console.warn('Unhandled WebSocket event:', message.event);
          break;
      }
    };
    ws.onclose = () => console.log('WebSocket disconnected');
    ws.onerror = (err) => console.error('WebSocket error:', err);

    setSocket(ws);
  };

  useEffect(() => {
    connectSocket();
  }, []);

  const sendMessage = (chatId: number, content: string) => {
    socket?.send(
      JSON.stringify({
        event: 'new_message',
        data: { chat_id: chatId, content: content },
      })
    );
  };

  return { sendMessage, messages, chatOverviewList };
};
