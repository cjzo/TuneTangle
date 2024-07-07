import React, { useEffect, useState } from 'react';
import { Box, Button, Image, Text } from '@chakra-ui/react';
import Spotify from './media/spotify.png';
import { Link } from 'react-router-dom';
import { getSpotifyAuthUrl } from './auth/spotify-auth';

const LoginButton: React.FC = () => {

    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('spotify_access_token');
        setIsLoggedIn(!!token);
    }, []);

    const handleLogin = () => {
        window.location.href = getSpotifyAuthUrl();
    };

    const handleLogout = () => {
        localStorage.removeItem('spotify_access_token');
        setIsLoggedIn(false);
    };

    async function fetchProfile(token: string): Promise<any> {
        const result = await fetch("https://api.spotify.com/v1/me", {
            method: "GET", headers: { Authorization: `Bearer ${token}` }
        });
        return await result.json();
    }

    const token = localStorage.getItem('access_token')

    if (token) {
        fetchProfile(token)
            .then(profile => {
                const username = profile.display_name;
                localStorage.setItem('user_name', username);
            })
            .catch(error => {
                console.error("Error fetching profile:", error);
            });
    }

    return (
        isLoggedIn ? (
            <Button as={Link} onClick={handleLogout} className="alt-button" to="/logout">
                Logout
            </Button>
        ) : (
            <Button className="alt-button" onClick={handleLogin}>
                <Box pr={2}>
                    <Image
                        src={Spotify}
                        height="15px"
                        alt="Spotify"
                    />
                </Box>
                <Text>Connect</Text>
            </Button>
        )
    );
};

export default LoginButton;
