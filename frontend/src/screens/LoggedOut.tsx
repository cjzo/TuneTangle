import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Stack,
    VStack,
    Heading,
    Text,
    Image
} from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { motion } from 'framer-motion';
import Spotify from '../media/spotify.png';
import '../App.css';

import { getSpotifyAuthUrl } from '../auth/spotify-auth';

function LoggedInHome() {
    const handleSpotifyLogin = () => {
        window.location.href = getSpotifyAuthUrl();
    };

    const [cursorPosition, setCursorPosition] = useState({ x: -100, y: -100 });

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setCursorPosition({ x: e.clientX, y: e.clientY });
        };

        window.addEventListener('mousemove', handleMouseMove);

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);

    return (
        <Box>
            <Box as="section" overflow="hidden" p={4} pos="relative">
                <motion.div
                    style={{
                        position: 'fixed',
                        top: cursorPosition.y - 75,
                        left: cursorPosition.x - 75,
                        width: 150,
                        height: 150,
                        borderRadius: '50%',
                        background: 'linear-gradient(45deg, rgba(72, 187, 120, 0.45), rgba(168, 85, 247, 0.45))',
                        filter: 'blur(40px)',
                        zIndex: -1,
                        pointerEvents: 'none',
                    }}
                />
                <Stack mx="auto" py="5" pos="relative" pb="40" px={[4, 0]}>
                    <VStack mb="20" spacing={20} alignItems="center">
                        <VStack spacing="6" w="full">
                            <Heading
                                as="h1"
                                fontSize={["4xl", "4xl", "5xl", "7xl"]}
                                textAlign="center"
                                maxW="1000px"
                                bgGradient="linear(to-r, green.400, purple.500)"
                                bgClip="text"
                                data-aos="fade-up"
                            >
                                Sound Search
                            </Heading>
                            <Text
                                fontSize={["lg", "xl"]}
                                maxW="800px"
                                textAlign="center"
                                data-aos="fade-up"
                                data-aos-delay="100"
                                mt={5}
                                mb={1}
                                className="text-shadow"
                                minHeight={["60px", "80px", "100px"]}
                            >
                                You have been logged out.
                            </Text>
                            <Text
                                fontSize={["lg", "2xl"]}
                                maxW="800px"
                                textAlign="center"
                                data-aos="fade-up"
                                data-aos-delay="100"
                                mt={1}
                                mb={4}
                                fontWeight="bold"
                                className="text-shadow">
                                Discover music and ideas like magic 🪄
                            </Text>
                            <Stack
                                direction={["column-reverse", "row"]}
                                data-aos="fade-up"
                                data-aos-delay="200"
                            >
                                <Button as={Link} onClick={handleSpotifyLogin} to="/loggedinhome" className="alt-button" size="lg" height="4rem" px="2rem">
                                    <Box pr={4}>
                                        <Image
                                            src={Spotify}
                                            height="25px"
                                        />
                                    </Box>
                                    <Text>Connect to Spotify</Text>
                                </Button>
                            </Stack>
                        </VStack>

                        <Box maxW="1200px" pos="absolute" zIndex={-1} top={450}>
                            <Box
                                pos="absolute"
                                left="-40px"
                                bgColor="purple.500"
                                boxSize={["150px", "150px", "300px", "600px"]}
                                rounded="full"
                                filter="blur(40px)"
                                opacity="0.3"
                                className="animated-blob"
                                data-aos="fade"
                                data-aos-delay="1200"
                            />
                            <Box
                                pos="absolute"
                                right="-40px"
                                bgColor="green.500"
                                boxSize={["150px", "300px", "600px"]}
                                rounded="full"
                                filter="blur(40px)"
                                opacity="0.3"
                                className="animated-blob animation-delay-5000"
                                data-aos="fade"
                                data-aos-delay="1200"
                            />
                            <Box
                                as="figure"
                                shadow="lg"
                                data-aos="zoom-out-up"
                                data-aos-delay="800"
                            ></Box>
                        </Box>
                    </VStack>
                </Stack>
            </Box>
            <Box
                p="4"
                textAlign="center"
                borderTop="1px solid gray"
                color="gray.500"
            >
                &copy; 2024 TTRP
            </Box>
        </Box>
    );
};

export default LoggedInHome;