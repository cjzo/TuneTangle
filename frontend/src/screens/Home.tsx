import React from 'react';
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
  import Spotify from '../media/spotify.png';

function Home() {
      
        return (
          <Box>
          <Box as="section" overflow="hidden" p={4}>
            <Stack mx="auto" py="5" pos="relative" pb="32" px={[4, 0]}>
              <VStack mb="20" spacing={20} alignItems="center">
                <VStack spacing="6" w="full">
                  {/* <Image
                    src={Logo}
                    width="300px"
                    height="300px"
                    borderRadius="full"
                  /> */}
                  <Heading
                    as="h1"
                    fontSize={["4xl", "4xl", "5xl", "7xl"]}
                    textAlign="center"
                    maxW="1000px"
                    bgGradient="linear(to-r, green.400, purple.500)"
                    bgClip="text"
                    data-aos="fade-up"
                  >
                    Sound Searcher
                  </Heading>
                  <Text
                    fontSize={["lg", "xl"]}
                    maxW="800px"
                    textAlign="center"
                    data-aos="fade-up"
                    data-aos-delay="100"
                    mt={5}
                    mb={5}
                  >
                    Discover a wide range of new sounds, songs, and trends. Using 
                    songs that you already love, sound searcher uses Spotify and TikTok
                    to get similar "underground" songs and videos for you to enjoy. 
                    Find music and ideas like magic. 🪄
                  </Text>
                  <Stack
                    direction={["column-reverse", "row"]}
                    data-aos="fade-up"
                    data-aos-delay="200"
                  >
                    <Button as={Link} to="/login" size="lg" height="4rem" px="2rem">
                    <Box pr={4}>
                        <Image
                        src={Spotify}
                        height="25px"
                        />
                    </Box>
                    <Text>Login with Spotify</Text>
                    </Button>
                  </Stack>
                </VStack>
                {/* <Flex
                  direction="column"
                  align="center"
                  justify="center"
                  w="100%"
                  h="100%"
                >
                  <Heading as="h2" mb={4}>
                    Latest Listings 📈
                  </Heading>
                </Flex> */}
      
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
            <Box p="4" textAlign="center" borderTop="1px solid gray">
              &copy; 2024 TTRP
            </Box>
          </Box>
        );
};

export default Home;