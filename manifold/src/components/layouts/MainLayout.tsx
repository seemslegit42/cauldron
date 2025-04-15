import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, theme, Space, Avatar, Dropdown, Badge } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  AppstoreOutlined,
  LineChartOutlined,
  SafetyOutlined,
  BookOutlined,
  CodeOutlined,
  SettingOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const userMenuItems = [
    {
      key: 'profile',
      label: 'Profile',
      icon: <UserOutlined />,
    },
    {
      key: 'settings',
      label: 'Settings',
      icon: <SettingOutlined />,
    },
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
    },
  ];

  return (
    <Layout className="app-container">
      <Sider trigger={null} collapsible collapsed={collapsed} width={250}>
        <div className="logo">
          {collapsed ? 'C' : 'Cauldron™'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname.split('/')[1] || 'dashboard']}
          items={[
            {
              key: 'dashboard',
              icon: <DashboardOutlined />,
              label: <Link to="/">Dashboard</Link>,
            },
            {
              key: 'operations',
              icon: <AppstoreOutlined />,
              label: <Link to="/operations">Operations</Link>,
            },
            {
              key: 'intelligence',
              icon: <LineChartOutlined />,
              label: <Link to="/intelligence">Intelligence</Link>,
            },
            {
              key: 'security',
              icon: <SafetyOutlined />,
              label: <Link to="/security">Security</Link>,
            },
            {
              key: 'knowledge',
              icon: <BookOutlined />,
              label: <Link to="/knowledge">Knowledge</Link>,
            },
            {
              key: 'devops',
              icon: <CodeOutlined />,
              label: <Link to="/devops">DevOps</Link>,
            },
            {
              key: 'settings',
              icon: <SettingOutlined />,
              label: <Link to="/settings">Settings</Link>,
            },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingRight: 24 }}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ fontSize: '16px', width: 64, height: 64 }}
            />
            <Space size="large">
              <Badge count={5}>
                <Button type="text" icon={<BellOutlined />} size="large" />
              </Badge>
              <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
                <Space>
                  <Avatar icon={<UserOutlined />} />
                  <span>Admin</span>
                </Space>
              </Dropdown>
            </Space>
          </div>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;