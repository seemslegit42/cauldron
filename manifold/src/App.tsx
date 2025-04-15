import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import MainLayout from './components/layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Operations from './pages/Operations';
import Intelligence from './pages/Intelligence';
import Security from './pages/Security';
import Knowledge from './pages/Knowledge';
import DevOps from './pages/DevOps';
import Settings from './pages/Settings';
import './styles/App.css';

const App: React.FC = () => {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="operations/*" element={<Operations />} />
            <Route path="intelligence/*" element={<Intelligence />} />
            <Route path="security/*" element={<Security />} />
            <Route path="knowledge/*" element={<Knowledge />} />
            <Route path="devops/*" element={<DevOps />} />
            <Route path="settings/*" element={<Settings />} />
          </Route>
        </Routes>
      </Router>
    </ConfigProvider>
  );
};

export default App;