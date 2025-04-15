import React from 'react';
import { Typography, Card, Tabs, Button, List, Tag, Progress, Space } from 'antd';
import { 
  CodeOutlined, 
  RocketOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  SyncOutlined,
  BranchesOutlined,
  ApiOutlined,
  ClockCircleOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { TabPane } = Tabs;

const DevOps: React.FC = () => {
  // Mock deployment data
  const deployments = [
    { 
      id: 1, 
      name: 'cauldron-api', 
      version: 'v1.2.3', 
      status: 'success', 
      environment: 'production',
      time: '2 hours ago',
      duration: '3m 42s'
    },
    { 
      id: 2, 
      name: 'manifold-ui', 
      version: 'v0.9.5', 
      status: 'success', 
      environment: 'production',
      time: '3 hours ago',
      duration: '2m 18s'
    },
    { 
      id: 3, 
      name: 'synapse-analytics', 
      version: 'v2.1.0', 
      status: 'failed', 
      environment: 'staging',
      time: '5 hours ago',
      duration: '4m 12s'
    },
    { 
      id: 4, 
      name: 'aegis-security', 
      version: 'v1.5.2', 
      status: 'in-progress', 
      environment: 'development',
      time: 'Just now',
      duration: '1m 30s'
    },
  ];

  // Mock pipeline data
  const pipelines = [
    { id: 1, name: 'Build & Test', status: 'success', progress: 100 },
    { id: 2, name: 'Security Scan', status: 'success', progress: 100 },
    { id: 3, name: 'Deploy to Staging', status: 'in-progress', progress: 65 },
    { id: 4, name: 'Integration Tests', status: 'pending', progress: 0 },
    { id: 5, name: 'Deploy to Production', status: 'pending', progress: 0 },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#f5222d' }} />;
      case 'in-progress':
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      case 'pending':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return <QuestionCircleOutlined style={{ color: '#faad14' }} />;
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={2}>Command & Cauldron™ DevOps</Title>
          <Paragraph>Manage your development, deployment, and infrastructure.</Paragraph>
        </div>
        <Button type="primary" icon={<RocketOutlined />}>
          New Deployment
        </Button>
      </div>
      
      <Card>
        <Tabs defaultActiveKey="deployments">
          <TabPane tab="Deployments" key="deployments">
            <List
              itemLayout="horizontal"
              dataSource={deployments}
              renderItem={item => (
                <List.Item
                  actions={[
                    <Button type="link">View Logs</Button>,
                    <Button type="link">Rollback</Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={getStatusIcon(item.status)}
                    title={
                      <Space>
                        <Text strong>{item.name}</Text>
                        <Tag color="blue">{item.version}</Tag>
                        <Tag color={
                          item.environment === 'production' ? 'red' : 
                          item.environment === 'staging' ? 'orange' : 'green'
                        }>
                          {item.environment}
                        </Tag>
                      </Space>
                    }
                    description={
                      <Space>
                        <Text type="secondary">Deployed {item.time}</Text>
                        <Text type="secondary">•</Text>
                        <Text type="secondary">Duration: {item.duration}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </TabPane>
          <TabPane tab="Pipelines" key="pipelines">
            <List
              itemLayout="horizontal"
              dataSource={pipelines}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={getStatusIcon(item.status)}
                    title={item.name}
                    description={
                      <Progress 
                        percent={item.progress} 
                        status={
                          item.status === 'success' ? 'success' : 
                          item.status === 'failed' ? 'exception' : 'active'
                        } 
                      />
                    }
                  />
                </List.Item>
              )}
            />
          </TabPane>
          <TabPane tab="Infrastructure" key="infrastructure">
            <p>Infrastructure management and monitoring will be displayed here.</p>
          </TabPane>
          <TabPane tab="Repositories" key="repositories">
            <p>Code repositories and version control will be displayed here.</p>
          </TabPane>
          <TabPane tab="API Gateway" key="api">
            <p>API management and documentation will be displayed here.</p>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default DevOps;