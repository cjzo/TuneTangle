import React from 'react';
import './App.css';
import {
  Link as ChakraLink,
  Box,
  Button,
  ButtonGroup,
  Image,
  HStack,
  Flex,
  Text,
  Heading,
} from "@chakra-ui/react";
import Logo from './media/TikTok-logo.png';
import Spotify from './media/spotify.png';
import Home from './screens/Home';
import { Link, Route, Routes } from "react-router-dom";

function App() {

  return (
    <Box className="App">
    <Flex align="center" justify="space-between" p="4" >
      <Heading as="h1" size="lg" >
        <ChakraLink as={Link} to="/">
          <HStack spacing={5}>
          <Image
            src={Logo}
            height="45px"
            backgroundColor={'whitesmoke'}
          />
          <Text>Music Discovery</Text>
          </HStack>
        </ChakraLink>
      </Heading>
      <ButtonGroup spacing={5}>
          <Button as={Link} to="/login">
            <Box pr={2}>
            <Image
            src={Spotify}
            height="15px"
          />
          </Box>
          <Text>Login</Text>
          </Button>
          <Button as={Link} to="/logout">
            Logout
          </Button>
      </ButtonGroup>
    </Flex>

    <Box>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </Box>
  </Box>
  );
}

export default App;
