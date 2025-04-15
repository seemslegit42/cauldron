import React from 'react';
import { Typography, Card, Tabs, Form, Input, Switch, Button, Select, Divider } from 'antd';
import { SaveOutlined, UserOutlined, LockOutlined, ApiOutlined, BellOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

const Settings: React.FC = () => {
  return (
    <div>
      <Title level={2}>Settings</Title>
      <Paragraph>Configure your Cauldron™ sEOS environment.</Paragraph>
      
      <Card>
        <Tabs defaultActiveKey="general">
          <TabPane tab="General" key="general">
            <Form layout="vertical" style={{ maxWidth: 600 }}>
              <Form.Item label="System Name" name="systemName" initialValue="Cauldron™ sEOS">
                <Input placeholder="Enter system name" />
              </Form.Item>
              
              <Form.Item label="Default Language" name="language" initialValue="en-US">
                <Select>
                  <Option value="en-US">English (US)</Option>
                  <Option value="en-GB">English (UK)</Option>
                  <Option value="es">Spanish</Option>
                  <Option value="fr">French</Option>
                  <Option value="de">German</Option>
                </Select>
              </Form.Item>
              
              <Form.Item label="Time Zone" name="timezone" initialValue="UTC">
                <Select>
                  <Option value="UTC">UTC</Option>
                  <Option value="America/New_York">Eastern Time (ET)</Option>
                  <Option value="America/Chicago">Central Time (CT)</Option>
                  <Option value="America/Denver">Mountain Time (MT)</Option>
                  <Option value="America/Los_Angeles">Pacific Time (PT)</Option>
                  <Option value="Europe/London">London</Option>
                  <Option value="Europe/Paris">Paris</Option>
                  <Option value="Asia/Tokyo">Tokyo</Option>
                </Select>
              </Form.Item>
              
              <Divider />
              
              <Form.Item label="Enable Dark Mode" name="darkMode" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Form.Item label="Enable Analytics" name="analytics" valuePropName="checked" initialValue={true}>
                <Switch />
              </Form.Item>
              
              <Form.Item>
                <Button type="primary" icon={<SaveOutlined />}>Save Settings</Button>
              </Form.Item>
            </Form>
          </TabPane>
          
          <TabPane tab="User Management" key="users">
            <p>User management settings will be displayed here.</p>
          </TabPane>
          
          <TabPane tab="Security" key="security">
            <Form layout="vertical" style={{ maxWidth: 600 }}>
              <Form.Item label="Two-Factor Authentication" name="2fa" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Form.Item label="Session Timeout (minutes)" name="sessionTimeout" initialValue={30}>
                <Input type="number" min={5} max={120} />
              </Form.Item>
              
              <Form.Item label="Password Policy" name="passwordPolicy" initialValue="strong">
                <Select>
                  <Option value="basic">Basic (8+ characters)</Option>
                  <Option value="medium">Medium (8+ chars, mixed case)</Option>
                  <Option value="strong">Strong (8+ chars, mixed case, numbers, symbols)</Option>
                  <Option value="custom">Custom</Option>
                </Select>
              </Form.Item>
              
              <Form.Item>
                <Button type="primary" icon={<LockOutlined />}>Save Security Settings</Button>
              </Form.Item>
            </Form>
          </TabPane>
          
          <TabPane tab="Integrations" key="integrations">
            <p>API and external service integration settings will be displayed here.</p>
          </TabPane>
          
          <TabPane tab="Notifications" key="notifications">
            <Form layout="vertical" style={{ maxWidth: 600 }}>
              <Form.Item label="Email Notifications" name="emailNotifications" valuePropName="checked" initialValue={true}>
                <Switch />
              </Form.Item>
              
              <Form.Item label="In-App Notifications" name="inAppNotifications" valuePropName="checked" initialValue={true}>
                <Switch />
              </Form.Item>
              
              <Form.Item label="System Alerts" name="systemAlerts" valuePropName="checked" initialValue={true}>
                <Switch />
              </Form.Item>
              
              <Form.Item>
                <Button type="primary" icon={<BellOutlined />}>Save Notification Settings</Button>
              </Form.Item>
            </Form>
          </TabPane>
          
          <TabPane tab="About" key="about">
            <div style={{ maxWidth: 600 }}>
              <Title level={4}>Cauldron™ Sentient Enterprise Operating System</Title>
              <Paragraph>Version: 0.1.0 (Alpha)</Paragraph>
              <Paragraph>Build Date: April 15, 2025</Paragraph>
              <Paragraph>License: Apache 2.0</Paragraph>
              <Divider />
              <Paragraph>
                Cauldron™ is a next-generation Sentient Enterprise Operating System (sEOS) that empowers businesses with unprecedented levels of operational awareness, adaptive optimization, and intelligent automation.
              </Paragraph>
            </div>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default Settings;