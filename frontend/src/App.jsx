import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './layouts/MainLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import NewAssessmentPage from './pages/NewAssessmentPage';
import ProfilePage from './pages/ProfilePage';
import LandingPage from './pages/LandingPage';
import AssessmentReportPage from './pages/AssessmentReportPage';
import ErrorBoundary from './components/ErrorBoundary';
import AdminDashboardPage from './pages/AdminDashboardPage';
function LegacyApplicationRedirect() { const { applicationId } = useParams(); return <Navigate to={`/applications/${applicationId}`} replace/>; }
export default function App() { return <AuthProvider><BrowserRouter><ErrorBoundary><Routes><Route path="/login" element={<LoginPage/>}/><Route path="/register" element={<RegisterPage/>}/><Route path="/" element={<LandingPage/>}/><Route element={<ProtectedRoute/>}><Route element={<MainLayout/>}><Route path="/dashboard" element={<DashboardPage/>}/><Route path="/assessment/new" element={<NewAssessmentPage/>}/><Route path="/assess/traditional" element={<Navigate to="/assessment/new?model=traditional" replace/>}/><Route path="/assess/alternative" element={<Navigate to="/assessment/new?model=alternative" replace/>}/><Route path="/applications/:applicationId" element={<AssessmentReportPage/>}/><Route path="/profile" element={<ProfilePage/>}/><Route path="/admin" element={<AdminDashboardPage/>}/><Route path="/history" element={<Navigate to="/profile" replace/>}/><Route path="/history/:applicationId" element={<LegacyApplicationRedirect/>}/></Route></Route><Route path="*" element={<Navigate to="/dashboard" replace/>}/></Routes></ErrorBoundary></BrowserRouter></AuthProvider>; }
