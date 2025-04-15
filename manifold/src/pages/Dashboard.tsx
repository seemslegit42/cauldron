import React from 'react';
import { Card, Row, Col, Statistic, Typography, List, Timeline, Space } from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined, 
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const Dashboard: React.FC = () => {
  // Mock data
  const recentActivities = [
    { id: 1, title: 'Invoice #INV-2023-001 created', time: '10 minutes ago', type: 'operations' },
    { id: 2, title: 'Security alert: Unusual login attempt', time: '30 minutes ago', type: 'security' },
    { id: 3, title: 'Sales forecast updated for Q2', time: '1 hour ago', type: 'intelligence' },
    { id: 4, title: 'New knowledge article: "AI Integration"', time: '2 hours ago', type: 'knowledge' },
    { id: 5, title: 'Deployment completed: v2.3.0', time: '3 hours ago', type: 'devops' },
  ];

  const systemStatus = [
    { name: 'Operations Core', status: 'operational', icon: <CheckCircleOutlined style={{ color: 'green' }} /> },
    { name: 'Synapse Intelligence', status: 'operational', icon: <CheckCircleOutlined style={{ color: 'green' }} /> },
    { name: 'Aegis Security', status: 'warning', icon: <ExclamationCircleOutlined style={{ color: 'orange' }} /> },
    { name: 'Lore Knowledge', status: 'operational', icon: <CheckCircleOutlined style={{ color: 'green' }} /> },
    { name: 'Command & Cauldron', status: 'incident', icon: <WarningOutlined style={{ color: 'red' }} /> },
  ];

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Paragraph>Welcome to Cauldron™ sEOS. Here's your enterprise overview.</Paragraph>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Revenue (MTD)"
              value={120500}
              precision={2}
              valueStyle={{ color: '#3f8600' }}
              prefix="$"
              suffix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Expenses (MTD)"
              value={95200}
              precision={2}
              valueStyle={{ color: '#cf1322' }}
              prefix="$"
              suffix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Active Orders"
              value={42}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Security Alerts"
              value={3}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} md={12}>
          <Card title="Recent Activities">
            <List
              itemLayout="horizontal"
              dataSource={recentActivities}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.title}
                    description={
                      <Space>
                        <ClockCircleOutlined />
                        {item.time}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="System Status">
            <Timeline mode="left">
              {systemStatus.map((item, index) => (
                <Timeline.Item key={index} dot={item.icon}>
                  <Space>
                    <span style={{ fontWeight: 'bold' }}>{item.name}</span>
                    <span style={{ 
                      textTransform: 'capitalize', 
                      color: item.status === 'operational' ? 'green' : 
                             item.status === 'warning' ? 'orange' : 'red' 
                    }}>
                      {item.status}
                    </span>
                  </Space>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;