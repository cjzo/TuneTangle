import { extendTheme, type ThemeConfig } from "@chakra-ui/react";

// 2. Add your color mode config
const config: ThemeConfig = {
  initialColorMode: "dark",
  useSystemColorMode: false,
};

// const fonts = {
//   heading: "Outfit",
//   body: "Open Sans",
// };


const colors = {
  blue: {
    50: "#e0edff",
    100: "#b0caff",
    200: "#7ea6ff",
    300: "#4b83ff",
    400: "#1a5fff",
    500: "#0042da",
    600: "#0036b4",
    700: "#002782",
    800: "#001751",
    900: "#1a202c",
  },
  orange: {
    50: "#fff1da",
    100: "#ffd7ae",
    200: "#ffbf7d",
    300: "#ffa54c",
    400: "#ff8b1a",
    500: "#e67200",
    600: "#b45800",
    700: "#813e00",
    800: "#4f2500",
    900: "#200b00",
  },
  yellow: {
    50: "#fff9da",
    100: "#ffedad",
    200: "#ffe17d",
    300: "#ffd54b",
    400: "#ffc91a",
    500: "#e6b000",
    600: "#b38800",
    700: "#806200",
    800: "#4e3a00",
    900: "#1d1400",
  },
};

const components = {
  Button: {
    defaultProps: {
      colorScheme: "blue",
    },
    variants: {
      solid: () => ({
        bg: "blue.400",
        color: "white",
        _hover: {
          bg: "blue.300",
        },
      }),
    },
  },
  NumberInput: {
    defaultProps: {
      focusBorderColor: "blue.200",
    },
  },
  Input: {
    defaultProps: {
      focusBorderColor: "#40444D",
    },
  },
  Popover: {
    baseStyle: {
      popper: {
        width: "fit-content",
        maxWidth: "fit-content",
      },
    },
  },
  Tooltip: {
    baseStyle: {
      borderRadius: "md",
    },
  },
  Link: {
    baseStyle: {
      _hover: { textDecoration: "none" },
    },
  },
};

const theme = extendTheme({
  // fonts,
  components,
  colors,
  config,
});

export default theme;