import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Button,
    Stack,
    VStack,
    Heading,
    Text,
    Input,
    Card,
    CardBody,
    CardFooter,
    Spinner,
    Image,
    Divider
} from "@chakra-ui/react";
import { motion } from 'framer-motion';
import '../App.css';
import Upload from '../media/upload.png';

interface Result {
    track: string;
    video?: string;
    error?: string;
}

const Recommendations = () => {
    const [cursorPosition, setCursorPosition] = useState({ x: -100, y: -100 });
    const [songQuery, setSongQuery] = useState('');
    const [results, setResults] = useState<Result[]>([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [embeds, setEmbeds] = useState<{ [key: number]: string }>({});
    const fileInputRef = useRef<HTMLInputElement>(null);

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

    const getRecommendations = async (query = songQuery) => {
        if(loading) return;
        setLoading(true);
        const code = localStorage.getItem('spotify_access_token');
        if (!code) {
            setError('Please log in to Spotify to get recommendations.');
            setResults([]);
            setLoading(false);
            return;
        }
        try {
            const response = await fetch('/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    song_query: query,
                    code: code
                })
            });
    
            const data = await response.json();
    
            if (data.error) {
                setError(data.error);
                setResults([]);
            } else {
                setError('');
                setResults(data);
                fetchEmbeds(data);
            }
        } catch (err) {
            setError('An error occurred while fetching recommendations.');
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    const fetchEmbeds = async (results: Result[]) => {
        const newEmbeds: { [key: number]: string } = {};
        await Promise.all(results.map(async (result, index) => {
            if (result.video) {
                const response = await fetch(`https://www.tiktok.com/oembed?url=${result.video}`);
                const data = await response.json();
                newEmbeds[index] = data.html;
            }
        }));
        setEmbeds(newEmbeds);
    };

    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'https://www.tiktok.com/embed.js';
        script.async = true;
        document.body.appendChild(script);
        return () => {
            document.body.removeChild(script);
        };
    }, [embeds]);

    const handleFileUpload = async (event: any) => {
        if (event.target.files.length === 0) {
            console.log("No file selected")
            return;
        }
        const file = event.target.files[0];
        if(!isVideo(file.name)){
          setError('Invalid file type. Please upload a video file.');
          return;
        }
        setLoading(true);
        setSongQuery('');
        setError('')
        let query = ''
        const formData = new FormData();
        formData.append('file', file);
        try {
          const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
          });
      
          if (response.status === 404) {
            throw new Error('No song detected.');
          }
          else if (!response.ok) {
            throw new Error('A file upload error occured');
          }
      
          // Process server's response here
          const data = await response.json();
          console.log(data.message);
          setSongQuery(data.message);
          query = data.message;
        } catch (error: any) {
          setError(error.message);
          console.error('Error:', error.message);
        }
        event.target.value = null;
        if(query !== '') {
            getRecommendations(query);
        }
        else{
            setLoading(false)
        }
      };

    const handleUploadButton = () => {
        fileInputRef.current?.click();
    };

    function isVideo(filename: string) {
        const parts = filename.split('.');
        const ext = parts[parts.length - 1];
        switch (ext.toLowerCase()) {
          case 'mp4':
          case 'mov': //can add more video extensions
            return true;
        }
        return false;
      }

    const handleAddToLikeButton = async (track: string) => {
        try {
            const response = await fetch('/add-liked', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'liked_song': track
                })
            });
            if (!response.ok) {
                throw new Error('An error occurred while adding song to liked songs.');
            }
            const data = await response.json();
            console.log(data);
        } catch (err) {
            console.error(err);
        }
    }

    const handleSubmit = () => {
        getRecommendations();
    }

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
                                onChange={handleInputChange}
                                onKeyDown={event => {
                                    if (event.key === 'Enter') {
                                        getRecommendations();
                                    }
                                }}
                                placeholder="Enter song name"
                                size="lg"
                                mt={5}
                                mb={1}
                                className="searchbar-main"
                            />
                            <Text
                                fontSize={["lg", "2xl"]}
                                maxW="800px"
                                textAlign="center"
                                data-aos="fade-up"
                                data-aos-delay="100"
                                mt={0}
                                mb={0}
                                fontWeight="bold"
                                className="text-shadow">
                                OR
                            </Text>
                            <Input id="file-upload" type="file" onChange={handleFileUpload} ref={fileInputRef} style={{ display: 'none' }} size="xs"/>
                            <Button className="alt-button" onClick={handleUploadButton}>
                                <Box pr={4}>
                                    <Image
                                        src={Upload}
                                        height="25px"
                                    />
                                </Box>
                                <Text>
                                        Upload Video
                                </Text>
                            </Button>
                            <Divider w="70%" mx="auto"/>
                            <Button onClick={handleSubmit} className="main-button" size="lg" height="4rem" px="2rem">
                                Get Recommendations
                            </Button>
                            {error && <Text color="red.500">{error}</Text>}
                            <Box className="results" mt={5} textAlign="center">
                                {loading ? (
                                    <Spinner size="xl" />
                                ) : (
                                    <Stack spacing={4} direction="column" align="center">
                                        {results.map((result, index) => (
                                            <Card className="custom-card" key={index} borderWidth="0px" borderRadius="lg" overflow="hidden" p={4}>
                                                {result.error ? (
                                                    <Text color="red.500">{result.track}: {result.error}</Text>
                                                ) : (
                                                    <>
                                                        <CardBody>
                                                            {embeds[index] ? (
                                                                <Box
                                                                    dangerouslySetInnerHTML={{ __html: embeds[index] }}
                                                                />
                                                            ) : (
                                                                <Spinner />
                                                            )}
                                                        </CardBody>
                                                        <CardFooter>
                                                            <Text as="span" fontWeight="bold">{result.track}</Text>
                                                            <Button onClick={() => handleAddToLikeButton(result.track)} className="alt-button" size="sm" ml={2}>
                                                                Add to Liked Songs
                                                            </Button>
                                                        </CardFooter>
                                                    </>
                                                )}
                                            </Card>
                                        ))}
                                    </Stack>
                                )}
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