import { useState, useEffect } from 'react';
import api from '../../lib/axios';
import PostCard from '../../components/PostCard';

interface Post {
    id: string;
    vibe_id: string;
    user_id: string;
    content: string;
    created_at: string;
    likes_count: number;
    comments_count: number;
    user?: {
        username: string;
        influence_score: number;
    };
}

const Feed = () => {
    const [posts, setPosts] = useState<Post[]>([]);
    const [cursor, setCursor] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const fetchFeed = async (nextCursor?: string | null) => {
        setLoading(true);
        try {
            const url = nextCursor ? `/feed/?cursor=${encodeURIComponent(nextCursor)}` : '/feed/';
            const res = await api.get(url);
            if (nextCursor) {
                setPosts(prev => [...prev, ...res.data.items]);
            } else {
                setPosts(res.data.items);
            }
            setCursor(res.data.next_cursor);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFeed();
    }, []);

    return (
        <section className="col-span-1 md:col-span-2 space-y-4">
            <h2 className="text-lg font-semibold mb-4 text-gray-200">Your Feed</h2>
            {posts.length === 0 && !loading ? (
                <div className="p-8 border border-dashed border-blue-500/30 rounded-xl bg-blue-900/10 text-center animate-pulse">
                    <h3 className="text-xl font-bold text-blue-400 mb-2">Welcome to Vibe Platform! 👋</h3>
                    <p className="text-gray-300 mb-6">You're currently not seeing any posts.</p>
                    
                    <div className="flex flex-col gap-4 max-w-sm mx-auto text-left">
                        <div className="bg-gray-900/80 p-4 rounded-lg border border-gray-800 flex items-start">
                            <span className="text-2xl mr-3">1️⃣</span>
                            <div>
                                <h4 className="font-semibold text-gray-200">Join a Vibe</h4>
                                <p className="text-xs text-gray-500">Pick an active vibe on the left to start seeing content.</p>
                            </div>
                        </div>
                        <div className="bg-gray-900/80 p-4 rounded-lg border border-gray-800 flex items-start">
                            <span className="text-2xl mr-3">2️⃣</span>
                            <div>
                                <h4 className="font-semibold text-gray-200">Create a Post</h4>
                                <p className="text-xs text-gray-500">Share your thoughts to earn <span className="text-orange-400 font-bold">XP</span>.</p>
                            </div>
                        </div>
                        <div className="bg-gray-900/80 p-4 rounded-lg border border-gray-800 flex items-start">
                            <span className="text-2xl mr-3">3️⃣</span>
                            <div>
                                <h4 className="font-semibold text-gray-200">Level Up!</h4>
                                <p className="text-xs text-gray-500">Gain levels automatically as you interact and post.</p>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="space-y-4">
                    {posts.map(post => (
                        <PostCard 
                            key={post.id} 
                            id={post.id}
                            vibe_id={post.vibe_id}
                            user_id={post.user_id}
                            content={post.content}
                            created_at={post.created_at}
                            initialLikes={post.likes_count}
                            initialCommentsCount={post.comments_count}
                            user={post.user}
                        />
                    ))}
                </div>
            )}
            
            {cursor && (
                <button 
                    onClick={() => fetchFeed(cursor)} 
                    disabled={loading}
                    className="w-full bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-white font-medium rounded-lg py-2 transition-colors border border-gray-700"
                >
                    {loading ? 'Loading...' : 'Load More'}
                </button>
            )}
        </section>
    );
};

export default Feed;
