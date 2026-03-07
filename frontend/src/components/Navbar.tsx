import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/axios';

interface Notification {
    id: string;
    user_id: string;
    type: string;
    reference_id: string;
    is_read: boolean;
    created_at: string;
}

interface UserData {
    id: string;
    username: string;
    influence_score: number;
}

interface SearchResult {
    id: string;
    name?: string;
    username?: string;
    content?: string;
}

const Navbar = () => {
    const navigate = useNavigate();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [showNotifs, setShowNotifs] = useState(false);
    const [userData, setUserData] = useState<UserData | null>(null);
    
    // Search states
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<{users: SearchResult[], vibes: SearchResult[], posts: SearchResult[]}>({ users: [], vibes: [], posts: [] });
    const [showSearch, setShowSearch] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetchNotifications();
        fetchUserData();
    }, []);

    const fetchUserData = async () => {
        try {
            const res = await api.get('/auth/me');
            setUserData(res.data);
        } catch(err) {
            console.error("Failed to fetch user data:", err);
        }
    };

    const fetchNotifications = async () => {
        try {
            const res = await api.get('/notifications/');
            setNotifications(res.data);
        } catch (err) {
            console.error("Failed to fetch notifications:", err);
        }
    };

    const markAsRead = async (id: string) => {
        try {
            await api.patch(`/notifications/${id}/read`);
            setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
        } catch (err) {
            console.error("Failed to mark notification as read:", err);
        }
    };

    const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const q = e.target.value;
        setSearchQuery(q);
        if (q.length < 2) {
            setShowSearch(false);
            return;
        }

        try {
            const [usersRes, vibesRes, postsRes] = await Promise.all([
                api.get(`/search/users?q=${q}`),
                api.get(`/search/vibes?q=${q}`),
                api.get(`/search/posts?q=${q}`)
            ]);
            setSearchResults({
                users: usersRes.data,
                vibes: vibesRes.data,
                posts: postsRes.data
            });
            setShowSearch(true);
        } catch (err) {
            console.error("Search failed", err);
        }
    };

    const handleFollow = async (userId: string) => {
        try {
            await api.post(`/users/${userId}/follow`);
            alert("Followed successfully!");
        } catch (err) {
            console.error("Failed to follow", err);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const unreadCount = notifications.filter(n => !n.is_read).length;

    return (
        <header className="sticky top-0 z-50 bg-gray-900 border-b border-gray-800 px-6 py-4 flex justify-between items-center shadow-lg">
            <h1 
                className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500 cursor-pointer"
                onClick={() => navigate('/dashboard')}
            >
                Vibe Platform
            </h1>
            
            <div className="flex items-center space-x-6">
                
                {/* User Level Display */}
                {userData && (
                    <div className="hidden md:flex items-center space-x-2 bg-gray-800/80 px-4 py-1.5 rounded-full border border-gray-700 shadow-sm transition-transform hover:scale-105 cursor-default">
                        <span className="text-sm font-semibold text-gray-200">@{userData.username}</span>
                        <span className="w-1 h-3 bg-gray-600 rounded-full"></span>
                        <div 
                            className="flex items-center justify-center bg-gradient-to-r from-yellow-400 to-orange-500 text-yellow-950 text-xs font-bold px-2 py-0.5 rounded-full shadow-[0_0_8px_rgba(250,204,21,0.4)]"
                            title={`Influence XP: ${userData.influence_score}`}
                        >
                            ★ LVL {Math.floor(Math.sqrt(userData.influence_score / 10))}
                        </div>
                    </div>
                )}
                
                {/* Search Menu */}
                <div className="relative" ref={searchRef}>
                    <input 
                        type="text"
                        placeholder="Search users, vibes..."
                        className="bg-gray-950 border border-gray-800 rounded-full px-5 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500 transition-colors w-64"
                        value={searchQuery}
                        onChange={handleSearch}
                        onFocus={() => { if (searchQuery.length >= 2) setShowSearch(true); }}
                    />
                    
                    {showSearch && (
                        <div className="absolute top-full mt-2 right-0 w-80 bg-gray-900 border border-gray-800 rounded-lg shadow-2xl p-4 overflow-y-auto max-h-96">
                            {(searchResults.users.length === 0 && searchResults.vibes.length === 0 && searchResults.posts.length === 0) ? (
                                <p className="text-gray-500 text-sm text-center">No results found.</p>
                            ) : (
                                <>
                                    {searchResults.users.length > 0 && (
                                        <div className="mb-4">
                                            <h3 className="text-xs font-bold text-gray-500 uppercase mb-2">Users</h3>
                                            {searchResults.users.map(u => (
                                                <div key={u.id} className="flex justify-between items-center mb-2 bg-gray-800/50 p-2 rounded-md">
                                                    <span className="text-sm text-gray-200">@{u.username}</span>
                                                    <button onClick={() => handleFollow(u.id)} className="text-xs bg-blue-600 hover:bg-blue-500 px-2 py-1 rounded">Follow</button>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                    
                                    {searchResults.vibes.length > 0 && (
                                        <div className="mb-4">
                                            <h3 className="text-xs font-bold text-gray-500 uppercase mb-2">Vibes</h3>
                                            {searchResults.vibes.map(v => (
                                                <div key={v.id} className="flex justify-between items-center mb-2 bg-gray-800/50 p-2 rounded-md cursor-pointer hover:bg-gray-800" onClick={() => { setShowSearch(false); navigate(`/vibes/${v.id}`); }}>
                                                    <span className="text-sm font-semibold text-blue-400">{v.name}</span>
                                                    <span className="text-xs text-gray-400">Join</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {searchResults.posts.length > 0 && (
                                        <div className="mb-2">
                                            <h3 className="text-xs font-bold text-gray-500 uppercase mb-2">Posts</h3>
                                            {searchResults.posts.map(p => (
                                                <div key={p.id} className="text-sm text-gray-300 bg-gray-800/50 p-2 rounded-md mb-2 line-clamp-2">
                                                    {p.content}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    )}
                </div>

                {/* Notifications Dropdown */}
                <div className="relative">
                    <button 
                        className="relative p-2 text-gray-400 hover:text-white transition-colors"
                        onClick={() => setShowNotifs(!showNotifs)}
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
                        {unreadCount > 0 && (
                            <span className="absolute top-1 right-1 flex items-center justify-center p-1 bg-red-500 text-white text-[10px] font-bold rounded-full w-4 h-4">
                                {unreadCount}
                            </span>
                        )}
                    </button>
                    
                    {showNotifs && (
                        <div className="absolute top-full mt-2 right-0 w-80 bg-gray-900 border border-gray-800 rounded-lg shadow-2xl p-4 max-h-96 overflow-y-auto">
                            <h3 className="text-sm font-bold text-gray-200 mb-3 border-b border-gray-800 pb-2">Notifications</h3>
                            {notifications.length === 0 ? (
                                <p className="text-gray-500 text-sm text-center">No new notifications</p>
                            ) : (
                                notifications.map(n => (
                                    <div 
                                        key={n.id} 
                                        className={`p-3 mb-2 rounded-lg text-sm transition-colors ${n.is_read ? 'bg-gray-800/40 text-gray-400' : 'bg-gray-800/80 text-gray-100 border border-blue-500/20'}`}
                                        onClick={() => !n.is_read && markAsRead(n.id)}
                                    >
                                        <p>
                                            <span className="font-semibold text-blue-400">[{n.type.toUpperCase()}]</span> Someone interacted with you.
                                        </p>
                                        <span className="text-xs text-gray-500 mt-1 block">{new Date(n.created_at).toLocaleString()}</span>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>

                <button
                    onClick={handleLogout}
                    className="text-gray-400 hover:text-white hover:underline transition-colors text-sm font-medium"
                >
                    Logout
                </button>
            </div>
        </header>
    );
};

export default Navbar;
