import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../lib/axios';

interface Message {
    id: string;
    vibe_id: string;
    user_id: string;
    username: string;
    content: string;
    created_at: string;
}

interface Vibe {
    id: string;
    name: string;
    description: string;
}

const VibeRoom = () => {
    const { vibeId } = useParams<{ vibeId: string }>();
    const navigate = useNavigate();
    const [vibe, setVibe] = useState<Vibe | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isJoined, setIsJoined] = useState(false);

    const ws = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initial load: Fetch Vibe Details & Message History
    useEffect(() => {
        const fetchState = async () => {
            try {
                // 1. Join immediately if not a member (or silently fail if already joined)
                try {
                    await api.post(`/vibes/${vibeId}/join`);
                } catch (e) {
                    // Usually 400 or ignoring if already joined based on our logic
                }
                setIsJoined(true);

                // 2. Fetch Vibe Details
                const vibeRes = await api.get(`/vibes/${vibeId}`);
                setVibe(vibeRes.data);

                // 3. (Optional but good) Fetch message history (We could use the history endpoint if we had built one for messages, 
                // but since the objective is pure realtime, let's just initialize blank or fetch if they want it. 
                // For MVP, just empty array is fine as they want to see live broadcast).

            } catch (err) {
                console.error("Failed to enter room:", err);
                navigate('/dashboard'); // Kick out if forbidden
            }
        };
        fetchState();
    }, [vibeId, navigate]);

    // WebSocket Connection Handling
    useEffect(() => {
        if (!isJoined || !vibeId) return;

        const token = localStorage.getItem('token');
        if (!token) return;

        // Note: Use standard WS protocol mapped to backend address
        const wsUrl = `ws://127.0.0.1:8008/ws/vibes/${vibeId}?token=${token}`;
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log("WebSocket connection established");
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setMessages((prev) => [...prev, data]);
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        socket.onclose = () => {
            console.log("WebSocket disconnected");
        };

        ws.current = socket;

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [isJoined, vibeId]);

    // Auto-scroll chat to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (ws.current && ws.current.readyState === WebSocket.OPEN && inputValue.trim()) {
            ws.current.send(inputValue.trim());
            setInputValue('');
        }
    };

    if (!vibe) return <div className="p-8 text-center text-gray-400">Loading Vibe Space...</div>;

    return (
        <div className="flex flex-col h-screen max-h-screen bg-gray-950 text-gray-100">
            {/* Header */}
            <header className="p-4 border-b border-gray-800 bg-gray-900 flex justify-between items-center shadow-md z-10 shrink-0">
                <div>
                    <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                        {vibe.name}
                    </h1>
                    <p className="text-sm text-gray-400">{vibe.description}</p>
                </div>
                <button
                    onClick={() => navigate('/dashboard')}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors duration-200"
                >
                    Back to Dashboard
                </button>
            </header>

            <div className="flex flex-1 overflow-hidden">
                {/* Left side: Vibe Posts */}
                <section className="w-2/3 border-r border-gray-800 flex flex-col bg-gray-950">
                    <div className="p-4 border-b border-gray-800 shrink-0">
                        <h2 className="text-lg font-bold text-gray-200 mb-3">Vibe Feed</h2>
                        <form onSubmit={async (e) => {
                            e.preventDefault();
                            const form = e.target as HTMLFormElement;
                            const input = form.elements.namedItem('postContent') as HTMLInputElement;
                            if(input.value.trim()){
                                try {
                                    await api.post(`/vibes/${vibeId}/posts`, { content: input.value });
                                    input.value = '';
                                    alert("Post created! (reload to see it for MVP)");
                                } catch(err){}
                            }
                        }} className="flex space-x-2">
                            <input 
                                name="postContent"
                                type="text"
                                placeholder="Share something with the vibe..."
                                className="flex-1 bg-gray-900 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
                            />
                            <button type="submit" className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium">Post</button>
                        </form>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        <p className="text-gray-500 text-sm text-center italic mt-10">Check your main dashboard Feed to see posts from this Vibe.</p>
                    </div>
                </section>

                {/* Right side: Chat Area */}
                <section className="w-1/3 flex flex-col bg-gray-900">
                    <div className="p-3 border-b border-gray-800 shrink-0 bg-gray-900 text-sm font-bold text-gray-300">
                        Live Chat
                    </div>
                    <main className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.length === 0 ? (
                            <div className="flex h-full items-center justify-center text-gray-500 italic text-sm">
                                No messages yet. Start the conversation!
                            </div>
                        ) : (
                            messages.map((msg, index) => (
                                <div key={msg.id || index} className="animate-fade-in-up">
                                    <div className="flex items-baseline space-x-2">
                                        <span className="font-bold text-xs text-blue-400">{msg.username}</span>
                                        <span className="text-[10px] text-gray-500">
                                            {new Date(msg.created_at).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <div className="mt-1 p-2 bg-gray-800/80 rounded-xl rounded-tl-sm w-fit max-w-[90%] break-words shadow-sm border border-gray-800 text-sm">
                                        {msg.content}
                                    </div>
                                </div>
                            ))
                        )}
                        <div ref={messagesEndRef} />
                    </main>

                    {/* Chat Input Area */}
                    <footer className="p-3 bg-gray-900 border-t border-gray-800 shrink-0">
                        <form onSubmit={handleSendMessage} className="flex space-x-2 relative w-full">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                placeholder="Chat..."
                                className="flex-1 bg-gray-950 border border-gray-800 rounded-full px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-all"
                            />
                            <button
                                type="submit"
                                disabled={!inputValue.trim()}
                                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 disabled:opacity-50 text-white rounded-full h-9 w-9 flex items-center justify-center transition-all"
                            >
                                <svg className="w-4 h-4 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
                            </button>
                        </form>
                    </footer>
                </section>
            </div>
        </div>
    );
};

export default VibeRoom;
