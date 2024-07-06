import React from 'react';
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
import Search from './media/search.png';
import Home from './screens/Home';
import { Link, Route, Routes } from "react-router-dom";

import Callback from './screens/Callback';

import LoggedInHome from './screens/LoggedInHome';
import LoggedOut from './screens/LoggedOut';
import LoginButton from './Login';

const App: React.FC = () => {
  const handleLogout = () => {
    localStorage.removeItem('spotify_access_token');
  };

  return (
    <Box className="App">
      <Flex align="center" justify="space-between" p="4">
        <Heading as="h1" size="lg">
          <ChakraLink as={Link} to="/callback">
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
            <LoginButton></LoginButton>
          </ButtonGroup>
        </HStack>
      </Flex>

      <Box>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/callback" element={<Callback />} />
          <Route path="/loggedinhome" element={<LoggedInHome />} />
          <Route path="/logout" element={<LoggedOut />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
