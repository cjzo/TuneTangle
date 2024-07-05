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
  Input,
  InputGroup,
  InputRightElement
} from "@chakra-ui/react";
import Logo from './media/TikTok-logo.png';
import Spotify from './media/spotify.png';
import Search from './media/search.png';
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
      
      <HStack spacing={5}>
      <Box className="SearchContainer">
        <InputGroup>
          <InputRightElement pointerEvents="none">
            <Image src={Search} alt="Search Icon" width="18px" height="18px" />
          </InputRightElement>
          <Input
            type="text"
            placeholder="Search for music"
            autoComplete="off"
            aria-autocomplete="list"
            aria-expanded="false"
            role="combobox"
            className="searchInput"
          />
        </InputGroup>
      </Box>
      <ButtonGroup spacing={5}>
          <Button as={Link} className="alt-button" to="/login">
            <Box pr={2}>
            <Image
            src={Spotify}
            height="15px"
          />
          </Box>
          <Text>Connect</Text>
          </Button>
          <Button as={Link} className="alt-button" to="/logout">
            Logout
          </Button>
      </ButtonGroup>
      </HStack>
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
