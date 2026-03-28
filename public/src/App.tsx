import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage } from './pages/LoginPage'
import { ProtectedRoute } from './components/ProtectedRoute'
import { LoadingSpinner } from './components/LoadingSpinner'

const UserPage = lazy(() => import('./pages/UserPage').then(module => ({ default: module.UserPage })))
const AdminPage = lazy(() => import('./pages/AdminPage').then(module => ({ default: module.AdminPage })))

function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      
      <Route 
        path="/user" 
        element={
          <ProtectedRoute requiredRole="user">
            <Suspense fallback={<LoadingSpinner />}>
              <UserPage />
            </Suspense>
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/user/:questionId" 
        element={
          <ProtectedRoute requiredRole="user">
            <Suspense fallback={<LoadingSpinner />}>
              <UserPage />
            </Suspense>
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute requiredRole="admin">
            <Suspense fallback={<LoadingSpinner />}>
              <AdminPage />
            </Suspense>
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/admin/:questionId" 
        element={
          <ProtectedRoute requiredRole="admin">
            <Suspense fallback={<LoadingSpinner />}>
              <AdminPage />
            </Suspense>
          </ProtectedRoute>
        } 
      />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
