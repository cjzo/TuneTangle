const SPOTIFY_AUTHORIZE_ENDPOINT = 'https://accounts.spotify.com/authorize';

const CLIENT_ID = '5771d5d776964495b21177378f72c035';
const REDIRECT_URI = 'http://localhost:3000/callback';

const RESPONSE_TYPE = 'token';
const SCOPES = ['playlist-read-private'];

export const getSpotifyAuthUrl = (): string => {
  const scope = encodeURIComponent(SCOPES.join(' '));
  return `${SPOTIFY_AUTHORIZE_ENDPOINT}?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=${RESPONSE_TYPE}&scope=${scope}`;
};
