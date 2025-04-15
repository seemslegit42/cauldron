import React from 'react';
import { Typography, Card, Tabs, Button, Alert, Timeline, Badge, Space } from 'antd';
import { SafetyOutlined, WarningOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

const Security: React.FC = () => {
  // Mock security alerts
  const securityAlerts = [
    { id: 1, level: 'high', title: 'Unusual login attempt detected', time: '10 minutes ago', status: 'active' },
    { id: 2, level: 'medium', title: 'Outdated software version detected', time: '1 hour ago', status: 'active' },
    { id: 3, level: 'low', title: 'User password expiring soon', time: '2 hours ago', status: 'active' },
    { id: 4, level: 'high', title: 'Potential data exfiltration attempt', time: '1 day ago', status: 'resolved' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={2}>Aegis Protocol™ Security</Title>
          <Paragraph>Proactive cybersecurity monitoring and defense.</Paragraph>
        </div>
        <Button type="primary" danger icon={<SafetyOutlined />}>
          Security Scan
        </Button>
      </div>
      
      <Alert 
        message="Security Status: Elevated Risk" 
        description="There are 3 active security alerts that require attention." 
        type="warning" 
        showIcon 
        style={{ marginBottom: 16 }}
      />
      
      <Card>
        <Tabs defaultActiveKey="alerts">
          <TabPane tab="Security Alerts" key="alerts">
            <Timeline mode="left">
              {securityAlerts.map(alert => (
                <Timeline.Item 
                  key={alert.id}
                  color={alert.level === 'high' ? 'red' : alert.level === 'medium' ? 'orange' : 'blue'}
                  dot={alert.status === 'active' ? <WarningOutlined /> : <CheckCircleOutlined />}
                >
                  <Space direction="vertical" size={0}>
                    <Space>
                      <Badge 
                        status={alert.level === 'high' ? 'error' : alert.level === 'medium' ? 'warning' : 'processing'} 
                        text={`${alert.level.toUpperCase()} PRIORITY`} 
                      />
                      {alert.status === 'resolved' && <Badge status="success" text="RESOLVED" />}
                    </Space>
                    <div style={{ fontWeight: 'bold' }}>{alert.title}</div>
                    <div>
                      <ClockCircleOutlined style={{ marginRight: 8 }} />
                      {alert.time}
                    </div>
                  </Space>
                </Timeline.Item>
              ))}
            </Timeline>
          </TabPane>
          <TabPane tab="Threat Intelligence" key="intelligence">
            <p>Threat intelligence and security insights will be displayed here.</p>
          </TabPane>
          <TabPane tab="Compliance" key="compliance">
            <p>Compliance status and controls will be displayed here.</p>
          </TabPane>
          <TabPane tab="Vulnerabilities" key="vulnerabilities">
            <p>Vulnerability management and remediation will be displayed here.</p>
          </TabPane>
          <TabPane tab="Security Posture" key="posture">
            <p>Overall security posture and recommendations will be displayed here.</p>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default Security;