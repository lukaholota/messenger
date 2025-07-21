import {useCallback, useEffect, useState} from 'react';
import axios from 'axios';
import type {
    ChatInfo,
    ChatOverview,
    IncomingMessage,
    Message,
    ServerToClientEvent
} from '../types';

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
            const res = await axios.post('http://127.0.0.1:8000/api/v1/auth/refresh', {refresh_token: refreshToken});
            const {access_token} = res.data;
            localStorage.setItem('access_token', access_token);
            return access_token;
        }
    } catch (err) {
        console.error('Token refresh failed', err);
    }
    return null;
}

const mergeAndSortMessages = (existing: Message[] = [], incoming: Message[]): Message[] => {
    const messageMap = new Map<number, Message>();

    [...existing, ...incoming].forEach(msg => {
        messageMap.set(msg.message_id, msg);
    });

    return Array.from(messageMap.values()).sort(
        (a, b) => new Date(a.sent_at).getTime() - new Date(b.sent_at).getTime()
    )
}

export const useWebSocket = () => {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [messagesByChat, setMessagesByChat] = useState<Record<number, Message[]>>({});
    const [chatOverviewList, setChatOverviewList] = useState<ChatOverview[]>([]);
    const [chatInfo, setChatInfo] = useState<ChatInfo | null>(null);

    const connectSocket = useCallback( async () => {
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
            console.log('new event arrived')
            switch (message.event as ServerToClientEvent) {
                case 'message_sent': {
                    console.log('event "message_sent" arrived')

                    const newMessage = message.data as Message;
                    const {chat_id} = newMessage;

                    console.log(`new message - '${newMessage.content}' at chat_id=${chat_id}`);

                    setMessagesByChat(prev => {
                        const currentMessages = prev[chat_id] || [];
                        const lastMessage = currentMessages[currentMessages.length - 1];

                        if (!lastMessage || new Date(newMessage.sent_at) >= new Date(lastMessage.sent_at)) {
                            return {
                                ...prev,
                                [chat_id]: [...currentMessages, newMessage]
                            };
                        }

                        console.warn(`Message arrived out of order in chat ${chat_id}. Resporting`);
                        return {
                            ...prev,
                            [chat_id]: mergeAndSortMessages(currentMessages, [newMessage]),
                        };
                    });
                    break;
                }
                case 'chat_overview_list_sent': {
                    setChatOverviewList(message.data as ChatOverview[]);
                    break;
                }
                case 'undelivered_messages_sent': {
                    const undelivered = message.data as Message[];
                    if (undelivered.length === 0) break;

                    const undeliveredByChat = undelivered.reduce((acc, msg) => {
                        if (!acc[msg.chat_id]) {
                            acc[msg.chat_id] = [];
                        }
                        acc[msg.chat_id].push(msg);
                        return acc;
                    }, {} as Record<number, Message[]>);

                    setMessagesByChat((prev) => {
                        const newState = {...prev};
                        for (const chatId in undeliveredByChat) {
                            newState[chatId] = mergeAndSortMessages(prev[chatId], undeliveredByChat[chatId]);
                        }
                        return newState;
                    });
                    break;
                }
                case 'chat_info_sent': {
                    setChatInfo(message.data as ChatInfo)
                    break;
                }
                case 'chat_messages_sent': {
                    const {chat_id, messages} = message.data as {
                        chat_id: number;
                        messages: Message[]
                    };
                    const validMessages = Array.isArray(messages) ? messages : [];

                    setMessagesByChat(prev => ({
                        ...prev,
                        [chat_id]: mergeAndSortMessages(prev[chat_id], validMessages)
                    }));
                    break;
                }
                default:
                    console.warn('Unhandled WebSocket event:', message.event);
                    break;
            }
        };
        ws.onclose = () => console.log('WebSocket disconnected');
        ws.onerror = (err) => console.error('WebSocket error:', err);

        setSocket(ws);
    }, []);

    useEffect(() => {
        connectSocket();
    }, [connectSocket]);

    const sendMessage = useCallback((chatId: number, content: string) => {
        socket?.send(
            JSON.stringify({
                event: 'new_message',
                data: {chat_id: chatId, content: content},
            })
        );
    }, [socket]);

    const requestChatInfo = useCallback((chatId: number) => {
        socket?.send(JSON.stringify({
            event: 'get_chat_info',
            data: {chat_id: chatId}
        }))
    }, [socket]);

    const requestChatMessages = useCallback((chatId: number) => {
        socket?.send(JSON.stringify({
            event: 'get_chat_messages',
            data: {chat_id: chatId}
        }))
    }, [socket]);

    return {
        sendMessage,
        messagesByChat,
        chatOverviewList,
        chatInfo,
        requestChatInfo,
        requestChatMessages
    };
};
