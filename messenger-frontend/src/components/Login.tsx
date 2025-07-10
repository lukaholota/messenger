import React, { useState } from 'react';
import axios from 'axios';

interface LoginProps {
  setAccessToken: React.Dispatch<React.SetStateAction<string | null>>;
}

export const Login: React.FC<LoginProps> = ({ setAccessToken }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await axios.post(
          'http://127.0.0.1:8000/api/v1/token',
          params,
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
      }}
          );
      const { access_token, refresh_token } = response.data;

      // Store tokens in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Set the access token in the app
      setAccessToken(access_token);
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};
