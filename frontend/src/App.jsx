import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import HotelList from './pages/HotelList';
import HotelDetail from './pages/HotelDetail';
import SentimentAnalyzer from './pages/SentimentAnalyzer';
import ReviewSummaryPage from './pages/ReviewSummaryPage';
import Login from './pages/Login';
import Register from './pages/Register';
import RequestPasswordReset from './pages/RequestPasswordReset';
import ResetPassword from './pages/ResetPassword';
import Profile from './pages/Profile';
import MyReviews from './pages/MyReviews';
import Home from './pages/Home';
import About from './pages/About';
import { AuthProvider } from './auth/AuthProvider';
import ProtectedRoute from './components/ProtectedRoute.jsx';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          <Header />

          <main style={{ flex: 1 }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/hotels" element={<HotelList />} />
              <Route path="/hotel/:id" element={<HotelDetail />} />

              <Route
                path="/analyze"
                element={
                  <ProtectedRoute>
                    <SentimentAnalyzer />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/summaries"
                element={
                  <ProtectedRoute>
                    <ReviewSummaryPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/my-reviews"
                element={
                  <ProtectedRoute>
                    <MyReviews />
                  </ProtectedRoute>
                }
              />

              <Route path="/about" element={<About />} />

              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/request-password-reset" element={<RequestPasswordReset />} />
              <Route path="/reset-password" element={<ResetPassword />} />
            </Routes>
          </main>

          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;