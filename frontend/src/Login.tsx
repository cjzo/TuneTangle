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
