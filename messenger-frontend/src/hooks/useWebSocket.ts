import {useCallback, useEffect, useState} from 'react';
import axios from 'axios';
import type {
    ChatInfo,
    ChatOverview, Contact,
    IncomingMessage,
    Message, NewMessagePayload, SearchUser,
    ServerToClientEvent
} from '../types';

const WS_URL = 'ws://127.0.0.1:8000/api/v1/ws/chat';

function isTokenExpired(token: string): boolean {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
    } catch (e) {
        console.error('Token parsing failed:', e);
        return true;
    }
}

async function refreshToken(): Promise<string | null> {
    try {
        console.log('Refreshing token...');
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
            console.warn('No refresh token found in localStorage');
            logoutUser();
            return null;
        }
        const res = await axios.post(
            'http://127.0.0.1:8000/api/v1/auth/refresh',
            {refresh_token: refreshToken}
        );

        const {access_token} = res.data;
        console.log('Token refreshed successfully');
        localStorage.setItem('access_token', access_token);
        return access_token;

    } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 401) {
            console.warn('Refresh token expired, logging out...')
            logoutUser();
        } else {
            console.error('Token refresh failed', err);
        }
    }
    return null;
}

function logoutUser() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.reload();
}

const mergeAndSortMessages = (existing: Message[] = [], incoming: Message[] = []): Message[] => {
    if (!existing) existing = []

    const messageMap = new Map<number, Message>();
    [...existing, ...incoming].forEach(msg => {
        messageMap.set(msg.message_id, msg);
    });
    const sorted = Array.from(messageMap.values()).sort(
        (a, b) => new Date(a.sent_at).getTime() - new Date(b.sent_at).getTime()
    );
    console.log('sorted messages: ', sorted)
    return sorted
};

export const useWebSocket = () => {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [messagesByChat, setMessagesByChat] = useState<Record<number, Message[]>>({});
    const [chatOverviewList, setChatOverviewList] = useState<ChatOverview[]>([]);
    const [chatInfo, setChatInfo] = useState<ChatInfo | null>(null);
    const [searchResults, setSearchResults] = useState<SearchUser[]>([]);
    const [newlyCreatedChatInfo, setNewlyCreatedChatInfo] = useState<ChatInfo | null>(null);
    const [contacts, setContacts] = useState<Contact[] | null>(null);
    const [notification, setNotification] = useState<string | null>(null);

    const connectSocket = useCallback(async () => {
        console.log('Attempting to connect WebSocket...');
        let token = localStorage.getItem('access_token');

        if (!token || isTokenExpired(token)) {
            console.log('Access token missing or expired, refreshing...');
            token = await refreshToken();
        }

        if (!token) {
            console.error('No valid access token, cannot connect WebSocket');
            return;
        }

        console.log('Connecting WebSocket with token:', token.slice(0, 10) + '...');
        const ws = new WebSocket(`${WS_URL}?access_token=${token}`);

        ws.onopen = () => console.log('WebSocket connected successfully');
        ws.onmessage = (event) => {
            console.log('Raw WebSocket message received:', event.data);
            try {
                const message: IncomingMessage = JSON.parse(event.data);
                console.log('Parsed message:', message);

                switch (message.event as ServerToClientEvent) {
                    case 'message_sent': {
                        console.log('Handling "message_sent" event');
                        const newMessage = message.data as Message;
                        const {chat_id} = newMessage;
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
                        console.log('Handling "chat_overview_list_sent" event');
                        setChatOverviewList(message.data as ChatOverview[]);
                        break;
                    }
                    case 'undelivered_messages_sent': {
                        console.log('Handling "undelivered_messages_sent" event');
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
                        console.log('Handling "chat_info_sent" event');
                        setChatInfo(message.data as ChatInfo);
                        break;
                    }
                    case 'chat_messages_sent': {
                        console.log('Handling "chat_messages_sent" event');
                        const messages = message.data as Message[]
                        if (messages && messages.length > 0) {
                            const chat_id = messages[0].chat_id

                            const validMessages = Array.isArray(messages) ? messages : [];
                            setMessagesByChat(prev => ({
                            ...prev,
                            [chat_id]: mergeAndSortMessages(prev[chat_id], validMessages)
                        }));
                        }
                        break;
                    }
                    case 'search_result_sent': {
                        console.log('Handling "search_result_sent" event')
                        const searchResult = message.data as { found_users: SearchUser[] };
                        setSearchResults(searchResult.found_users || []);
                        break;
                    }
                    case 'chat_created': {
                        console.log('Handling "chat_created" event')
                        setNewlyCreatedChatInfo(message.data as ChatInfo)
                        break;
                    }
                    case 'new_chat_sent': {
                        console.log('Handling "new_chat_sent" event')
                        const newChatOverview = message.data as ChatOverview
                        setChatOverviewList((prev) => [newChatOverview, ...prev])
                        break;
                    }
                    case 'added_to_contacts': {
                        console.log('Handling "added_to_contacts" event');
                        const newContact = message.data as Contact

                        setNotification(`${newContact.name} was added to your contacts`);
                        setTimeout(() => setNotification(null), 3000);

                        setContacts(prev => prev ? [...prev, newContact] : [newContact]);

                        setSearchResults(prev => prev.map(user =>
                            user.user_id === newContact.contact_id
                                ? { ...user, is_contact: true }
                                : user
                        ));
                        break;
                    }
                    case 'contacts_sent': {
                        console.log('Handling "contacts_sent" event');
                        setContacts(message.data as Contact[])
                        break;
                    }
                    default:
                        console.warn('Unhandled WebSocket event:', message.event);
                        break;
                }
            } catch (err) {
                console.error('Failed to parse WebSocket message', err);
            }
        };
        ws.onclose = (e) => console.warn('WebSocket disconnected:', e.reason);
        ws.onerror = (err) => console.error('WebSocket error:', err);

        setSocket(ws);
    }, []);

    useEffect(() => {
        connectSocket();
    }, [connectSocket]);

    const sendMessage = useCallback((payload: NewMessagePayload) => {
        if (payload.type === 'existing_chat') {
            console.log(`Sending message to chat ${payload.chatId}:`, payload.content);
        socket?.send(JSON.stringify({
            event: 'new_message',
            data: {chat_id: payload.chatId, content: payload.content},
        }));
        } else if (payload.type === 'new_chat') {
            console.log(
              `starting new private chat (sending FIRST message) with User 
            ${payload.targetUserId}, message content: "${payload.content}"`
            )
            socket?.send(JSON.stringify({
                event: 'start_new_chat',
                data: {
                    target_user_id: payload.targetUserId,
                    content: payload.content
                }
            }))
        }

    }, [socket]);

    const requestChatInfo = useCallback((chatId: number) => {
        console.log(`Requesting chat info for chat ${chatId}`);
        socket?.send(JSON.stringify({
            event: 'get_chat_info',
            data: {chat_id: chatId}
        }));
    }, [socket]);

    const requestChatMessages = useCallback((chatId: number) => {
        console.log(`Requesting messages for chat ${chatId}`);
        socket?.send(JSON.stringify({
            event: 'get_chat_messages',
            data: {chat_id: chatId}
        }));
    }, [socket]);

    const search = useCallback((prompt: string) => {
        socket?.send(JSON.stringify({
            event: 'search',
            data: {prompt: prompt}
        }));
    }, [socket]);

    const getContacts = useCallback(() => {
        socket?.send(JSON.stringify({
            event: 'get_contacts'
        }))
    }, [socket]);

    const addToContacts = useCallback((
      contact_id: number, name: string
    ) => {
        socket?.send(JSON.stringify({
            event: 'add_to_contacts',
            data: {contact_id: contact_id, name: name}
        }))
    }, [socket]);

    return {
        sendMessage,
        messagesByChat,
        chatOverviewList,
        chatInfo,
        requestChatInfo,
        requestChatMessages,
        search,
        searchResults,
        setSearchResults,
        newlyCreatedChatInfo,
        contacts,
        getContacts,
        addToContacts,
        notification
    };
};
