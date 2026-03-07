import React, { useState, useEffect, useRef } from 'react';
import api from '../lib/axios';

interface Comment {
    id: string;
    post_id: string;
    user_id: string;
    content: string;
    created_at: string;
}

interface PostProps {
    id: string;
    vibe_id: string;
    user_id: string;
    content: string;
    created_at: string;
    initialLikes?: number;
    initialCommentsCount?: number;
    user?: {
        username: string;
        influence_score: number;
        vibe_score?: number;
    };
    onDelete?: (id: string) => void;
}

const PostCard: React.FC<PostProps> = ({ id, vibe_id, user_id, content, created_at, initialLikes = 0, initialCommentsCount = 0, user, onDelete }) => {
    const [likes, setLikes] = useState(initialLikes); 
    const [commentsCount, setCommentsCount] = useState(initialCommentsCount);
    const [comments, setComments] = useState<Comment[]>([]);
    const [showComments, setShowComments] = useState(false);
    const [newComment, setNewComment] = useState('');
    const [viewLogged, setViewLogged] = useState(false);
    const postRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!postRef.current || viewLogged) return;
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                api.post(`/posts/${id}/view`).catch(() => {});
                setViewLogged(true);
                observer.disconnect();
            }
        }, { threshold: 0.5 });
        observer.observe(postRef.current);
        return () => observer.disconnect();
    }, [id, viewLogged]);

    const handleLike = async () => {
        try {
            await api.post(`/posts/${id}/like`);
            setLikes(l => l + 1);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchComments = async () => {
        try {
            const res = await api.get(`/posts/${id}/comments`);
            setComments(res.data);
            setShowComments(true);
        } catch (err) {
            console.error(err);
        }
    };

    const submitComment = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await api.post(`/posts/${id}/comments`, { content: newComment });
            setComments([...comments, res.data]);
            setCommentsCount(c => c + 1);
            setNewComment('');
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div ref={postRef} className="bg-gray-900 border border-gray-800 rounded-xl p-5 shadow-sm text-gray-200 mb-4 animate-fade-in-up">
            <div className="flex justify-between items-start mb-2">
                <div className="flex items-center">
                    {user ? (
                        <div className="flex items-center gap-2">
                            <span 
                                className="text-xs font-semibold bg-gray-800 text-purple-400 px-2 py-0.5 rounded cursor-help"
                                title="Global Influence Level"
                            >
                                @{user.username} 🔥 Lv.{Math.floor(Math.sqrt(user.influence_score / 10))}
                            </span>
                            {user.vibe_score !== undefined && (
                                <span 
                                    className="text-xs font-medium text-blue-400/80 cursor-help"
                                    title="Level within this Vibe"
                                >
                                    Lv.{Math.floor(Math.sqrt(user.vibe_score / 10))} in Vibe
                                </span>
                            )}
                        </div>
                    ) : (
                        <span className="font-semibold text-blue-400 text-sm">
                            User {user_id.slice(0, 6)}
                        </span>
                    )}
                    {vibe_id && <span className="ml-2 text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">Vibe {vibe_id.slice(0,6)}</span>}
                </div>
                <span className="text-xs text-gray-500">{new Date(created_at).toLocaleDateString()}</span>
            </div>
            
            <p className="text-gray-300 mt-2 mb-4 whitespace-pre-wrap">{content}</p>
            
            <div className="flex justify-between items-center border-t border-gray-800 pt-3">
                <div className="flex space-x-4">
                    <button onClick={handleLike} className="flex items-center text-gray-400 hover:text-pink-500 transition-colors text-sm">
                        <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
                        Like ({likes})
                    </button>
                    <button 
                        onClick={() => showComments ? setShowComments(false) : fetchComments()} 
                        className="flex items-center text-gray-400 hover:text-blue-400 transition-colors text-sm"
                    >
                        <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                        Comments {commentsCount > 0 && `(${commentsCount})`}
                    </button>
                </div>
                {onDelete && (
                    <button 
                        onClick={() => onDelete(id)} 
                        className="text-gray-500 hover:text-red-500 transition-colors text-sm"
                        title="Delete Post"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                )}
            </div>

            {showComments && (
                <div className="mt-4 pt-4 border-t border-gray-800 space-y-3">
                    {comments.map(c => (
                        <div key={c.id} className="bg-gray-800/50 p-3 rounded-lg text-sm">
                            <span className="font-bold text-gray-400">User {c.user_id.slice(0,4)}</span>: <span className="text-gray-300">{c.content}</span>
                        </div>
                    ))}
                    
                    <form onSubmit={submitComment} className="mt-3 flex gap-2">
                        <input 
                            type="text" 
                            className="flex-1 bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                            placeholder="Write a comment..."
                            value={newComment}
                            onChange={(e) => setNewComment(e.target.value)}
                        />
                        <button disabled={!newComment} type="submit" className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">Post</button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default PostCard;
