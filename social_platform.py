# social_platform.py - Social features and community system
import sqlite3
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
from pathlib import Path

class SocialPlatform:
    """
    Social platform features for Swing Sage:
    - User profiles and achievements
    - Following/followers system
    - Swing sharing and privacy controls
    - Leaderboards and competitions
    - Comments and reactions
    - Challenge system
    - Group coaching sessions
    """
    
    def __init__(self, db_path: str = "social_platform.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize social platform database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced users table with social features
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT,
                email TEXT UNIQUE,
                bio TEXT,
                avatar_url TEXT,
                location TEXT,
                handicap INTEGER,
                privacy_level TEXT DEFAULT 'public',
                join_date TEXT,
                last_active TEXT,
                total_swings INTEGER DEFAULT 0,
                best_score REAL DEFAULT 0,
                achievement_points INTEGER DEFAULT 0,
                verified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Follow relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follows (
                follower_id TEXT,
                following_id TEXT,
                follow_date TEXT,
                PRIMARY KEY (follower_id, following_id),
                FOREIGN KEY (follower_id) REFERENCES social_users (user_id),
                FOREIGN KEY (following_id) REFERENCES social_users (user_id)
            )
        ''')
        
        # Shared swings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_swings (
                share_id TEXT PRIMARY KEY,
                user_id TEXT,
                analysis_id TEXT,
                title TEXT,
                description TEXT,
                video_url TEXT,
                thumbnail_url TEXT,
                privacy_level TEXT DEFAULT 'public',
                allow_comments BOOLEAN DEFAULT TRUE,
                share_date TEXT,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                tags TEXT,
                FOREIGN KEY (user_id) REFERENCES social_users (user_id)
            )
        ''')
        
        # Reactions (likes, loves, etc.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reactions (
                reaction_id TEXT PRIMARY KEY,
                user_id TEXT,
                target_type TEXT,
                target_id TEXT,
                reaction_type TEXT,
                reaction_date TEXT,
                FOREIGN KEY (user_id) REFERENCES social_users (user_id)
            )
        ''')
        
        # Comments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                comment_id TEXT PRIMARY KEY,
                user_id TEXT,
                target_type TEXT,
                target_id TEXT,
                parent_comment_id TEXT,
                content TEXT,
                comment_date TEXT,
                like_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES social_users (user_id),
                FOREIGN KEY (parent_comment_id) REFERENCES comments (comment_id)
            )
        ''')
        
        # Achievements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id TEXT PRIMARY KEY,
                user_id TEXT,
                achievement_type TEXT,
                achievement_name TEXT,
                description TEXT,
                icon_url TEXT,
                achievement_date TEXT,
                points INTEGER DEFAULT 0,
                rarity TEXT DEFAULT 'common',
                FOREIGN KEY (user_id) REFERENCES social_users (user_id)
            )
        ''')
        
        # Challenges
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                challenge_id TEXT PRIMARY KEY,
                creator_id TEXT,
                title TEXT,
                description TEXT,
                challenge_type TEXT,
                target_metric TEXT,
                target_value REAL,
                start_date TEXT,
                end_date TEXT,
                entry_fee INTEGER DEFAULT 0,
                prize_pool INTEGER DEFAULT 0,
                max_participants INTEGER,
                current_participants INTEGER DEFAULT 0,
                status TEXT DEFAULT 'open',
                FOREIGN KEY (creator_id) REFERENCES social_users (user_id)
            )
        ''')
        
        # Challenge participants
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenge_participants (
                participation_id TEXT PRIMARY KEY,
                challenge_id TEXT,
                user_id TEXT,
                join_date TEXT,
                best_score REAL,
                submission_count INTEGER DEFAULT 0,
                final_rank INTEGER,
                FOREIGN KEY (challenge_id) REFERENCES challenges (challenge_id),
                FOREIGN KEY (user_id) REFERENCES social_users (user_id)
            )
        ''')
        
        # Groups/Communities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT PRIMARY KEY,
                creator_id TEXT,
                name TEXT,
                description TEXT,
                avatar_url TEXT,
                group_type TEXT DEFAULT 'public',
                member_count INTEGER DEFAULT 0,
                creation_date TEXT,
                tags TEXT,
                FOREIGN KEY (creator_id) REFERENCES social_users (user_id)
            )
        ''')
        
        # Group memberships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                membership_id TEXT PRIMARY KEY,
                group_id TEXT,
                user_id TEXT,
                role TEXT DEFAULT 'member',
                join_date TEXT,
                FOREIGN KEY (group_id) REFERENCES groups (group_id),
                FOREIGN KEY (user_id) REFERENCES social_users (user_id)
            )
        ''')
        
        # Feed/Activity timeline
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_feed (
                activity_id TEXT PRIMARY KEY,
                user_id TEXT,
                activity_type TEXT,
                target_type TEXT,
                target_id TEXT,
                activity_data TEXT,
                activity_date TEXT,
                visibility TEXT DEFAULT 'public',
                FOREIGN KEY (user_id) REFERENCES social_users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_social_profile(self, user_id: str, username: str, display_name: str, 
                            email: str, bio: str = "", location: str = "") -> Dict:
        """Create or update social profile"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO social_users 
                (user_id, username, display_name, email, bio, location, join_date, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, display_name, email, bio, location, 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            
            # Create welcome achievement
            self._grant_achievement(user_id, 'welcome', 'Welcome to Swing Sage!', 
                                  'Joined the community', 50)
            
            return {'success': True, 'user_id': user_id}
            
        except sqlite3.IntegrityError as e:
            return {'success': False, 'error': 'Username or email already taken'}
        finally:
            conn.close()
    
    def follow_user(self, follower_id: str, following_id: str) -> Dict:
        """Follow another user"""
        
        if follower_id == following_id:
            return {'success': False, 'error': 'Cannot follow yourself'}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO follows (follower_id, following_id, follow_date)
                VALUES (?, ?, ?)
            ''', (follower_id, following_id, datetime.now().isoformat()))
            
            conn.commit()
            
            # Add to activity feed
            self._add_activity(follower_id, 'follow', 'user', following_id, 
                             {'action': 'followed'})
            
            return {'success': True}
            
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Already following this user'}
        finally:
            conn.close()
    
    def unfollow_user(self, follower_id: str, following_id: str) -> Dict:
        """Unfollow a user"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM follows 
            WHERE follower_id = ? AND following_id = ?
        ''', (follower_id, following_id))
        
        conn.commit()
        conn.close()
        
        return {'success': cursor.rowcount > 0}
    
    def share_swing(self, user_id: str, analysis_id: str, title: str, 
                   description: str, video_url: str, privacy_level: str = 'public',
                   tags: List[str] = None) -> Dict:
        """Share a swing analysis with the community"""
        
        share_id = str(uuid.uuid4())
        tags_json = json.dumps(tags or [])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shared_swings 
            (share_id, user_id, analysis_id, title, description, video_url, 
             privacy_level, share_date, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (share_id, user_id, analysis_id, title, description, video_url,
              privacy_level, datetime.now().isoformat(), tags_json))
        
        conn.commit()
        conn.close()
        
        # Add to activity feed
        self._add_activity(user_id, 'share_swing', 'shared_swing', share_id,
                         {'title': title, 'privacy': privacy_level})
        
        # Grant sharing achievement if first time
        self._check_sharing_achievements(user_id)
        
        return {'success': True, 'share_id': share_id}
    
    def get_user_feed(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get personalized activity feed for user"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get activities from followed users and own activities
        cursor.execute('''
            SELECT af.*, su.username, su.display_name, su.avatar_url
            FROM activity_feed af
            JOIN social_users su ON af.user_id = su.user_id
            WHERE af.user_id IN (
                SELECT following_id FROM follows WHERE follower_id = ?
                UNION
                SELECT ?
            )
            AND af.visibility = 'public'
            ORDER BY af.activity_date DESC
            LIMIT ? OFFSET ?
        ''', (user_id, user_id, limit, offset))
        
        activities = cursor.fetchall()
        conn.close()
        
        # Format activities for display
        formatted_activities = []
        for activity in activities:
            formatted_activity = {
                'activity_id': activity[0],
                'user_id': activity[1],
                'username': activity[8],
                'display_name': activity[9],
                'avatar_url': activity[10],
                'activity_type': activity[2],
                'target_type': activity[3],
                'target_id': activity[4],
                'activity_data': json.loads(activity[5]) if activity[5] else {},
                'activity_date': activity[6],
                'visibility': activity[7]
            }
            formatted_activities.append(formatted_activity)
        
        return formatted_activities
    
    def get_trending_swings(self, limit: int = 10, time_period: str = '24h') -> List[Dict]:
        """Get trending swing shares based on engagement"""
        
        # Calculate time cutoff
        if time_period == '24h':
            cutoff = datetime.now() - timedelta(days=1)
        elif time_period == '7d':
            cutoff = datetime.now() - timedelta(days=7)
        else:  # 30d
            cutoff = datetime.now() - timedelta(days=30)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ss.*, su.username, su.display_name, su.avatar_url,
                   (ss.like_count + ss.comment_count * 2 + ss.view_count * 0.1) as engagement_score
            FROM shared_swings ss
            JOIN social_users su ON ss.user_id = su.user_id
            WHERE ss.privacy_level = 'public' 
            AND ss.share_date >= ?
            ORDER BY engagement_score DESC
            LIMIT ?
        ''', (cutoff.isoformat(), limit))
        
        trending = cursor.fetchall()
        conn.close()
        
        return [self._format_shared_swing(swing) for swing in trending]
    
    def create_challenge(self, creator_id: str, title: str, description: str,
                        challenge_type: str, target_metric: str, target_value: float,
                        duration_days: int = 7, entry_fee: int = 0) -> Dict:
        """Create a new community challenge"""
        
        challenge_id = str(uuid.uuid4())
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO challenges 
            (challenge_id, creator_id, title, description, challenge_type,
             target_metric, target_value, start_date, end_date, entry_fee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (challenge_id, creator_id, title, description, challenge_type,
              target_metric, target_value, start_date.isoformat(),
              end_date.isoformat(), entry_fee))
        
        conn.commit()
        conn.close()
        
        # Add to activity feed
        self._add_activity(creator_id, 'create_challenge', 'challenge', challenge_id,
                         {'title': title, 'type': challenge_type})
        
        return {'success': True, 'challenge_id': challenge_id}
    
    def join_challenge(self, user_id: str, challenge_id: str) -> Dict:
        """Join a community challenge"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if challenge exists and is open
        cursor.execute('''
            SELECT status, max_participants, current_participants
            FROM challenges WHERE challenge_id = ?
        ''', (challenge_id,))
        
        challenge = cursor.fetchone()
        if not challenge:
            conn.close()
            return {'success': False, 'error': 'Challenge not found'}
        
        if challenge[0] != 'open':
            conn.close()
            return {'success': False, 'error': 'Challenge is not open'}
        
        if challenge[1] and challenge[2] >= challenge[1]:
            conn.close()
            return {'success': False, 'error': 'Challenge is full'}
        
        try:
            # Add participant
            participation_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO challenge_participants 
                (participation_id, challenge_id, user_id, join_date)
                VALUES (?, ?, ?, ?)
            ''', (participation_id, challenge_id, user_id, datetime.now().isoformat()))
            
            # Update participant count
            cursor.execute('''
                UPDATE challenges 
                SET current_participants = current_participants + 1
                WHERE challenge_id = ?
            ''', (challenge_id,))
            
            conn.commit()
            
            # Add to activity feed
            self._add_activity(user_id, 'join_challenge', 'challenge', challenge_id,
                             {'action': 'joined'})
            
            return {'success': True, 'participation_id': participation_id}
            
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Already joined this challenge'}
        finally:
            conn.close()
    
    def get_leaderboard(self, leaderboard_type: str = 'overall', 
                       time_period: str = 'all_time', limit: int = 50) -> List[Dict]:
        """Get community leaderboards"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if leaderboard_type == 'overall':
            # Overall achievement points
            cursor.execute('''
                SELECT su.user_id, su.username, su.display_name, su.avatar_url,
                       su.achievement_points, su.total_swings, su.best_score
                FROM social_users su
                WHERE su.privacy_level IN ('public', 'friends')
                ORDER BY su.achievement_points DESC
                LIMIT ?
            ''', (limit,))
            
        elif leaderboard_type == 'improvement':
            # Most improved players (based on recent vs historical scores)
            cursor.execute('''
                SELECT su.user_id, su.username, su.display_name, su.avatar_url,
                       su.achievement_points, su.total_swings, su.best_score
                FROM social_users su
                WHERE su.privacy_level IN ('public', 'friends')
                AND su.total_swings >= 5
                ORDER BY su.best_score DESC
                LIMIT ?
            ''', (limit,))
            
        elif leaderboard_type == 'activity':
            # Most active players
            cursor.execute('''
                SELECT su.user_id, su.username, su.display_name, su.avatar_url,
                       su.achievement_points, su.total_swings, su.best_score
                FROM social_users su
                WHERE su.privacy_level IN ('public', 'friends')
                ORDER BY su.total_swings DESC
                LIMIT ?
            ''', (limit,))
        
        leaderboard = cursor.fetchall()
        conn.close()
        
        # Format leaderboard
        formatted_leaderboard = []
        for i, entry in enumerate(leaderboard):
            formatted_entry = {
                'rank': i + 1,
                'user_id': entry[0],
                'username': entry[1],
                'display_name': entry[2],
                'avatar_url': entry[3],
                'achievement_points': entry[4],
                'total_swings': entry[5],
                'best_score': entry[6]
            }
            formatted_leaderboard.append(formatted_entry)
        
        return formatted_leaderboard
    
    def add_reaction(self, user_id: str, target_type: str, target_id: str, 
                    reaction_type: str = 'like') -> Dict:
        """Add reaction to swing, comment, etc."""
        
        reaction_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO reactions 
                (reaction_id, user_id, target_type, target_id, reaction_type, reaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (reaction_id, user_id, target_type, target_id, reaction_type,
                  datetime.now().isoformat()))
            
            # Update like count on target
            if target_type == 'shared_swing':
                cursor.execute('''
                    UPDATE shared_swings 
                    SET like_count = like_count + 1 
                    WHERE share_id = ?
                ''', (target_id,))
            
            conn.commit()
            return {'success': True, 'reaction_id': reaction_id}
            
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Already reacted'}
        finally:
            conn.close()
    
    def add_comment(self, user_id: str, target_type: str, target_id: str,
                   content: str, parent_comment_id: str = None) -> Dict:
        """Add comment to swing or reply to comment"""
        
        comment_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comments 
            (comment_id, user_id, target_type, target_id, parent_comment_id, 
             content, comment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (comment_id, user_id, target_type, target_id, parent_comment_id,
              content, datetime.now().isoformat()))
        
        # Update comment count on target
        if target_type == 'shared_swing':
            cursor.execute('''
                UPDATE shared_swings 
                SET comment_count = comment_count + 1 
                WHERE share_id = ?
            ''', (target_id,))
        
        conn.commit()
        conn.close()
        
        # Add to activity feed
        self._add_activity(user_id, 'comment', target_type, target_id,
                         {'content': content[:100]})  # Truncate for feed
        
        return {'success': True, 'comment_id': comment_id}
    
    def _grant_achievement(self, user_id: str, achievement_type: str, 
                          name: str, description: str, points: int):
        """Grant achievement to user"""
        
        achievement_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO achievements 
                (achievement_id, user_id, achievement_type, achievement_name,
                 description, achievement_date, points)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (achievement_id, user_id, achievement_type, name, description,
                  datetime.now().isoformat(), points))
            
            # Update user's achievement points
            cursor.execute('''
                UPDATE social_users 
                SET achievement_points = achievement_points + ?
                WHERE user_id = ?
            ''', (points, user_id))
            
            conn.commit()
            
            # Add to activity feed
            self._add_activity(user_id, 'achievement', 'achievement', achievement_id,
                             {'name': name, 'points': points})
            
        except sqlite3.IntegrityError:
            pass  # Achievement already granted
        finally:
            conn.close()
    
    def _add_activity(self, user_id: str, activity_type: str, target_type: str,
                     target_id: str, activity_data: Dict):
        """Add activity to user's feed"""
        
        activity_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_feed 
            (activity_id, user_id, activity_type, target_type, target_id,
             activity_data, activity_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (activity_id, user_id, activity_type, target_type, target_id,
              json.dumps(activity_data), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _check_sharing_achievements(self, user_id: str):
        """Check and grant sharing-related achievements"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count user's shares
        cursor.execute('''
            SELECT COUNT(*) FROM shared_swings WHERE user_id = ?
        ''', (user_id,))
        
        share_count = cursor.fetchone()[0]
        conn.close()
        
        # Grant achievements based on share count
        if share_count == 1:
            self._grant_achievement(user_id, 'first_share', 'First Share',
                                  'Shared your first swing', 100)
        elif share_count == 5:
            self._grant_achievement(user_id, 'active_sharer', 'Active Sharer',
                                  'Shared 5 swings', 250)
        elif share_count == 25:
            self._grant_achievement(user_id, 'swing_ambassador', 'Swing Ambassador',
                                  'Shared 25 swings', 500)
    
    def _format_shared_swing(self, swing_data) -> Dict:
        """Format shared swing data for API response"""
        
        return {
            'share_id': swing_data[0],
            'user_id': swing_data[1],
            'analysis_id': swing_data[2],
            'title': swing_data[3],
            'description': swing_data[4],
            'video_url': swing_data[5],
            'thumbnail_url': swing_data[6],
            'privacy_level': swing_data[7],
            'allow_comments': swing_data[8],
            'share_date': swing_data[9],
            'view_count': swing_data[10],
            'like_count': swing_data[11],
            'comment_count': swing_data[12],
            'tags': json.loads(swing_data[13]) if swing_data[13] else [],
            'username': swing_data[14] if len(swing_data) > 14 else None,
            'display_name': swing_data[15] if len(swing_data) > 15 else None,
            'avatar_url': swing_data[16] if len(swing_data) > 16 else None
        }
    
    def get_user_profile(self, user_id: str, viewer_id: str = None) -> Dict:
        """Get user's social profile with privacy filtering"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM social_users WHERE user_id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        if not user:
            conn.close()
            return {'error': 'User not found'}
        
        # Check if viewer can see full profile
        can_view_full = (user_id == viewer_id or 
                        user[8] == 'public' or  # privacy_level
                        self._are_friends(user_id, viewer_id))
        
        # Get follower/following counts
        cursor.execute('SELECT COUNT(*) FROM follows WHERE following_id = ?', (user_id,))
        follower_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM follows WHERE follower_id = ?', (user_id,))
        following_count = cursor.fetchone()[0]
        
        # Get recent achievements
        cursor.execute('''
            SELECT achievement_name, description, points, achievement_date
            FROM achievements WHERE user_id = ?
            ORDER BY achievement_date DESC LIMIT 5
        ''', (user_id,))
        
        recent_achievements = cursor.fetchall()
        
        conn.close()
        
        profile = {
            'user_id': user[0],
            'username': user[1],
            'display_name': user[2],
            'bio': user[4] if can_view_full else None,
            'avatar_url': user[5],
            'location': user[6] if can_view_full else None,
            'handicap': user[7] if can_view_full else None,
            'join_date': user[9],
            'total_swings': user[10],
            'best_score': user[11],
            'achievement_points': user[12],
            'verified': user[13],
            'follower_count': follower_count,
            'following_count': following_count,
            'recent_achievements': [
                {
                    'name': ach[0],
                    'description': ach[1],
                    'points': ach[2],
                    'date': ach[3]
                } for ach in recent_achievements
            ]
        }
        
        return profile
    
    def _are_friends(self, user1_id: str, user2_id: str) -> bool:
        """Check if two users follow each other (mutual follow = friends)"""
        
        if not user2_id:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM follows 
            WHERE (follower_id = ? AND following_id = ?)
            OR (follower_id = ? AND following_id = ?)
        ''', (user1_id, user2_id, user2_id, user1_id))
        
        mutual_follows = cursor.fetchone()[0]
        conn.close()
        
        return mutual_follows == 2  # Both follow each other 