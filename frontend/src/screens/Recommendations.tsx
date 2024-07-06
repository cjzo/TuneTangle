import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Stack,
    VStack,
    Heading,
    Text,
    Input,
    Image
} from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { motion } from 'framer-motion';
import '../App.css';

const Recommendations = () => {
    const [cursorPosition, setCursorPosition] = useState({ x: -100, y: -100 });
    const [songQuery, setSongQuery] = useState('');
    const [results, setResults] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setCursorPosition({ x: e.clientX, y: e.clientY });
        };

        window.addEventListener('mousemove', handleMouseMove);

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSongQuery(e.target.value);
    };

    const getRecommendations = async () => {
        const accessToken = localStorage.getItem('spotify_access_token');
        
        try {
            const response = await fetch('/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    song_query: songQuery,
                    access_token: accessToken
                })
            });

            const data = await response.json();

            if (data.error) {
                setError(data.error);
                setResults([]);
            } else {
                setError('');
                setResults(data);
            }
        } catch (err) {
            setError('An error occurred while fetching recommendations.');
            setResults([]);
        }
    };

    return (
        <Box display="flex" flexDirection="column" minHeight="90vh" overflow="hidden">
            <Box as="section" flex="1" overflow="hidden" p={4} pos="relative" display="flex" flexDirection="column">
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
                <Stack mx="auto" py="5" pos="relative" pb="40" px={[4, 0]} flex="1" justify="center">
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
                                Music Recommendations
                            </Heading>
                            <Input
                                value={songQuery}
                                onChange={handleInputChange}
                                placeholder="Enter song name"
                                size="lg"
                                mt={5}
                                mb={1}
                                className="searchbar"
                            />
                            <Button onClick={getRecommendations} className="main-button" size="lg" height="4rem" px="2rem">
                                Get Recommendations
                            </Button>
                            {error && <Text color="red.500">{error}</Text>}
                            <Box className="results" mt={5}>
                                <ul>
                                    {results.map((track, index) => (
                                        <li key={index}>{track}</li>
                                    ))}
                                </ul>
                            </Box>
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
                height="50px"
                flexShrink="0"
            >
                &copy; 2024 TTRP
            </Box>
        </Box>
    );
};

export default Recommendations;