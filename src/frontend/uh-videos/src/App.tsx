import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import React, { useState, useEffect } from 'react';
import Movie from './components/MovieInfo/Movie';
import { MovieType } from './types/Movie';
import LoginModal from './components/LoginModal/LoginModal';
import RegisterModal from './components/RegisterModal/RegisterModal';
import Button from 'react-bootstrap/esm/Button';

function App() {
  const [user, setUser] = useState<any>()
  const [movies, setMovies] = useState<MovieType[]>([]);
  const [trace, setTrace] = useState([])
  const [error, setError] = useState('');

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/users/${user.id}/recommendations/`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const fetchedMovies = data.movies || data.results || data; // Ajusta según la estructura de tu API
        setMovies(fetchedMovies.recommendations);
        setTrace(fetchedMovies.trace);
        setError("");
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [user]); // El arreglo vacío significa que solo se ejecutará una vez al montaje del componente

  const getUserDetails = async () => {
    const token = localStorage.getItem('access');

    try {
      const response = await fetch('http://localhost:8000/api/user/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user details');
      }

      const userData = await response.json();
      // console.log('User details:', userData);
      return userData;
    } catch (error) {
      console.error('Error fetching user details:', error);
      return null;
    }
  };


  useEffect(() => {
    getUserDetails().then(userC => {
      if (userC) {
        setUser(userC);
      }
    });
  }, []);

  const handleLogout = () => {
    // Eliminar los tokens del almacenamiento local
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.replace("/")

  };


  return (
    <div className="relative">
      {loading ? (
        <div>Cargando...</div>
      ) : (
        <div>
          {
            user &&
            <div className='user-name'>Hola {user?.username}</div>
          }
          <div className="d-flex align-items-center justify-content-center">
            <img className="main-icon" src="../public/R (1).jpg" alt="" />
            <h1>UH-VIDEOS</h1>
          </div>
          <div className="user-admin">
            {user ?
              <Button variant="danger" onClick={handleLogout}>
                Log out
              </Button>
              :
              <>
                <div className='me-2'>
                  <LoginModal />
                </div>
                <RegisterModal />
              </>
            }
          </div>
          <nav className="navbar navbar-expand-lg">
            <div className="container-fluid">
              <img src="../public/almamaterw.png" className='alma-mater-icon' alt='uh' />
              <form className="d-flex w-100" role="search">
                <input className="form-control me-3 ms-3" type="search" placeholder="Search" aria-label="Search" />
                <button className="btn btn-outline-light text-light" type="submit">Search</button>
              </form>
            </div>
          </nav>

          <div className='movies-container'>
            {error ? (
              <div className="error-message">Cargando...</div>
            ) : (
              movies.map((movie, index) => (
                <Movie
                  title={movie.title}
                  genres={movie.genre}
                  director={movie.director}
                  date={movie.release_date}
                  description={movie.description}
                  explanation={trace[index]}
                  key={index}
                />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );

}

export default App;
