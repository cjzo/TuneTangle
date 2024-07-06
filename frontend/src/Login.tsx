import React from 'react';
import { Box, Button, Image, Text } from '@chakra-ui/react';
import Spotify from './media/spotify.png';
import { getSpotifyAuthUrl } from './auth/spotify-auth';

const LoginButton: React.FC = () => {
    const handleLogin = () => {
        window.location.href = getSpotifyAuthUrl();
    };

    return (
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
    );
};

export default LoginButton;
