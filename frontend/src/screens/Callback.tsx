import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Callback: React.FC = () => {
    const navigate = useNavigate();

    useEffect(() => {
        const hash = window.location.hash;
        const token = hash
            .substring(1)
            .split('&')
            .find(elem => elem.startsWith('access_token'))
            ?.split('=')[1];

        if (token) {
            localStorage.setItem('spotify_access_token', token);
            navigate('/loggedinhome');
        } else {
            const storedToken = localStorage.getItem('spotify_access_token');
            if (storedToken) {
                navigate('/loggedinhome');
            } else {
                navigate('/');
            }
        }
    }, [navigate]);

    return <div>Loading...</div>;
};

export default Callback;
