import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../lib/axios';
import Navbar from '../../components/Navbar';
import Feed from './Feed';

interface Vibe {
    id: string;
    name: string;
    description: string;
    member_count?: number;
    online_count?: number;
}

const Dashboard = () => {
    const navigate = useNavigate();
    const [trendingVibes, setTrendingVibes] = useState<Vibe[]>([]);
    const [newVibes, setNewVibes] = useState<Vibe[]>([]);
    const [newVibeName, setNewVibeName] = useState('');
    const [newVibeDesc, setNewVibeDesc] = useState('');
    const [userData, setUserData] = useState<{influence_score: number} | null>(null);

    useEffect(() => {
        const fetchVibes = async () => {
            try {
                const [resTrending, resNew] = await Promise.all([
                    api.get('/vibes/trending'),
                    api.get('/vibes/new')
                ]);
                setTrendingVibes(resTrending.data);
                setNewVibes(resNew.data);
            } catch (err) {
                console.error("Could not fetch vibes:", err);
            }
        };
        const fetchUserData = async () => {
            try {
                const res = await api.get('/auth/me');
                setUserData(res.data);
            } catch(err) {
                console.error("Failed to fetch user data:", err);
            }
        };
        fetchVibes();
        fetchUserData();
    }, []);

    const handleCreateVibe = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await api.post('/vibes/', { name: newVibeName, description: newVibeDesc });
            setNewVibes(prev => [res.data, ...prev]);
            setNewVibeName('');
            setNewVibeDesc('');
        } catch (err) {
            console.error("Error creating vibe:", err);
        }
    };

    const joinVibe = async (vibeId: string) => {
        try {
            await api.post(`/vibes/${vibeId}/join`);
            // Optimistically update or re-fetch
            const res = await api.get('/vibes/trending');
            setTrendingVibes(res.data);
            navigate(`/vibes/${vibeId}`);
        } catch (err) {
            console.error("Error joining vibe:", err);
            // Even if we fail (e.g. already joined), try to navigate
            navigate(`/vibes/${vibeId}`);
        }
    };

    const copyInvite = () => {
        navigator.clipboard.writeText(window.location.origin + "/join");
        alert("Invite link copied!");
    };

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
            <Navbar />
            <div className="flex-1 p-8 max-w-7xl mx-auto w-full">

            <main className="grid md:grid-cols-3 gap-8">
                <div className="space-y-6">
                {/* Discover Vibes */}
                <section className="col-span-1 space-y-6">
                    {/* Trending Vibes */}
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl h-fit">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-200">🔥 Vibing Now</h2>
                        </div>
                        {trendingVibes.length === 0 ? (
                            <p className="text-gray-400">No vibes available.</p>
                        ) : (
                            <ul className="space-y-3">
                                {trendingVibes.map((v: Vibe) => (
                                    <li key={v.id} className="flex flex-col p-3 bg-gray-950 border border-gray-800 rounded-lg hover:border-blue-500/50 transition-colors group cursor-pointer" onClick={() => joinVibe(v.id)}>
                                        <div className="flex items-center justify-between">
                                            <span className="font-medium text-gray-200 group-hover:text-blue-400">{v.name}</span>
                                            <button 
                                                className="text-sm bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white px-3 py-1 rounded-md transition-colors"
                                            >
                                                Join
                                            </button>
                                        </div>
                                        {/* Presence Indicator */}
                                        <div className="mt-2 flex items-center gap-1 text-xs text-green-400 font-medium tracking-wide">
                                            <span className="relative flex h-2 w-2 mr-1">
                                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                                            </span>
                                            {v.online_count || Math.floor(Math.random() * 8) + 1} vibing right now
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    {/* New Vibes */}
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl h-fit">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-200">New Vibes</h2>
                        </div>
                        {newVibes.length === 0 ? (
                            <p className="text-gray-400">No new vibes.</p>
                        ) : (
                            <ul className="space-y-3">
                                {newVibes.slice(0, 3).map((v: Vibe) => (
                                    <li key={v.id} className="flex justify-between items-center p-3 bg-gray-950 border border-gray-800 rounded-lg">
                                        <span className="font-medium text-gray-200">{v.name}</span>
                                        <button 
                                            onClick={() => joinVibe(v.id)}
                                            className="text-sm border border-gray-700 hover:border-blue-400 hover:text-blue-400 text-gray-400 px-3 py-1 rounded-md transition-colors"
                                        >
                                            Join
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </section>
                {/* Create Space */}
                <section className="col-span-1 bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl h-fit">
                    <h2 className="text-lg font-semibold mb-4 text-gray-200">Start a new Vibe</h2>
                    <form onSubmit={handleCreateVibe} className="space-y-4">
                        <div>
                            <input
                                type="text"
                                placeholder="Vibe Name"
                                value={newVibeName}
                                onChange={(e) => setNewVibeName(e.target.value)}
                                className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2 text-gray-300 focus:outline-none focus:border-blue-500 transition-colors"
                                required
                            />
                        </div>
                        <div>
                            <input
                                type="text"
                                placeholder="Short Description..."
                                value={newVibeDesc}
                                onChange={(e) => setNewVibeDesc(e.target.value)}
                                className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2 text-gray-300 focus:outline-none focus:border-blue-500 transition-colors"
                            />
                        </div>
                        {/* Vibe Creation Unlock - Assume user needs at least 90 XP (Level 3) */}
                        {userData && Math.floor(Math.sqrt(userData.influence_score / 10)) >= 3 ? (
                            <button
                                type="submit"
                                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium rounded-lg py-2 transition-all shadow-md"
                            >
                                Create Vibe
                            </button>
                        ) : (
                            <button
                                type="button"
                                disabled
                                className="w-full bg-gray-800 text-gray-500 cursor-not-allowed font-medium rounded-lg py-2 transition-all shadow-sm"
                                title="Reach Level 3 to unlock Vibe creation!"
                            >
                                🔒 Unlocks at Level 3
                            </button>
                        )}
                    </form>

                    <div className="mt-8 pt-6 border-t border-gray-800">
                        <h3 className="text-md font-semibold text-gray-200 mb-3">Strengthen the Loop</h3>
                        <p className="text-xs text-gray-400 mb-4">Communities grow when members bring others in.</p>
                        <button
                            onClick={copyInvite}
                            className="w-full flex items-center justify-center gap-2 border border-blue-500/30 text-blue-400 hover:bg-blue-500/10 font-medium rounded-lg py-2 transition-colors shadow-sm"
                        >
                            <span>📥</span> Invite Friends
                        </button>
                    </div>
                </section>
                
                </div>


                {/* Feed Area */}
                <Feed />
            </main>
            </div>
        </div>
    );
};

export default Dashboard;
